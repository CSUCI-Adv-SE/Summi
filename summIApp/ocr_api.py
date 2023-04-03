from google.cloud import vision
import io
import logging
import traceback
from google.oauth2 import service_account


logger = logging.getLogger("django")


def recognize_text_api(file_path):
    try:

        credentials = service_account.Credentials.from_service_account_file(
            "service-account.json")

        client = vision.ImageAnnotatorClient(credentials=credentials)

        with io.open(file_path, 'rb') as image_file1:
            content = image_file1.read()

        content_image = vision.Image(content=content)
        response = client.document_text_detection(image=content_image)
        document = response.full_text_annotation

        return document.text

    except Exception as e:
        logger.error(traceback.format_exc())
        return ""
