import logging

from dramatiq.middleware import Middleware

LOGGER = logging.getLogger(__name__)


class AdminMiddleware(Middleware):
    """This middleware keeps track of task executions."""

    def after_enqueue(self, broker, message, delay):
        if message.actor_name != "render_certificate":
            return

        LOGGER.debug(
            "Creating task with ID '%r' for certificate '%r'.",
            message.message_id,
            message.options.get("certificate_id"),
        )

        from course.models import CertificateRenderTask  # pylint: disable=import-outside-toplevel

        task, created = CertificateRenderTask.objects.get_or_create(
            id=message.message_id,
            certificate_id=message.kwargs.get("certificate_id"),
            defaults={
                "status": CertificateRenderTask.Status.PENDING,
            },
        )
        if not created:
            task.status = CertificateRenderTask.Status.PENDING
            task.save()

    def before_process_message(self, broker, message):
        if message.actor_name != "render_certificate":
            return

        from course.models import CertificateRenderTask  # pylint: disable=import-outside-toplevel

        task, created = CertificateRenderTask.objects.get_or_create(
            id=message.message_id,
            certificate_id=message.kwargs.get("certificate_id"),
            defaults={
                "status": CertificateRenderTask.Status.IN_PROGRESS,
            },
        )
        if not created:
            task.status = CertificateRenderTask.Status.IN_PROGRESS
            task.save()

    def after_skip_message(self, broker, message):
        if message.actor_name != "render_certificate":
            return

        from course.models import CertificateRenderTask  # pylint: disable=import-outside-toplevel

        self.after_process_message(broker, message, status=CertificateRenderTask.Status.SKIPPED)

    def after_process_message(self, broker, message, *, result=None, exception=None, status=None):
        if message.actor_name != "render_certificate":
            return

        from course.models import CertificateRenderTask  # pylint: disable=import-outside-toplevel

        if exception is not None:
            status = CertificateRenderTask.Status.FAILED
        elif status is None:
            status = CertificateRenderTask.Status.DONE

        LOGGER.debug("Updating Task from message %r.", message.message_id)

        task, created = CertificateRenderTask.objects.get_or_create(
            id=message.message_id,
            certificate_id=message.kwargs.get("certificate_id"),
            defaults={
                "status": status,
            },
        )
        if not created:
            task.status = status
            task.save()
