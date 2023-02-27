from PIL import Image
import logging
from pathvalidate import sanitize_filename
from uuid import UUID

logger = logging.getLogger("django")
def validate_file(file):
    try:
        img = Image.open(file)

        return img.format.upper() in ["PNG", "JPG", "JPEG", "WEBP", "TIFF"]
    except Exception as e:
        logger.error(str(e))
        return False

def strip_html(name):
    sanitized_filename = ""
    try:
        sanitized_filename = sanitize_filename(name)
        return sanitized_filename
    except Exception as e:
        logger.error(str(e))
    return sanitized_filename



def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except Exception as e:
        logger.error(str(e))
        return False

    return str(uuid_obj) == uuid_to_test
    