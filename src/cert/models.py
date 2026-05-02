from django.db import models
from simple_history.models import HistoricalRecords

from cert.validators import DjangoTemplateValidator


class Template(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField(validators=[DjangoTemplateValidator()])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return str(self.name)
