from uuid import uuid4

from django.core.validators import FileExtensionValidator
from django.db import models
from simple_history.models import HistoricalRecords


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(
        upload_to="files/",
        validators=[FileExtensionValidator(allowed_extensions=["css", "jpg", "jpeg", "png", "svg", "webp"])],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()
