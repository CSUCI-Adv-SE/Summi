from PIL import Image
import logging
from pathvalidate import sanitize_filename
import traceback
from io import BytesIO

logger = logging.getLogger("django")

# Restrict file formats to a limited set
ALLOWED_FORMATS = ["PNG", "JPG", "JPEG", "WEBP", "TIFF"]


def validate_file(file):
    try:
        # Use BytesIO to prevent potential issues with file handling
        with BytesIO(file.read()) as buffered_file:
            img = Image.open(buffered_file)

            # Ensure the file format is in the allowed formats list
            return img.format.upper() in ALLOWED_FORMATS
    except Exception as e:
        logger.error(traceback.format_exc())
        return False


def strip_html(name):
    sanitized_filename = ""
    try:
        sanitized_filename = sanitize_filename(name, replacement_text="-")

        # Limit the length of filenames to prevent potential issues
        max_filename_length = 255
        return sanitized_filename[:max_filename_length]
    except Exception as e:
        logger.error(traceback.format_exc())
    return sanitized_filename
