from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from .pipeline import *
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from .models import *
from django.views.generic.edit import FormView
from .forms import *
from django.forms import formset_factory

from django.shortcuts import render_to_response


# Create your views here.
def home(request):
    if 'expression' in request.POST:
        return HttpResponseRedirect(reverse("ngs pipeline home"))
    if 'phylogenie' in request.POST:
        return HttpResponseRedirect(reverse('phylogenic pipeline hub'))
    return render(request, "ngs/home.html", locals())


def pipeline(request):
    FastQFormSet = formset_factory(FastQForm)

    if request.method == 'POST':
        formset = FastQFormSet(request.POST, files=request.FILES)
        if formset.is_valid():
            r = Request()
            r.save()
            for form in formset:
                fast_q = form.save(commit=False)
                fast_q.request = r
                fast_q.save()
            for file in r.fastq_set.all():
                file.generate_fastqc()
            print(r.pk)
            return redirect('ngs fastqc', r.pk)
    else:
        formset = FastQFormSet()
    return render(request, 'ngs/pipeline/formset_fastq.html', locals())

def fastqc(request, id_request):
    print("caca")
    fastqcs = []
    r = Request.objects.get(pk=id_request)
    for fastq in r.fastq_set.all():
        for fastqc in fastq.fastqc_set.all():
            with open(fastqc.file.path) as html:
                fastqcs.append(html.read())
    print(fastqcs)
    htmlfastqc = get_html()
    return render(request, "ngs/pipeline/fastqc.html", locals())


def phylo(request):
    return render(request, "ngs/phylo.html", locals())
