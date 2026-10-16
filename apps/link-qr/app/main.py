from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, Form, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import extract_admin_token, require_admin, tokens_match
from app.config import Settings, get_settings
from app.database import Base, engine, get_db
from app.models import Click, Link
from app.qr_util import generate_qr_png
from app.slugs import generate_slug, is_valid_slug
from app.utm import build_redirect_url, defaults_to_json, parse_default_utm_json

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except Exception as exc:
            last_error = exc
            logger.warning("Database not ready (attempt %s/5): %s", attempt, exc)
            await asyncio.sleep(2)
    else:
        raise RuntimeError("Could not connect to database") from last_error
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="link-qr", version="1.0.0", lifespan=lifespan)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    async def admin_home(
        request: Request,
        settings: Annotated[Settings, Depends(get_settings)],
        x_admin_token: Annotated[str | None, Header()] = None,
    ):
        token = extract_admin_token(request, settings, x_admin_token=x_admin_token)
        if token is None:
            return templates.TemplateResponse(
                request,
                "login.html",
                {"title": "Вход"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        return templates.TemplateResponse(
            request,
            "index.html",
            {"title": "Новая ссылка", "public_base_url": settings.public_base_url.rstrip("/")},
        )

    @app.post("/login", response_class=HTMLResponse)
    async def login(
        request: Request,
        settings: Annotated[Settings, Depends(get_settings)],
        admin_token: Annotated[str, Form()] = "",
    ):
        if not tokens_match(admin_token, settings.admin_token):
            return templates.TemplateResponse(
                request,
                "login.html",
                {"title": "Вход", "error": "Неверный токен"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key=settings.cookie_name,
            value=admin_token,
            httponly=True,
            samesite="lax",
            max_age=settings.cookie_max_age_seconds,
        )
        return response

    @app.post("/links", response_class=HTMLResponse)
    async def create_link(
        request: Request,
        db: Annotated[AsyncSession, Depends(get_db)],
        settings: Annotated[Settings, Depends(get_settings)],
        destination_url: Annotated[str, Form()] = "",
        slug: Annotated[str, Form()] = "",
        utm_source: Annotated[str, Form()] = "",
        utm_medium: Annotated[str, Form()] = "",
        utm_campaign: Annotated[str, Form()] = "",
        utm_content: Annotated[str, Form()] = "",
        utm_term: Annotated[str, Form()] = "",
        admin_token: Annotated[str, Form()] = "",
        x_admin_token: Annotated[str | None, Header()] = None,
    ):
        token = extract_admin_token(
            request,
            settings,
            x_admin_token=x_admin_token,
            form_token=admin_token or None,
        )
        if token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        destination_url = destination_url.strip()
        if not _is_valid_http_url(destination_url):
            return templates.TemplateResponse(
                request,
                "index.html",
                {
                    "title": "Новая ссылка",
                    "error": "Укажите корректный http(s) URL",
                    "public_base_url": settings.public_base_url.rstrip("/"),
                    "form": _form_state(
                        destination_url,
                        slug,
                        utm_source,
                        utm_medium,
                        utm_campaign,
                        utm_content,
                        utm_term,
                    ),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        custom_slug = slug.strip()
        if custom_slug:
            if not is_valid_slug(custom_slug):
                return templates.TemplateResponse(
                    request,
                    "index.html",
                    {
                        "title": "Новая ссылка",
                        "error": "Slug: буквы, цифры, -, _; 1–64 символа",
                        "public_base_url": settings.public_base_url.rstrip("/"),
                        "form": _form_state(
                            destination_url,
                            custom_slug,
                            utm_source,
                            utm_medium,
                            utm_campaign,
                            utm_content,
                            utm_term,
                        ),
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            final_slug = custom_slug
        else:
            final_slug = await _unique_slug(db)

        default_utm = {
            k: v.strip()
            for k, v in {
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "utm_content": utm_content,
                "utm_term": utm_term,
            }.items()
            if v and v.strip()
        }
        link = Link(
            slug=final_slug,
            destination_url=destination_url,
            default_utm_json=defaults_to_json(default_utm),
        )
        db.add(link)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return templates.TemplateResponse(
                request,
                "index.html",
                {
                    "title": "Новая ссылка",
                    "error": "Такой slug уже занят",
                    "public_base_url": settings.public_base_url.rstrip("/"),
                    "form": _form_state(
                        destination_url,
                        final_slug,
                        utm_source,
                        utm_medium,
                        utm_campaign,
                        utm_content,
                        utm_term,
                    ),
                },
                status_code=status.HTTP_409_CONFLICT,
            )
        await db.refresh(link)

        base = settings.public_base_url.rstrip("/")
        short_url = f"{base}/r/{link.slug}"
        qr_url = f"{base}/qr/{link.slug}.png"
        stats_url = f"{base}/stats/{link.slug}"

        response = templates.TemplateResponse(
            request,
            "created.html",
            {
                "title": "Ссылка создана",
                "link": link,
                "short_url": short_url,
                "qr_url": qr_url,
                "stats_url": stats_url,
            },
        )
        response.set_cookie(
            key=settings.cookie_name,
            value=token,
            httponly=True,
            samesite="lax",
            max_age=settings.cookie_max_age_seconds,
        )
        return response

    @app.get("/r/{slug}")
    async def redirect_slug(
        slug: str,
        request: Request,
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        result = await db.execute(select(Link).where(Link.slug == slug))
        link = result.scalar_one_or_none()
        if link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        flat_params = {k: v for k, v in request.query_params.items()}
        default_utm = parse_default_utm_json(link.default_utm_json)
        redirect_url, utm_values = build_redirect_url(link.destination_url, flat_params, default_utm)

        click = Click(
            link_id=link.id,
            utm_source=utm_values.get("utm_source"),
            utm_medium=utm_values.get("utm_medium"),
            utm_campaign=utm_values.get("utm_campaign"),
            utm_content=utm_values.get("utm_content"),
            utm_term=utm_values.get("utm_term"),
            referer=request.headers.get("referer"),
            user_agent=request.headers.get("user-agent"),
        )
        db.add(click)
        await db.commit()

        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

    @app.get("/qr/{slug}.png")
    async def qr_png(
        slug: str,
        request: Request,
        db: Annotated[AsyncSession, Depends(get_db)],
        settings: Annotated[Settings, Depends(get_settings)],
    ):
        result = await db.execute(select(Link).where(Link.slug == slug))
        link = result.scalar_one_or_none()
        if link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        base = settings.public_base_url.rstrip("/")
        # Prefer request host when PUBLIC_BASE_URL is unset/default-ish for local use.
        short_url = f"{base}/r/{link.slug}"
        png = generate_qr_png(short_url)
        return Response(content=png, media_type="image/png")

    @app.get("/stats/{slug}", response_class=HTMLResponse)
    async def stats(
        slug: str,
        request: Request,
        db: Annotated[AsyncSession, Depends(get_db)],
        settings: Annotated[Settings, Depends(get_settings)],
        _: Annotated[str, Depends(require_admin)],
    ):
        result = await db.execute(select(Link).where(Link.slug == slug))
        link = result.scalar_one_or_none()
        if link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        total = await db.scalar(select(func.count()).select_from(Click).where(Click.link_id == link.id))
        breakdowns = {}
        for field_name, column in (
            ("utm_source", Click.utm_source),
            ("utm_medium", Click.utm_medium),
            ("utm_campaign", Click.utm_campaign),
            ("utm_content", Click.utm_content),
            ("utm_term", Click.utm_term),
        ):
            rows = await db.execute(
                select(column, func.count())
                .where(Click.link_id == link.id)
                .group_by(column)
                .order_by(func.count().desc())
            )
            breakdowns[field_name] = [
                {"value": value if value is not None else "(пусто)", "count": count}
                for value, count in rows.all()
            ]

        base = settings.public_base_url.rstrip("/")
        return templates.TemplateResponse(
            request,
            "stats.html",
            {
                "title": f"Статистика · {link.slug}",
                "link": link,
                "short_url": f"{base}/r/{link.slug}",
                "qr_url": f"{base}/qr/{link.slug}.png",
                "total": total or 0,
                "breakdowns": breakdowns,
                "default_utm": parse_default_utm_json(link.default_utm_json),
            },
        )

    return app


def _is_valid_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _form_state(
    destination_url: str,
    slug: str,
    utm_source: str,
    utm_medium: str,
    utm_campaign: str,
    utm_content: str,
    utm_term: str,
) -> dict[str, str]:
    return {
        "destination_url": destination_url,
        "slug": slug,
        "utm_source": utm_source,
        "utm_medium": utm_medium,
        "utm_campaign": utm_campaign,
        "utm_content": utm_content,
        "utm_term": utm_term,
    }


async def _unique_slug(db: AsyncSession, attempts: int = 8) -> str:
    for _ in range(attempts):
        candidate = generate_slug()
        exists = await db.scalar(select(Link.id).where(Link.slug == candidate))
        if exists is None:
            return candidate
    raise HTTPException(status_code=500, detail="Could not generate unique slug")


app = create_app()
