from functools import partial

from django.db import transaction
from django.dispatch import receiver
from simple_history.signals import post_create_historical_record

from course.models import Certificate
from course.tasks import render_certificate


@receiver(post_create_historical_record, sender=Certificate.history.model)
def certificate_post_create_historical_record(sender, instance: Certificate, history_instance, **kwargs):
    if instance.dry_run:
        return

    if instance.tracker.has_changed("file") and instance.tracker.previous("file") is None:
        return

    if set(instance.tracker.changed().keys()) & {"first_name", "last_name", "intake"}:
        transaction.on_commit(
            partial(
                render_certificate.send,
                certificate_id=str(instance.id),
                history_id=history_instance.history_id,
            )
        )
