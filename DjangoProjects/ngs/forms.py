from django import forms
from .models import *


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class FastQForm(forms.ModelForm):
    class Meta:
        model = FastQ
        fields = ['archive']

    def __init__(self, *args, **kwargs):
        super(FastQForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'required': 'True'})
