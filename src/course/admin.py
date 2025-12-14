from django.contrib import admin
from unfold.admin import ModelAdmin

from course.models import Certificate, Course, Intake


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    pass


@admin.register(Intake)
class IntakeAdmin(ModelAdmin):
    pass


@admin.register(Certificate)
class CertificateAdmin(ModelAdmin):
    pass
