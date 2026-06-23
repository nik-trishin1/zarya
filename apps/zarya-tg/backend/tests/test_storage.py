from app.services.storage import normalize_cover_image_url


def test_normalize_cover_image_url_absolute_backend():
    url = "https://zarya-production-be.up.railway.app/uploads/abc123.jpg"
    assert normalize_cover_image_url(url) == "/uploads/abc123.jpg"


def test_normalize_cover_image_url_relative():
    assert normalize_cover_image_url("/uploads/abc123.jpg") == "/uploads/abc123.jpg"


def test_normalize_cover_image_url_none():
    assert normalize_cover_image_url(None) is None
