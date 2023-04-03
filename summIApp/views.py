from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import UserUploadedFiles
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import logging
from .utils import *
from summI.settings import MEDIA_PATH, MEDIA_URL
from .constants import *
from PIL import Image
import re


# logging
logger = logging.getLogger("django")


# Create your views here.
@csrf_exempt
@api_view(["POST"])
def UserUploadedFilesView(request):
    if request.method == "POST":
        try:
            user = request.user
            uploaded_file = request.FILES['uploaded_file']
            is_valid_file = False
            is_public_file = True

            if uploaded_file.size > max_file_size:
                return JsonResponse({
                    "status": 401,
                    "message": f"file size cannot be higher than {max_file_size//1024**2} MB",
                })

            is_valid_file = validate_file(uploaded_file.file)

            if not is_valid_file:
                return JsonResponse({
                    "status": 300,
                    "message": "file format not supported",
                })

            file_name = strip_html(uploaded_file.name)

            if user.is_authenticated:
                user = User.objects.filter(user=user).first()
                is_public_file = False
            else:
                user = User.objects.filter(username="guest_user")
                if not len(user):
                    user = User.objects.create(
                        username="guest_user", is_superuser=False, is_staff=False)
                    user.set_password("guest_user@123!")
                    user.save()
                else:
                    user = user.first()

            uploaded_file_object = UserUploadedFiles.objects.create(
                user=user, file_name=file_name, is_public_file=is_public_file)
            file_path = os.path.join(
                MEDIA_PATH, str(uploaded_file_object.uuid))

            with Image.open(uploaded_file.file) as f:
                image_format = f.format.upper()

            if image_format in supported_converters:
                converted_image_file_path = convert_to_png(
                    uploaded_file, file_path)

                if converted_image_file_path is None:
                    return JsonResponse({
                        "status": 302,
                        "message": "Problem with the converter",
                    })

                uploaded_file_object.file_name = os.path.split(
                    converted_image_file_path)[1]
                file_path = converted_image_file_path

            if create_dirs(file_path):
                if image_format not in supported_converters:
                    file_path = os.path.join(file_path, file_name)
                    try:
                        user_image = Image.open(uploaded_file.file)
                        user_image.save(file_path)
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        return JsonResponse({
                            "status": 301,
                            "message": "Cannot able to save the file to the disk",
                        })

                uploaded_file_object.file_path = file_path
                uploaded_file_object.save()
            else:
                return JsonResponse({
                    "status": 400,
                    "message": "cannot able to create a dir in media"
                })

            return JsonResponse({
                "status": 200,
                "message": "success",
                "image_id": str(uploaded_file_object.uuid),
                "image_url": MEDIA_URL + str(uploaded_file_object.uuid) + "/" + str(uploaded_file_object.file_name),
            })
        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse({
                "status": 500,
                "message": str(e),
            })


# @csrf_exempt
# @api_view(["POST"])
# def GetUserUploadedFileView(request):
#     if request.method == "POST":
#         try:
#             image_uuid = request.POST.get('image_uuid', None)

#             if image_uuid is None:
#                 return JsonResponse({
#                     "status": 300,
#                     "message": "Missing Image ID"
#                 })

#             user_uploaded_file_obj = UserUploadedFiles.objects.filter(uuid=image_uuid).first()

#             if not user_uploaded_file_obj:
#                 return JsonResponse({
#                     "status": 301,
#                     "message": "Invalid Image ID"
#                 })

#             return JsonResponse({
#                 "status": 200,
#                 "message": "success",
#                 "image_url": MEDIA_URL + str(user_uploaded_file_obj.uuid) + "/" + str(user_uploaded_file_obj.file_name),
#             })


#         except Exception as e:
#             logger.error(traceback.format_exc())


@csrf_exempt
@api_view(["POST"])
def GetSummarisedTextView(request):
    if request.method == "POST":
        try:
            image_uuid = request.POST.get('image_uuid', None)

            if image_uuid is None:
                return JsonResponse({
                    "status": 300,
                    "message": "Missing Image ID"
                })

            user_uploaded_file_obj = UserUploadedFiles.objects.filter(
                uuid=image_uuid).first()

            if not user_uploaded_file_obj:
                return JsonResponse({
                    "status": 301,
                    "message": "Invalid Image ID or Uploaded File object not found"
                })

            detected_text = recognize_text_wrapper(user_uploaded_file_obj.file_path)
            cleaned_detected_text = re.sub('[^A-Za-z0-9]+', ' ', detected_text)

            if len(cleaned_detected_text):
                return JsonResponse({
                    "status": 200,
                    "message": cleaned_detected_text,
                })

            return JsonResponse({
                "status": 302,
                "message": "Empty file or empty text detected"
            })

        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse({
                "status": 500,
                "message": str(e),
            })
