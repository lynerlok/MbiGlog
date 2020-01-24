from django.shortcuts import render
from django.contrib import messages
from .pipeline import *
from django.core.files.storage import FileSystemStorage

from django.views.generic.edit import FormView
from .forms import FileFieldForm

# Create your views here.
def home(request):
    if request.method == 'POST':
        for afile in request.FILES.getlist('fastq'):
            fs = FileSystemStorage()
            filename = fs.save(afile.name, afile)
            uploaded_file_url = fs.url(filename)

    if 'fastqc' in request.POST:
        fastqc = go_fastqc()
    return render(request, "ngs/home.html", locals())

    # if request.GET.get('fastqc'):
    #     print("MDR")
    #     return render(request, "ngs/fastqc.html", locals())
    # return render(request, "ngs/home.html", locals())

# def fastqc(request):
#     return render(request, "ngs/fastqc.html", locals())

# def simple_upload(request):
#     return render(request,'ngs/home.html')
