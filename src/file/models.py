from uuid import uuid4

from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify
from simple_history.models import HistoricalRecords


def font_file_upload_to(instance, filename):
    return f"fonts/{slugify(instance.family.name)}/{filename}"


def font_styles_default():
    return [FontStyle.NORMAL, FontStyle.ITALIC]


class FontStyle(models.TextChoices):
    NORMAL = "normal", "Normal"
    ITALIC = "italic", "Italic"
    OBLIQUE = "oblique", "Oblique"


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


class FontFamily(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "font families"
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unq_font_family_name"),
        ]

    def __str__(self):
        return str(self.name)


class Font(models.Model):
    file = models.FileField(
        upload_to=font_file_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=["ttf", "otf", "woff", "woff2"])],
    )
    family = models.ForeignKey(FontFamily, on_delete=models.CASCADE)
    weight = ArrayField(models.PositiveSmallIntegerField(default=400), default=list, null=True, blank=True)
    styles = ArrayField(
        models.CharField(max_length=50, choices=FontStyle.choices),
        default=font_styles_default,
    )
    position = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        result = f"{self.family.name}"
        if self.styles:
            result += f" [{', '.join(FontStyle(style).label for style in self.styles)}]"  # pylint: disable=not-an-iterable
        if self.weight:
            result += f" ({', '.join(str(weight) for weight in self.weight)})"  # pylint: disable=not-an-iterable
        return result
