import os
import logging
from .utils_validations import *
from uuid import uuid4
from .constants import *
import traceback
from summI.settings import BASE_DIR
from .ocr_model.summi_ocr import recognize_text
from .ocr_api import recognize_text_api

logger = logging.getLogger("django")


def create_dirs(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except Exception as e:
        logger.error(traceback.format_exc())
        return False


def convert_to_png(uploaded_file, file_path):
    try:
        user_file = Image.open(uploaded_file.file)

        if create_dirs(file_path):
            new_file_name = "_".join(
                uploaded_file.name.split(".")[:-1]) + ".png"
            file_path = os.path.join(file_path, new_file_name)
            user_file.save(file_path, format="png", lossless=True)
            return file_path
    except Exception as e:
        logger.error(traceback.format_exc())
    return None


def recognize_text_wrapper(file_path):
    try:
        if USE_OCR_APIs:
            return recognize_text_api(file_path)
        else:
            return recognize_text(file_path)
    except Exception as e:
        logger.error(traceback.format_exc())
        return