from django import forms

from .models import *


class ImportImageForm(forms.ModelForm):
    class Meta:
        model = SubmittedImage
        fields = ["image", "plant_organ", "background_type"]

    def __init__(self, *args, **kwargs):
        super(ImportImageForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'required': 'True'
            })
