import logging
import uuid
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

from apps.common.services import ActivityEventType, record_activity_event

logger = logging.getLogger(__name__)


class ImageProcessingError(Exception):
    pass


def process_uploaded_image(
    uploaded_file: UploadedFile,
    *,
    actor=None,
) -> ContentFile:
    """
    Validate, re-encode, and return a safe image file with a random filename.
    Strips metadata by re-encoding through Pillow.
    """
    if uploaded_file.size > settings.IMAGE_MAX_BYTES:
        _record_rejection(actor, "file_too_large", uploaded_file.size)
        raise ImageProcessingError(
            f"Image must be {settings.IMAGE_MAX_BYTES // (1024 * 1024)} MB or smaller."
        )

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        _record_rejection(actor, "invalid_image", str(type(exc).__name__))
        raise ImageProcessingError("The uploaded file is not a valid image.") from exc

    if image.format not in settings.ALLOWED_IMAGE_FORMATS:
        _record_rejection(actor, "unsupported_format", image.format or "unknown")
        raise ImageProcessingError("Only JPEG, PNG, and WebP images are allowed.")

    width, height = image.size
    if width > settings.IMAGE_MAX_WIDTH or height > settings.IMAGE_MAX_HEIGHT:
        _record_rejection(actor, "dimensions_exceeded", f"{width}x{height}")
        raise ImageProcessingError(
            f"Image dimensions must not exceed "
            f"{settings.IMAGE_MAX_WIDTH}x{settings.IMAGE_MAX_HEIGHT} pixels."
        )

    if width * height > settings.IMAGE_MAX_PIXELS:
        _record_rejection(actor, "pixel_count_exceeded", width * height)
        raise ImageProcessingError("Image has too many pixels.")

    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        output_format = "PNG"
        save_kwargs: dict = {"optimize": True}
    else:
        output_format = "JPEG"
        if image.mode != "RGB":
            image = image.convert("RGB")
        save_kwargs = {"quality": 85, "optimize": True}

    buffer = BytesIO()
    image.save(buffer, format=output_format, **save_kwargs)
    extension = output_format.lower()
    if extension == "jpeg":
        extension = "jpg"
    filename = f"{uuid.uuid4().hex}.{extension}"
    return ContentFile(buffer.getvalue(), name=filename)


def _record_rejection(actor, reason: str, detail) -> None:
    record_activity_event(
        event_type=ActivityEventType.IMAGE_UPLOAD_REJECTED,
        actor=actor,
        metadata={"reason": reason, "detail": str(detail)},
    )
    logger.info("Image upload rejected: %s (%s)", reason, detail)


def save_processed_image(content_file: ContentFile, subdirectory: str) -> str:
    """Return the relative media path for a processed image."""
    target_dir = Path(settings.MEDIA_ROOT) / subdirectory
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / content_file.name
    with destination.open("wb") as handle:
        handle.write(content_file.read())
    return str(Path(subdirectory) / content_file.name)
