from functools import partial
from typing import Type

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from course.models import Certificate
from course.tasks import render_certificate


@receiver(post_save, sender=Certificate)
def certificate_post_save(sender: Type[Certificate], instance: Certificate, **kwargs):
    if instance.dry_run:
        return

    if instance.tracker.has_changed("file") and instance.tracker.previous("file") is None:
        return

    if set(instance.tracker.changed().keys()) & {"first_name", "last_name", "intake"}:
        transaction.on_commit(
            partial(
                render_certificate.send,
                str(instance.id),
            )
        )
