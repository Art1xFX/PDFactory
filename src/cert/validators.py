from django.core.exceptions import ValidationError
from django.template import engines
from django.utils.deconstruct import deconstructible


@deconstructible
class DjangoTemplateValidator:
    def __init__(self, engine_name: str = "django"):
        self.engine_name = engine_name

    def __call__(self, content: str):
        try:
            engines[self.engine_name].from_string(content)
        except Exception as exc:
            raise ValidationError(str(exc)) from exc
