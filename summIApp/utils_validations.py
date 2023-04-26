from PIL import Image
import logging
from pathvalidate import sanitize_filename
import traceback
import re

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


def is_email_valid(email):
    try:
        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return re.fullmatch(regex, email)
    except Exception:
        logger.error(traceback.format_exc())
        return False


def is_strong_password(password):
    try:
        regex = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,}$"
        return re.match(regex, password)
    except Exception:
        logger.error(traceback.format_exc())
        return False
