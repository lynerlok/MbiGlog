from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from .pipeline import *
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from .models import *
from django.views.generic.edit import FormView
from .forms import *
from django.forms import formset_factory


# Create your views here.
def home(request):
    if 'expression' in request.POST:
        return HttpResponseRedirect(reverse("ngs pipeline home"))
    return render(request, "ngs/home.html", locals())


def pipeline(request):
    FastQFormSet = formset_factory(FastQForm)

    if request.method == 'POST':
        formset = FastQFormSet(request.POST, files=request.FILES)
        if formset.is_valid():
            request = Request()
            request.save()
            for form in formset:
                fast_q = form.save(commit=False)
                fast_q.request = request
                fast_q.save()
                fast_q.generate_fastqc()

            return HttpResponseRedirect(reverse("ngs_fastqc"))

    else:
        formset = FastQFormSet()
    return render(request, 'ngs/pipeline/formset_fastq.html', locals())



        # for afile in request.FILES.getlist('fastq'):
        #     fs = FileSystemStorage()
        #     filename = fs.save(afile.name, afile)
        #     uploaded_file_url = fs.url(filename)

    if 'fastqc' in request.POST:
        fastqctool = go_fastqc()
        if fastqctool == 0:
            return HttpResponseRedirect(reverse("ngs_fastqc"))
    return render(request, "ngs/pipeline/pipeline.html", locals())


def fastqc(request, id_request):
    r = Request.objects.get(pk=id_request)
    for fastq in r.fastq_set.all():
        for fastqc in fastq.fastqc_set.all():
            print(fastqc.file.open())
    htmlfastqc = get_html()
    return render(request, "ngs/pipeline/fastqc.html", locals())
