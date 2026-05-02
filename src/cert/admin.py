from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin

from cert.models import Template


@admin.register(Template)
class TemplateAdmin(ModelAdmin, SimpleHistoryAdmin):
    pass
