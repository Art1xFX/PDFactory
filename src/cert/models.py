from django.db import models

from cert.validators import DjangoTemplateValidator


class Template(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField(validators=[DjangoTemplateValidator()])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
