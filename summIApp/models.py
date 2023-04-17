from django.db import models
import uuid
from django.contrib.auth.models import User


# Create your models here.
class UserUploadedFiles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Who uploaded the object")
    file_name = models.CharField(max_length=255, help_text="Name of the file")
    file_path = models.CharField(max_length=1000, null=True, help_text="Path of the file that user has uploaded")
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique ID for every uploaded file")
    is_public_file = models.BooleanField(default=False, help_text="is this file public")
    is_file_uploaded_on_imgbb = models.BooleanField(default=False, help_text="is this file uploaded in the imgbb server")
    uploaded_datetime = models.DateTimeField(auto_now_add=True, help_text="When did the user uploaded the file")

