from uuid import UUID

from django.contrib import admin
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Concat
from django.http import FileResponse, HttpRequest
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportMixin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.decorators import action, display

from course.forms import CertificateImportForm, CodeConfirmImportForm
from course.models import Certificate, CertificateRenderTask, Course, Intake
from course.resources import CertificateResource
from course.utils import CertificateFileNameBuilder


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
        "display_status",
        "intake__course",
        "intake__start_date",
        "intake__end_date",
        "updated_at",
    )
    list_filter = (
        ["intake__course", AutocompleteSelectFilter],
        ["intake", AutocompleteSelectFilter],
    )
    list_filter_submit = True
    search_fields = ("first_name", "last_name", "intake__course__title")
    actions_row = ["download_row_action"]

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
        latest_task_status = Subquery(
            CertificateRenderTask.objects.filter(certificate=OuterRef("pk"))
            .order_by("-updated_at")
            .values("status")[:1]
        )
        return (
            super()
            .get_queryset(request)
            .select_related("intake__course")
            .annotate(latest_task_status=latest_task_status)
        )

    @admin.display(
        description="Full name",
        ordering=Concat("first_name", Value(" "), "last_name"),
    )
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @display(
        description="Status",
        label={
            CertificateRenderTask.Status.PENDING.label: "warning",
            CertificateRenderTask.Status.IN_PROGRESS.label: "info",
            CertificateRenderTask.Status.DONE.label: "success",
            CertificateRenderTask.Status.FAILED.label: "danger",
            _("Unknown"): "secondary",
        },
    )
    def display_status(self, obj):
        if not obj.latest_task_status:
            return _("Unknown")

        return CertificateRenderTask.Status(obj.latest_task_status).label

    @admin.display(description="Course", ordering="intake__course__title")
    def intake__course(self, obj):
        return obj.intake.course

    @admin.display(description="Start date", ordering="intake__start_date")
    def intake__start_date(self, obj):
        return obj.intake.start_date

    @admin.display(description="End date", ordering="intake__end_date")
    def intake__end_date(self, obj):
        return obj.intake.end_date

    @action(
        description=_("Download"),
        icon="download",
        url_path="download",
    )
    def download_row_action(self, request: HttpRequest, object_id: UUID):
        certificate = Certificate.objects.get(id=object_id)
        file = certificate.file

        return FileResponse(
            file,
            as_attachment=True,
            filename=(
                CertificateFileNameBuilder(certificate)
                .add_first_name()
                .add_separator()
                .add_last_name()
                .add_separator()
                .add_course_title()
                .add_separator()
                .add_intake_start_date()
                .add_separator()
                .add_intake_end_date()
                .build()
            ),
        )


@admin.register(CertificateRenderTask)
class CertificateRenderTaskAdmin(ModelAdmin):
    list_display = ("id", "certificate", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("certificate__first_name", "certificate__last_name", "certificate__intake__course__title")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("certificate__intake__course")
