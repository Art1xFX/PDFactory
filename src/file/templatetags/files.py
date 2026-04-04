from pathlib import Path

from django import template
from django.core.files.storage import FileSystemStorage

from file.models import File, FontFamily, FontStyle

register = template.Library()


FONT_EXTENSION_FORMAT_MAP = {
    "ttf": "truetype",
    "otf": "opentype",
    "woff": "woff",
    "woff2": "woff2",
}


@register.simple_tag
def media_url(uuid):
    file = File.objects.get(id=uuid)
    storage = file.file.storage

    if not isinstance(storage, FileSystemStorage):
        raise ValueError("Unsupported file storage.")

    return f"file://{storage.path(file.file.name)}"


@register.inclusion_tag("file/templatetags/font_face.css")
def font_face_definition(font_family_name: str):
    font_family = FontFamily.objects.get(name=font_family_name)

    font_faces = []
    fonts = font_family.font_set.all().order_by("position", "id")

    for font in fonts:
        storage = font.file.storage

        if not isinstance(storage, FileSystemStorage):
            raise ValueError("Unsupported file storage.")

        url = f"file://{storage.path(font.file.name)}"

        styles = font.styles or [FontStyle.NORMAL]
        weights = font.weight or [400]

        for style in styles:
            for weight in weights:
                font_faces.append(
                    {
                        "family_name": font_family.name,
                        "src__url": url,
                        "src__format": FONT_EXTENSION_FORMAT_MAP.get(
                            Path(font.file.name).suffix.lower().lstrip("."), "truetype"
                        ),
                        "font_weight": weight,
                        "font_style": style,
                    }
                )

    return {"font_faces": font_faces}
