from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

UTM_KEYS = ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")


def parse_default_utm_json(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    result: dict[str, str] = {}
    for key in UTM_KEYS:
        value = data.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            result[key] = text
    return result


def defaults_to_json(defaults: dict[str, str]) -> str | None:
    cleaned = {k: v for k, v in defaults.items() if k in UTM_KEYS and v}
    if not cleaned:
        return None
    return json.dumps(cleaned, ensure_ascii=False, sort_keys=True)


def merge_utm(
    request_params: dict[str, str],
    default_utm: dict[str, str],
) -> dict[str, str | None]:
    """Request query wins; fill missing UTM keys from defaults."""
    merged: dict[str, str | None] = {}
    for key in UTM_KEYS:
        req_val = (request_params.get(key) or "").strip()
        if req_val:
            merged[key] = req_val
        else:
            default_val = (default_utm.get(key) or "").strip()
            merged[key] = default_val or None
    return merged


def build_redirect_url(
    destination_url: str,
    request_params: dict[str, Any],
    default_utm: dict[str, str],
) -> tuple[str, dict[str, str | None]]:
    """
    Build final destination URL.

    Start from destination query, fill missing utm_* from defaults,
    then overlay request query (request wins). Persist UTM values from the
    final merged set.
    """
    parsed = urlparse(destination_url)
    dest_params = dict(parse_qsl(parsed.query, keep_blank_values=True))

    req_flat = {str(k): str(v) for k, v in request_params.items() if v is not None}

    final_params = dict(dest_params)
    for key in UTM_KEYS:
        if key not in final_params or not str(final_params.get(key) or "").strip():
            if key in default_utm and default_utm[key]:
                final_params[key] = default_utm[key]

    final_params.update(req_flat)

    # Click analytics: request query wins, then defaults — not destination baked-ins.
    utm_values = merge_utm(req_flat, default_utm)

    query = urlencode([(k, v) for k, v in final_params.items() if v is not None and str(v) != ""])
    redirect = urlunparse(parsed._replace(query=query))
    return redirect, utm_values
