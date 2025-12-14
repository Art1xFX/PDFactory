from django.contrib import admin
from django.db.models import Value
from django.db.models.functions import Concat
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter

from course.models import Certificate, Course, Intake


@admin.register(Course)
class CourseAdmin(ModelAdmin, SimpleHistoryAdmin):
    search_fields = ("title",)


@admin.register(Intake)
class IntakeAdmin(ModelAdmin, SimpleHistoryAdmin):
    search_fields = ("course__title",)


@admin.register(Certificate)
class CertificateAdmin(ModelAdmin, SimpleHistoryAdmin):
    list_display = (
        "id",
        "full_name",
        "intake__course",
        "intake__start_date",
        "intake__end_date",
        "created_at",
        "updated_at",
    )
    list_filter = (
        ["intake__course", AutocompleteSelectFilter],
        ["intake", AutocompleteSelectFilter],
    )
    list_filter_submit = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("intake__course")

    @admin.display(
        description="Full name",
        ordering=Concat("first_name", Value(" "), "last_name"),
    )
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="Course", ordering="intake__course__title")
    def intake__course(self, obj):
        return obj.intake.course

    @admin.display(description="Start date", ordering="intake__start_date")
    def intake__start_date(self, obj):
        return obj.intake.start_date

    @admin.display(description="End date", ordering="intake__end_date")
    def intake__end_date(self, obj):
        return obj.intake.end_date
