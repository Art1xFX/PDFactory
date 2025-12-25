from django import forms
from import_export.forms import ConfirmImportForm
from unfold import widgets
from unfold.contrib.import_export.forms import ImportForm

from course.models import Intake


class CertificateImportForm(ImportForm):
    intake = forms.ModelChoiceField(queryset=Intake.objects.all(), widget=widgets.UnfoldAdminSelectWidget())


class CodeConfirmImportForm(ConfirmImportForm):
    intake = forms.ModelChoiceField(queryset=Intake.objects.all(), widget=forms.HiddenInput())
