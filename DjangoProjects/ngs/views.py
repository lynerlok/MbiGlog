from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from .pipeline import *
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.conf import settings
from .models import *
from django.views.generic.edit import FormView
from .forms import *
from django.forms import formset_factory
import subprocess

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
            return redirect('ngs fastqc', r.pk)
    else:
        formset = FastQFormSet()
    return render(request, 'ngs/pipeline/formset_fastq.html', locals())

def fastqc(request, id_request):
    fastqcs = []
    r = Request.objects.get(pk=id_request)
    for fastq in r.fastq_set.all():
        for fastqc in fastq.fastqc_set.all():
            fastqcs.append(fastqc)
            # with open(fastqc.file.path) as html:
            #     fastqcs.append(html.read())
    # htmlfastqc = get_html()
    return render(request, "ngs/pipeline/fastqc.html", locals())


def phylo_align(request):
    correct = False
    align_request = AlignFieldForm(request.POST or None, request.FILES)

    if align_request.is_valid():
        align = Sequence()
        align.mail = align_request.cleaned_data['your_email']
        align.file = align_request.cleaned_data['file_field']
        align.save()
        correct = True
        print(settings.BASE_DIR)
        script = settings.BASE_DIR+'/ngs/clustalo.py'
        output = settings.BASE_DIR+'/media/ngs/align_result'
        tool = subprocess.Popen(['python', script,'--email',align.mail,'--outfile','AlignedData', '--stype', 'rna',align.file.path, ], close_fds=True , cwd=output)
        tool.communicate()
        return phylo_tree(request)


    return render(request, "ngs/phylo.html", {'align':align_request}, locals())

def phylo_tree(request):
    correct = False
    tree_request = TreeForm(request.POST or None, request.FILES)

    if tree_request.is_valid():
        tree = Alignement()
        tree.mail = tree_request.cleaned_data['your_email']
        tree.file = tree_request.cleaned_data['file_field']
        tree.save()
        script = settings.BASE_DIR+'/ngs/simple_phylogeny.py'
        output = settings.MEDIA_ROOT+'/ngs/tree_result'
        tool = subprocess.Popen(['python', script, '--email', tree.mail, '--stype', 'rna', tree.file.path, ], close_fds=True, cwd=output)
    return render(request, "ngs/phylo_tree.html",{'tree': tree_request},locals())

