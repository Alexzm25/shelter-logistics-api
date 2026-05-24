from cloudinary import config as cloudinary_config
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.utils import cloudinary_url
from fastapi import HTTPException, UploadFile, status

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


def upload_image_to_cloudinary(upload_file: UploadFile, folder: str) -> str:
    upload_file.file.seek(0)
    result = cloudinary_upload(
        upload_file.file,
        folder=folder,
        resource_type="image",
    )

    secure_url = result.get("secure_url") or result.get("url")
    if not secure_url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible guardar la imagen en Cloudinary.",
        )

    return secure_url
