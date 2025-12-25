from typing import Type

from django.db.models.signals import pre_save
from django.dispatch import receiver

from course.models import Certificate
from course.services import CertificateRenderService


@receiver(pre_save, sender=Certificate)
def certificate_pre_save(sender: Type[Certificate], instance: Certificate, **kwargs):
    if instance.dry_run:
        return

    if instance.tracker.has_changed("file") and instance.tracker.previous("file") is None:
        return

    if set(instance.tracker.changed().keys()) & {"first_name", "last_name", "intake"}:
        service = CertificateRenderService(certificate=instance)
        service.render()
