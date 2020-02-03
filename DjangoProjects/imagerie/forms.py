from django import forms

from .models import *


class ImportImageForm(forms.ModelForm):
    class Meta:
        model = SubmittedImage
        fields = ["image", "plant_organ", "background_type"]
