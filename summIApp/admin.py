from django.contrib import admin
from .models import *

# Register your models here.


class UserUploadedFilesAdmin(admin.ModelAdmin):
    ordering = ["-uploaded_datetime"]
    list_display = ["uuid", "user", "uploaded_datetime", "file_path"]


admin.site.register(UserUploadedFiles, UserUploadedFilesAdmin)


class UserSummaryHistoryAdmin(admin.ModelAdmin):
    list_display = ["get_user", "uploaded_file", ]

    def get_user(self, obj):
        return obj.uploaded_file.user


admin.site.register(UserSummaryHistory, UserSummaryHistoryAdmin)
