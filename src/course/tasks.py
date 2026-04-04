from uuid import UUID

import dramatiq
from django.db import transaction

from course.models import Certificate
from course.services import CertificateRenderService


@dramatiq.actor
@transaction.atomic
def render_certificate(*, certificate_id: str):
    instance = Certificate.objects.select_for_update().get(id=UUID(certificate_id))

    service = CertificateRenderService(certificate=instance)
    filename, file = service.render()

    instance.file.save(filename, file, save=True)
