from django.contrib.auth.models import AbstractUser, Group
from simple_history import register
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    history = HistoricalRecords()


register(Group, app=__package__)
