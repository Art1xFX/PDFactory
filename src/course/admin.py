from tempfile import NamedTemporaryFile
from uuid import UUID
from zipfile import ZIP_DEFLATED, ZipFile

from django.contrib import admin, messages
from django.db.models import Count, OuterRef, Subquery, Value
from django.db.models.functions import Concat
from django.http import FileResponse, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportMixin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter, RangeDateFilter
from unfold.decorators import action, display

from course.forms import CertificateImportForm, CodeConfirmImportForm
from course.models import Certificate, CertificateRenderTask, Course, Intake
from course.resources import CertificateResource
from course.tasks import Trigger, render_certificate
from course.utils import CertificateFileNameBuilder
from shared.widgets import Target, a


@admin.register(Course)
class CourseAdmin(ModelAdmin, SimpleHistoryAdmin):
    search_fields = ("title",)
    list_display = ("title", "display_intakes", "created_at", "updated_at")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("intakes")
            .annotate(intake_count=Count("intakes", distinct=True))
        )

    @display(
        description=_("Intakes"),  # type: ignore[arg-type]
        ordering="intake_count",
        dropdown=True,
    )
    def display_intakes(self, obj: Course):
        items = [
            {
                "title": f"{intake.start_date} - {intake.end_date}",
                "link": reverse("admin:course_intake_change", args=(intake.id,)),
            }
            for intake in obj.intakes.all()
        ]
        count = len(items)

        return {
            "title": count if count else "-",
            "items": items,
            "striped": False,
            "width": 220,
        }


@admin.register(Intake)
class IntakeAdmin(ModelAdmin, SimpleHistoryAdmin):
    search_fields = ("course__title",)
    autocomplete_fields = ("course",)
    list_display = (
        "display_name",
        "display_certificates",
        "display_course",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
    )
    list_filter = (
        ("course", AutocompleteSelectFilter),
        ("start_date", RangeDateFilter),
        ("end_date", RangeDateFilter),
    )
    list_filter_submit = True

    @admin.display(
        description="Name",
    )
    def display_name(self, obj: Intake):
        return str(obj)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("course")
            .prefetch_related("certificates")
            .annotate(certificate_count=Count("certificates", distinct=True))
        )

    @display(
        description=_("Intakes"),  # type: ignore[arg-type]
        ordering="intake_count",
        dropdown=True,
    )
    def display_certificates(self, obj: Intake):
        items = [
            {
                "title": f"{certificate.first_name} {certificate.last_name}",
                "link": reverse("admin:course_certificate_change", args=(certificate.id,)),
            }
            for certificate in obj.certificates.all()
        ]
        count = len(items)

        return {
            "title": count if count else "-",
            "items": items,
            "striped": False,
        }

    @display(
        description=_("Course"),
        ordering="course__title",
    )
    def display_course(self, obj: Intake):
        return a(
            obj.course.title,
            href=reverse("admin:course_course_change", args=(obj.course.id,)),
            target=Target.SELF,
        )


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
        ("intake__start_date", RangeDateFilter),
        ("intake__end_date", RangeDateFilter),
    )
    list_filter_submit = True
    search_fields = ("first_name", "last_name", "intake__course__title")
    actions = ["download_selected_action"]
    actions_row = ["regenerate_row_action", "download_row_action"]

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
    def intake__course(self, obj: Certificate):
        return a(
            obj.intake.course.title,
            href=reverse("admin:course_course_change", args=(obj.intake.course.id,)),
            target=Target.SELF,
        )

    @admin.display(description="Start date", ordering="intake__start_date")
    def intake__start_date(self, obj):
        return obj.intake.start_date

    @admin.display(description="End date", ordering="intake__end_date")
    def intake__end_date(self, obj):
        return obj.intake.end_date

    @admin.action(
        description=_("Download selected %(verbose_name_plural)s"),
    )
    def download_selected_action(self, request: HttpRequest, queryset) -> FileResponse:
        tmp = NamedTemporaryFile(mode="w+b", suffix=".zip")

        with ZipFile(tmp, "w", compression=ZIP_DEFLATED) as archive:
            for certificate in queryset.select_related("intake__course"):
                if not certificate.file or not certificate.file.name:
                    continue

                filename = (
                    CertificateFileNameBuilder(certificate)
                    .add_course_title()
                    .add_separator()
                    .add_intake_start_date()
                    .add_separator()
                    .add_intake_end_date()
                    .add_separator()
                    .add_first_name()
                    .add_separator()
                    .add_last_name()
                    .build()
                )

                with certificate.file.open("rb") as file:
                    archive.writestr(filename, file.read())

        tmp.seek(0)

        return FileResponse(
            tmp,
            as_attachment=True,
            filename=f"certificates_{now().strftime('%Y-%m-%d_%H-%M-%S')}.zip",
            content_type="application/zip",
        )

    @action(
        icon="settings_backup_restore",
        description=_("Regenerate"),
        url_path="regenerate",
    )
    def regenerate_row_action(self, request: HttpRequest, object_id: UUID):
        certificate = Certificate.objects.get(id=object_id)
        history_instance = certificate.history.first()

        render_certificate.send(
            certificate_id=str(certificate.id),
            history_id=history_instance.history_id,
            trigger=Trigger.MANUAL.value,
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            mark_safe(
                _("Certificate regeneration for {certificate} has been started.").format(
                    certificate=a(
                        str(certificate),
                        href=reverse("admin:course_certificate_change", args=(certificate.id,)),
                        target=Target.SELF,
                    )
                ),
            ),
        )

        return redirect(reverse("admin:course_certificate_changelist"))

    @action(
        icon="download",
        description=_("Download"),
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
