from django import forms

class NGSForm(forms.Form):
    NGS_data = forms.FileField()

class GeneForm(forms.Form):
    Gene_data = forms.CharField()

class CytoscapeForm(forms.Form):
    JSON = forms.FileField()
