from django.contrib import admin
from django.db.models import Value
from django.db.models.functions import Concat
from import_export.admin import ImportMixin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter

from course.forms import CertificateImportForm, CodeConfirmImportForm
from course.models import Certificate, Course, Intake
from course.resources import CertificateResource


@admin.register(Course)
class CourseAdmin(ModelAdmin, SimpleHistoryAdmin):
    search_fields = ("title",)


@admin.register(Intake)
class IntakeAdmin(ModelAdmin, SimpleHistoryAdmin):
    search_fields = ("course__title",)


@admin.register(Certificate)
class CertificateAdmin(ModelAdmin, ImportMixin, SimpleHistoryAdmin):
    readonly_fields = ("file", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "intake",
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Certificate",
            {"fields": ("file",)},
        ),
        (
            "Important dates",
            {"fields": ("created_at", "updated_at")},
        ),
    )
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
    search_fields = ("first_name", "last_name", "intake__course__title")

    resource_classes = [CertificateResource]
    import_form_class = CertificateImportForm
    confirm_form_class = CodeConfirmImportForm

    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)
        if import_form and import_form.is_valid():
            initial["intake"] = import_form.cleaned_data["intake"]
        return initial

    def get_import_data_kwargs(self, **kwargs):
        form = kwargs.get("form")

        if form and form.is_valid():
            kwargs.update(
                {
                    "intake": form.cleaned_data["intake"],
                }
            )
        return kwargs

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
