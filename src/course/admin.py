from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin

from course.models import Certificate, Course, Intake


@admin.register(Course)
class CourseAdmin(ModelAdmin, SimpleHistoryAdmin):
    pass


@admin.register(Intake)
class IntakeAdmin(ModelAdmin, SimpleHistoryAdmin):
    pass


@admin.register(Certificate)
class CertificateAdmin(ModelAdmin, SimpleHistoryAdmin):
    pass
