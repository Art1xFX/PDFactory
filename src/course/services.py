from django.core.files.base import ContentFile
from django.template import engines
from weasyprint import HTML

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

        pdf = HTML(string=html).write_pdf()

        filename = f"{course.id}/{intake.id}/{certificate.id}.pdf"

        certificate.file.save(filename, ContentFile(pdf), save=False)

        return ContentFile(html.encode("utf-8"))
