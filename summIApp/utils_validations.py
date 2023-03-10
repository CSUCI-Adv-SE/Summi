from PIL import Image
import logging
from pathvalidate import sanitize_filename
# regex library added
import re
logger = logging.getLogger("django")


def validate_file(file):
    try:
        # Opening and closing files manually can cause errors if you forget to close the file.
        # Using context managers (with statements) ensures that the file is automatically closed after the block of code finishes executing.
        img = Image.open(file)
        with Image.open(file) as img:
            return img.format.upper() in ["PNG", "JPG", "JPEG", "WEBP", "TIFF"]
    except Exception as e:
        logger.error(str(e))
        return False


def strip_html(name, max_length=100):
    try:
        # Remove leading and trailing whitespace
        sanitized_filename = name.strip()

        # Replace non-alphanumeric characters with underscores
        sanitized_filename = re.sub(r"[^\w\s\-_]", "_", sanitized_filename)

        # Limit the length of the filename
        sanitized_filename = sanitized_filename[:max_length]

        # Remove any remaining whitespace
        sanitized_filename = sanitized_filename.replace(" ", "_")

        return sanitized_filename
    except Exception as e:
        logger.error(str(e))
        return ""
