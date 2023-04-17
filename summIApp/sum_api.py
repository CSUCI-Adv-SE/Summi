import logging
import traceback
import openai
from decouple import config

logger = logging.getLogger("django")


def summarize_text(text):
    try:
        openai.api_key = config("OPENAI_API_KEY")
        response = openai.Completion.create(
            model="text-ada-001",
            prompt=f'{text}\n\nTl;dr',
            temperature=0.7,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=1
        )
        return response['choices'][0].text.strip()

    except Exception as e:
        logger.error(traceback.format_exc())
        return ""
