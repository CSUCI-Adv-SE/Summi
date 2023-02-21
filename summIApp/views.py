from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import UserUploadedFiles
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import logging
from .utils import *
from summI.settings import MEDIA_PATH
from .constants import *

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
                user=user, file_name=file_name)
            file_path = os.path.join(
                MEDIA_PATH, str(uploaded_file_object.uuid))

            if create_dirs(file_path):
                file_path = os.path.join(file_path, file_name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.file.read())

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
            })
        except Exception as e:
            logger.error(str(e))
            return JsonResponse({
                "status": 500,
                "message": str(e),
            })


@csrf_exempt
@api_view(["POST"])
def GetUserUploadedFileView(request):
    if request.method == "POST":
        try:
            image_uuid = request.POST.get('image_uuid', None)

            if image_uuid is None:
                return JsonResponse({
                    "status": 300,
                    "message": "Missing Image ID"
                })

            user_uploaded_file_obj = UserUploadedFiles.objects.filter(uuid=image_uuid).first()

            if not user_uploaded_file_obj:
                return JsonResponse({
                    "status": 301,
                    "message": "Invalid Image ID"
                })

            
        except Exception as e:
            logger.error(str(e))
