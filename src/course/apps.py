from importlib import import_module

from django.apps import AppConfig


class CourseConfig(AppConfig):
    name = "course"

    def ready(self):
        import_module("course.signals")
