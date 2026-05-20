from cloudinary import config as cloudinary_config
from cloudinary.utils import cloudinary_url

from src.core.settings import settings


def configure_cloudinary() -> dict:
    return cloudinary_config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=settings.cloudinary_secure,
    )


def build_cloudinary_url(public_id: str | None) -> str | None:
    if not public_id:
        return None

    trimmed = public_id.strip()
    if trimmed.lower().startswith("http://") or trimmed.lower().startswith("https://"):
        return trimmed

    normalized = trimmed.lstrip("/")
    url, _ = cloudinary_url(normalized, secure=settings.cloudinary_secure)
    return url
