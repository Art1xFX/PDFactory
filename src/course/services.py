from django.core.files.base import ContentFile
from django.template import engines
from django.utils.text import slugify

from course.models import Certificate


class CertificateRenderService:
    def __init__(self, certificate: Certificate):
        self.certificate = certificate

    def render(self):
        certificate = self.certificate
        intake = certificate.intake
        course = intake.course

        html = (
            engines["django"]
            .from_string(intake.template.content)
            .render(
                context={
                    "certificate": certificate,
                }
            )
        )

        filename = f"{course.id}/{intake.id}/{slugify(certificate.last_name)}_{slugify(certificate.first_name)}.html"

        certificate.file.save(filename, ContentFile(html.encode("utf-8")), save=False)

        return ContentFile(html.encode("utf-8"))
