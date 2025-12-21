from django.contrib import admin
from unfold.admin import ModelAdmin

from file.models import File


@admin.register(File)
class FileAdmin(ModelAdmin):
    list_display = ("id", "name", "file", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name",)
