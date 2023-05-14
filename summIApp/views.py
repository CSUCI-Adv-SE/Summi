from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import logging
from .utils import *
from summI.settings import MEDIA_PATH, MEDIA_URL
from .constants import *
from PIL import Image
import re
from urllib.request import urlretrieve
import tempfile
from .sum_api import *
# from .summarizer import *
from .imgbb.upload_file import imgbb_upload
from .imgbb.download_file import imgbb_download_file
from rest_framework.authtoken.models import Token

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

            file_contents = uploaded_file.file.read()
            is_valid_file = validate_file(uploaded_file.file)

            if not is_valid_file:
                return JsonResponse({
                    "status": 300,
                    "message": "file format not supported",
                })

            file_name = strip_html(uploaded_file.name)

            if user.is_authenticated:
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

            summi_config_objs = SummIConfig.objects.all()

            if summi_config_objs.count() == 0:
                SummIConfig.objects.create()

            if SummIConfig.objects.last().SAVE_UPLOADED_IMAGES_LOCALLY:
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
            else:
                api_response = imgbb_upload(file_contents)

                if api_response["status"] == 200:
                    image_url = api_response["data"]["url"]
                    uploaded_file_object.file_path = image_url
                    uploaded_file_object.is_file_uploaded_on_imgbb = True
                    uploaded_file_object.save()

                    return JsonResponse({
                        "status": 200,
                        "message": "success",
                        "image_id": str(uploaded_file_object.uuid),
                        "image_url": image_url,
                    })
                else:
                    return JsonResponse({
                        "status": api_response["status_code"],
                        "message": api_response["error"]["message"],
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

            if request.user.is_authenticated:
                user_obj = request.user
            else:
                user_obj = User.objects.get(username="guest_user")

            user_uploaded_file_obj = UserUploadedFiles.objects.filter(
                uuid=image_uuid, user=user_obj).first()

            if not user_uploaded_file_obj:
                return JsonResponse({
                    "status": 301,
                    "message": "Invalid Image ID or Uploaded File object not found"
                })

            file_path = user_uploaded_file_obj.file_path

            if user_uploaded_file_obj.is_file_uploaded_on_imgbb:
                temp_path_dir = create_dir_in_temporary_media()
                temp_path = os.path.join(temp_path_dir, str(uuid4()) + ".png")
                imgbb_download_file(
                    user_uploaded_file_obj.file_path, temp_path)
                file_path = temp_path

            detected_text = recognize_text_wrapper(file_path)
            cleaned_detected_text = re.sub('[^A-Za-z0-9]+', ' ', detected_text)
            summary_text = summarize_text(cleaned_detected_text)
            #summary_text = summarizer(cleaned_detected_text)
            cleaned_summary_text = re.sub('[^A-Za-z0-9]+', ' ', summary_text)

            if request.user.is_authenticated:
                UserSummaryHistory.objects.create(
                    uploaded_file=user_uploaded_file_obj, summary_text=cleaned_summary_text)

            if user_uploaded_file_obj.is_file_uploaded_on_imgbb:
                remove_directory(temp_path_dir)

            if len(cleaned_detected_text):
                return JsonResponse({
                    "status": 200,
                    "message": cleaned_summary_text,
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


@csrf_exempt
@api_view(["POST"])
def registerView(request):
    if request.method == "POST":
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        confirm_password = request.POST.get('confirm_password', None)

        try:
            if not username:
                return JsonResponse({
                    "status": 300,
                    "message": "Missing Username"
                })
            if not email:
                return JsonResponse({
                    "status": 301,
                    "message": "Missing User Email"
                })
            if not password:
                return JsonResponse({
                    "status": 302,
                    "message": "Missing User Password"
                })
            if password != confirm_password:
                return JsonResponse({
                    "status": 303,
                    "message": "Passwords are mismatching",
                })

            if not is_email_valid(email):
                return JsonResponse({
                    "status": 310,
                    "message": "Please use valid email",
                })

            if not is_strong_password(password):
                return JsonResponse({
                    "status": 311,
                    "message": "Please use Strong Password",
                })

            objects_with_username = User.objects.filter(username=username)

            if objects_with_username:
                return JsonResponse({
                    "status": 304,
                    "message": "Username already taken. Please use different Username"
                })
            objects_with_email = User.objects.filter(email=email)

            if objects_with_email:
                return JsonResponse({
                    "status": 305,
                    "message": "Username with this email already present. Please sign in with your username"
                })

            user_obj = User.objects.create_user(
                username=username, email=email, password=password)

            token_obj = Token.objects.create(user=user_obj)

            return JsonResponse({
                "status": 200,
                "message": "User has been created!",
                "token": str(token_obj.key),
                "username": str(user_obj.username),
            })

        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse({
                "status": 500,
                "message": str(e),
            })


@csrf_exempt
@api_view(["POST"])
def loginView(request):
    if request.method == "POST":
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        try:
            if not email:
                return JsonResponse({
                    "status": 301,
                    "message": "Missing email"
                })

            if not password:
                return JsonResponse({
                    "status": 302,
                    "message": "Missing Password"
                })

            if not is_email_valid(email):
                return JsonResponse({
                    "status": 303,
                    "message": "Invalid Email Format"
                })

            user_objs = User.objects.filter(email=email)
            if not user_objs.count():
                return JsonResponse({
                    "status": 401,
                    "message": "Email not found"
                })

            if user_objs.count() > 1:
                return JsonResponse({
                    "status": 410,
                    "message": "Please report this message to the developer. Multiple accounts found with the same email"
                })

            user_obj = user_objs.first()

            if not user_obj.check_password(password):
                return JsonResponse({
                    "status": 400,
                    "message": "Bad credentials"
                })

            token_objs = Token.objects.filter(user=user_obj)

            if not token_objs.count():
                return JsonResponse({
                    "status": 401,
                    "message": "Token not found for the user. Please create a new account."
                })

            token_obj = token_objs.first()

            return JsonResponse({
                "status": 200,
                "message": "Login Success",
                "token": str(token_obj.key),
                "username": str(user_obj.username),
            })

        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse({
                "status": 500,
                "message": str(e),
            })


@csrf_exempt
@api_view(["POST"])
def ProcessImageURLView(request):
    if request.method == "POST":
        image_url = request.POST.get('image_url', None)

        if not image_url:
            return JsonResponse({"status": 400, "message": "No image URL provided"})

        # Download the image from the URL
        temp_image_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            urlretrieve(image_url, temp_image_file.name)
        except Exception as e:
            return JsonResponse({"status": 500, "message": "Failed to download image from the provided URL"})

        # Process the image file and return the result
        # You can call your existing functions for processing the image
        # For example, you can use your recognize_text_wrapper function
        detected_text = recognize_text_wrapper(temp_image_file.name)
        cleaned_detected_text = re.sub('[^A-Za-z0-9]+', ' ', detected_text)
        summary_text = summarize_text(cleaned_detected_text)
        cleaned_summary_text = re.sub('[^A-Za-z0-9]+', ' ', summary_text)

        if len(cleaned_summary_text):
            return JsonResponse({"status": 200, "message": cleaned_summary_text})

        return JsonResponse({"status": 302, "message": "Empty file or empty text detected"})


@csrf_exempt
@api_view(["POST"])
def GetUserSummaryHistory(request):
    if request.method == "POST":
        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    "status": 400,
                    "message": "Only allowed for logined users."
                })

            user_obj = request.user
            history = []

            history_objs = UserSummaryHistory.objects.filter(
                uploaded_file__user=user_obj)

            for history_obj in history_objs:
                image_path = history_obj.uploaded_file.file_path

                if not history_obj.uploaded_file.is_file_uploaded_on_imgbb:
                    _, file_name = os.path.split(image_path)
                    image_path = f"/media/{str(history_obj.uploaded_file.uuid)}/{file_name}"

                history.append({
                    "image_path": image_path,
                    "image_summary": history_obj.summary_text
                })

            return JsonResponse({
                "status": 200,
                "message": "success",
                "history": history,
            })
        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse({
                "status": 500,
                "message": str(e),
            })
