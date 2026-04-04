from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
from simple_history.models import HistoricalRecords

from cert.models import Template


class Course(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return str(self.title)


class Intake(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    template = models.ForeignKey(Template, on_delete=models.DO_NOTHING, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.course} ({self.start_date} - {self.end_date})"


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    intake = models.ForeignKey(Intake, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    file = models.FileField(upload_to="certificates/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tracker = FieldTracker()
    history = HistoricalRecords()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dry_run = False

    def __str__(self):
        return f"Certificate for {self.first_name} {self.last_name} - {self.intake}"


class CertificateRenderTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        IN_PROGRESS = "in_progress", _("In progress")
        SKIPPED = "skipped", _("Skipped")
        DONE = "done", _("Done")
        FAILED = "failed", _("Failed")

    id = models.UUIDField(primary_key=True, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["updated_at"]),
            models.Index(fields=["certificate", "status", "updated_at"]),
        ]

    def __str__(self):
        return f"Render task for {self.certificate}"
