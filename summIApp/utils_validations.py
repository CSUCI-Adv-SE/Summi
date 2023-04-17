from PIL import Image
import logging
from pathvalidate import sanitize_filename
import traceback


logger = logging.getLogger("django")


def validate_file(file):
    try:
        with Image.open(file) as img:
            return img.format.upper() in ["PNG", "JPG", "JPEG", "WEBP", "TIFF"]
    except Exception as e:
        logger.error(traceback.format_exc())
        return False


def strip_html(name):
    sanitized_filename = ""
    try:
        sanitized_filename = sanitize_filename(name)
        return sanitized_filename
    except Exception as e:
        logger.error(traceback.format_exc())
    return sanitized_filename
