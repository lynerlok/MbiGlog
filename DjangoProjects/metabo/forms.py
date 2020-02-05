from django import forms

class NGSForm(forms.Form):
    NGS_data = forms.FileField()