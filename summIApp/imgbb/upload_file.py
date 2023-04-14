import base64
from decouple import config
import requests
import logging
import traceback
from ..constants import imgbb_url


logger = logging.getLogger("django")


def imgbb_upload(file_contents):
    try:
        encoded_string = base64.b64encode(file_contents)

        params = {
            "key": config("IMGBB_API_KEY")
        }

        api_response = requests.post(imgbb_url, params=params, data={
            "image": encoded_string
        })

        return api_response.json()
    except Exception as e:
        logger.error(traceback.format_exc())
        return {
            "status": 500,
            "error": {
                "message": str(e)
            }
        }
