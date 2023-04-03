import pytesseract as tess
from PIL import Image
import logging
import os
from summI.settings import DEBUG


def recognize_text(uploaded_image):
    text = ""
    try:
        img = Image.open(uploaded_image)
        img_path = os.path.join(img.filename)
        if DEBUG:
            tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

        text = tess.image_to_string(img_path)

        return text.strip()
    except Exception as e:
        logging.error(str(e))
        return text
