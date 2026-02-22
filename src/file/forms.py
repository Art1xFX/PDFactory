from django import forms
from unfold.contrib.forms.widgets import ArrayWidget

from file.models import Font, FontStyle


class FontModelForm(forms.ModelForm):
    class Meta:
        model = Font
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["styles"].widget = ArrayWidget(choices=FontStyle.choices)
        self.fields["weight"].widget = ArrayWidget()

    def clean_weight(self):
        weights = self.cleaned_data.get("weight", [])

        if len(weights) != len(set(weights)):
            raise forms.ValidationError("Duplicate items are not allowed.")

        return weights

    def clean_styles(self):
        styles = self.cleaned_data.get("styles", [])

        if len(styles) != len(set(styles)):
            raise forms.ValidationError("Duplicate items are not allowed.")

        return styles
