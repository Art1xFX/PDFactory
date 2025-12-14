from django.contrib import admin
from unfold.admin import ModelAdmin

from cert.models import Template


@admin.register(Template)
class TemplateAdmin(ModelAdmin):
    pass
