from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin, TabularInline

from file.forms import FontModelForm
from file.models import File, Font, FontFamily


@admin.register(File)
class FileAdmin(ModelAdmin):
    list_display = ("id", "name", "file", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name",)


class FontInline(TabularInline):
    model = Font
    form = FontModelForm

    ordering_field = "position"  # type: ignore[assignment]
    hide_ordering_field = True

    extra = 1


@admin.register(FontFamily)
class FontFamilyAdmin(ModelAdmin, SimpleHistoryAdmin):
    list_display = ("name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name",)
    inlines = [FontInline]
