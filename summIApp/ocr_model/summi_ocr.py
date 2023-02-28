# import easyocr
import PIL
import os
import logging


logger = logging.getLogger("django")

def recognize_text(uploaded_image):
    text = ""
    try:
        # Load the image
        image = PIL.Image.open(uploaded_image)

        #prevent some path errors for other image formats
        image_path = os.path.join(image.filename)

        # Initialize EasyOCR reader
        #reader = easyocr.Reader(['en'])

        # Use the reader to detect the text in the photo
        result = reader.readtext(image_path)

        # Extract the recognized text from the result and return it as a text (str)
        text = ' '.join([r[1] for r in result])

        return text.strip()
    except Exception as e:
        logging.error(str(e))
        return text
