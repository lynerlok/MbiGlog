from django import forms
from .models import *


class FileFieldForm(forms.Form):
    file_field = forms.FileField()



class AlignFieldForm(forms.Form):
    file_field = forms.FileField(label= 'Fasta containing ARN18s')
    your_email = forms.EmailField(label='your email', max_length=200)

class TreeForm(forms.Form):
    file_field = forms.FileField(label = 'Aligned Sequences (Clustal, Fasta, MSF')
    your_email = forms.EmailField(label='your email', max_length=200)


class FastQForm(forms.ModelForm):
    class Meta:
        model = FastQ
        fields = ['archive']

    def __init__(self, *args, **kwargs):
        super(FastQForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'required': 'True'})
