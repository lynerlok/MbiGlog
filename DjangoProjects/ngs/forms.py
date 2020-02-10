from django import forms
from .models import *


class FileFieldForm(forms.Form):
    file_field = forms.FileField()


class GenomeAnnotationsForm(forms.Form):
    genome_file = forms.FileField(label='Genome file')
    annotations_file_gff = forms.FileField(label='Annotations file GFF')
    annotations_file_gtf = forms.FileField(label='Annotations file GTF')

    fastq = forms.ModelMultipleChoiceField(
        label='FastQ to work on',
        queryset=FastQ.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'fastq', 'required': ''})
    )

class IDProteoForm(forms.Form):
    id_field = forms.CharField(label="ID GenBank", max_length=50)


class RNAFileFieldForm(forms.Form):
    file_field = forms.FileField(label = 'File containing species name')
    email_field = forms.EmailField(label='your email', max_length=200)


class AlignFieldForm(forms.Form):
    file_field = forms.FileField(label='Fasta containing ARN18s')
    your_email = forms.EmailField(label='your email', max_length=200)


class TreeForm(forms.Form):
    file_field = forms.FileField(label='Aligned Sequences (Clustal, Fasta, MSF)')
    your_email = forms.EmailField(label='your email', max_length=200)


TRIM_LEADING=(
    ("0","0"),
    ("5", "5"),
    ("10", "10"),
    ("15", "15"),
    ("20", "20")
)

TRIM_TRAILING =(
    ("0", "0"),
    ("5", "5"),
    ("10", "10"),
    ("15", "15"),
    ("20", "20")
)

TRIM_AVGQUAL=(
    ("0","0"),
    ("5", "5"),
    ("10", "10"),
    ("15", "15"),
    ("20", "20")
)

TRIM_SLIDING_WINDOWS = (
    ("0","0"),
    ("5", "5"),
    ("10", "10"),
    ("15", "15"),
    ("20", "20")
)

TRIM_MINLEN = (
    ("0","0"),
    ("5", "5"),
    ("10", "10"),
    ("15", "15"),
    ("20", "20")
)

class TrimOptionsForm(forms.Form):
    leading_field = forms.ChoiceField(label="Leading",choices=TRIM_LEADING)
    trailing_field = forms.ChoiceField(label="Trailing", choices=TRIM_TRAILING)
    avgqual_field = forms.ChoiceField(label="AVGQUAL", choices=TRIM_AVGQUAL)
    slid_wind_field = forms.ChoiceField(label="Sliding Windows", choices=TRIM_SLIDING_WINDOWS)
    minlen_field = forms.ChoiceField(label="Minlen", choices=TRIM_MINLEN)
    name_field = forms.CharField(label="Name of the Fastq", max_length=200)


class FastQForm(forms.ModelForm):
    class Meta:
        file_field = forms.FileField(label='genome')
        model = FastQ
        fields = ['archive']

    def __init__(self, *args, **kwargs):
        super(FastQForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'required': 'True'})

class SelectFastQForm(forms.Form):
    fastq = forms.ModelChoiceField(
        queryset=FastQ.objects.all(),
        widget=forms.Select(attrs={'class': 'fastq', 'required': 'True'})
    )