from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import logging
from .utils import *
from summI.settings import MEDIA_PATH, MEDIA_URL
from .constants import *
from PIL import Image
import re
from .sum_api import *
from .imgbb.upload_file import imgbb_upload
from .imgbb.download_file import imgbb_download_file
from django.shortcuts import redirect, render
from django.core import serializers
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

            if SAVE_UPLOADED_IMAGES_LOCALLY:
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

            user_uploaded_file_obj = UserUploadedFiles.objects.filter(
                uuid=image_uuid).first()

            if not user_uploaded_file_obj:
                return JsonResponse({
                    "status": 301,
                    "message": "Invalid Image ID or Uploaded File object not found"
                })

            file_path = user_uploaded_file_obj.file_path

            if user_uploaded_file_obj.is_file_uploaded_on_imgbb:
                temp_path = create_dir_in_temporary_media()
                temp_path = os.path.join(temp_path, str(uuid4()) + ".png")
                imgbb_download_file(
                    user_uploaded_file_obj.file_path, temp_path)
                file_path = temp_path

            detected_text = recognize_text_wrapper(file_path)
            cleaned_detected_text = re.sub('[^A-Za-z0-9]+', ' ', detected_text)
            summary_text = summarize_text(cleaned_detected_text)
            cleaned_summary_text = re.sub('[^A-Za-z0-9]+', ' ', summary_text)

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
    print(request.data)
    username = request.data['username']
    email = request.data['email']
    password = request.data['password']
    print(email, password)
    try:
        if(username is None):
            return JsonResponse({
                    "status": 300,
                    "message": "Missing Username"
                })
        elif(email is None):
            return JsonResponse({
                    "status": 300,
                    "message": "Missing User Email"
                })
        elif(password is None):
            return JsonResponse({
                    "status": 300,
                    "message": "Missing User Password"
                })
        else:
            token = Token.objects.create(username)
            print(token.key)
            User.objects.create(username=username, email=email, password=password, token=token)
            return JsonResponse({
                'status': 200, 
                'message': token
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
    print(request.data)
    email = request.data['email']
    password = request.data['password']
    print(email, password)
    user = authenticate(username=email, password=password)
    print('user//////', user)
    if user and user.is_active:
        try:
            if(email is None):
                return JsonResponse({
                    "status": 300,
                    "message": "Missing User Email"
                    })
            elif(password is None):
                return JsonResponse({
                    "status": 300,
                    "message": "Missing User Password"
                    })
            else:
                login(request._request, user)
                return JsonResponse({
                    "status": 200,
                    "message": user
                })
        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse({
                "status": 500,
                "message": str(e),
            })
    else:
        return JsonResponse({
            "status": 500,
            "message": "Error",
        })
    
@csrf_exempt
@api_view(["GET"])
def currentUserView(request):
    if request.user.is_authenticated:
        try:
            data = serializers.serialize('json', [request.user], fields=['email'])
            return HttpResponse(data) 
        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse({
                "status": 500,
                "message": str(e),
            })
    else: 
        return JsonResponse({'user': None})

@csrf_exempt
@api_view(["POST"])
def logoutView(request):
    try:
        logout(request)
        return JsonResponse({
            'status': 200, 
            'message': 'true',
        })
    except Exception as e:
        logger.error(traceback.format_exc())
        return JsonResponse({
            "status": 500,
            "message": str(e),
        })