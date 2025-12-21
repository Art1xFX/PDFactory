from django import template
from django.core.files.storage import FileSystemStorage

from file.models import File

register = template.Library()


@register.simple_tag
def media_url(uuid):
    file = File.objects.get(id=uuid)
    storage = file.file.storage

    if not isinstance(storage, FileSystemStorage):
        raise ValueError("Unsupported file storage.")

    return f"file://{storage.path(file.file.name)}"
