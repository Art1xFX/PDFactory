from typing import Callable, Optional

from django.utils.text import slugify

from course.models import Certificate


class CertificateFileNameBuilder:
    def __init__(
        self,
        certificate: Certificate,
        suffix: str = "",
        prefix: str = "",
        extension: str = "pdf",
        slugify: Optional[Callable[[str], str]] = slugify,
    ):
        self.certificate = certificate
        self.file_name = ""
        self.suffix = suffix
        self.prefix = prefix
        self.extension = extension
        self.slugify = slugify

    def reset(self):
        self.file_name = ""

    def add_first_name(self):
        self.file_name += self.certificate.first_name
        return self

    def add_last_name(self):
        self.file_name += self.certificate.last_name
        return self

    def add_course_title(self):
        self.file_name += self.certificate.intake.course.title
        return self

    def add_intake_start_date(self, format: str = "%d-%m"):
        self.file_name += self.certificate.intake.start_date.strftime(format)
        return self

    def add_intake_end_date(self, format: str = "%d-%m-%Y"):
        self.file_name += self.certificate.intake.end_date.strftime(format)
        return self

    def add_separator(self, separator: str = "_"):
        self.file_name += separator
        return self

    def build(self) -> str:
        filename = self.prefix + self.file_name + self.suffix

        if self.slugify:
            filename = slugify(filename)

        filename += "." + self.extension

        return filename
