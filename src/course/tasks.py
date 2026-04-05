from enum import Enum
from typing import Literal
from uuid import UUID

import dramatiq
from django.db import transaction
from simple_history.utils import update_change_reason

from course.models import Certificate
from course.services import CertificateRenderService


class Trigger(Enum):
    AUTO = "auto"
    MANUAL = "manual"


@dramatiq.actor
@transaction.atomic
def render_certificate(
    *,
    certificate_id: str,
    history_id: int,
    trigger: Literal["auto", "manual"] = Trigger.AUTO.value,
):
    History = Certificate.history.model

    instance = (
        Certificate.objects.select_related("intake", "intake__course").select_for_update().get(id=UUID(certificate_id))
    )
    history = History.objects.select_for_update().get(id=instance.id, history_id=history_id)

    service = CertificateRenderService(certificate=instance)
    filename, file = service.render()

    match trigger:
        case Trigger.AUTO.value:
            instance.file.save(filename, file, save=False)
            if history.next_record is None:
                instance.save_without_historical_record()

            history.file = instance.file
            history.save()
        case Trigger.MANUAL.value:
            instance.file.save(filename, file, save=True)
            update_change_reason(instance, "Certificate manually re-rendered.")
