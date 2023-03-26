from PIL import Image
import logging
from pathvalidate import sanitize_filename
import traceback
from io import BytesIO

logger = logging.getLogger("django")

def validate_file(file):
    try:
        with Image.open(file) as img:
            img_format = img.format.upper()
            return img_format in {"PNG", "JPG", "JPEG", "WEBP", "TIFF"}
    except Exception as e:
        logger.error("Error validating file:", exc_info=True)
        return False

def strip_html(name):
    sanitized_filename = ""
    try:
        sanitized_filename = sanitize_filename(name, replacement_text="")
        return sanitized_filename
    except Exception as e:
        logger.error("Error sanitizing filename:", exc_info=True)
    return sanitized_filename