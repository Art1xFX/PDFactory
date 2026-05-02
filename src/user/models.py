from django.contrib.auth.models import AbstractUser, Group
from simple_history import register
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    history = HistoricalRecords()

    class Meta:
        permissions = [
            ("view_user_personal_data", "Can view user personal data"),
            ("change_user_personal_data", "Can change user personal data"),
        ]


register(Group, app=__package__, m2m_fields=["permissions"])
