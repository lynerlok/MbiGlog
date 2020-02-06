from django.http import HttpResponseRedirect, HttpResponse
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
import itolapi

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
    if 'hisat' in request.POST:
        return redirect('hisat2')
    return render(request, "ngs/pipeline/fastqc.html", locals())

def hisat(request):
    if os.path.isdir(Genome.dir.as_posix()) == False:
        process = subprocess.Popen("mkdir " + Genome.dir.as_posix(), shell=True)
        process.communicate()
    if os.path.isdir(Annotation.dir.as_posix()) == False:
        process = subprocess.Popen("mkdir " + Annotation.dir.as_posix(), shell=True)
        process.communicate()

    genome_annotations_request = GenomeAnnotationsForm(request.POST or None, request.FILES)

    if request.method=='POST':
        if genome_annotations_request.is_valid():
            r = Request()
            r.save()
            genome = Genome()
            genome.request = r
            genome.file = genome_annotations_request.cleaned_data['genome_file']
            genome.save()
            annotations = Annotation()
            annotations.request = r
            annotations.file = genome_annotations_request.cleaned_data['annotations_file']
            annotations.save()
            return redirect('R analysis')
    return render(request, "ngs/pipeline/hisat.html",locals())

def ranalysis(request):
    return render(request, "ngs/pipeline/R_analysis.html",locals())

def phylo_align(request):
    align_request = AlignFieldForm(request.POST or None, request.FILES)

    if align_request.is_valid():
        align = Sequence()
        align.mail = align_request.cleaned_data['your_email']
        align.file = align_request.cleaned_data['file_field']
        align.save()
        print(settings.BASE_DIR)
        script = settings.BASE_DIR+'/ngs/clustalo.py'
        output = settings.BASE_DIR+'/media/ngs/align_result'
        tool = subprocess.Popen(['python', script,'--email',align.mail,'--outfile','AlignedData', '--stype', 'rna',align.file.path, ], close_fds=True , cwd=output)
        tool.communicate()
        tool.communicate()
        return HttpResponseRedirect(reverse("phylogenic compute tree"))


    return render(request, "ngs/phylo.html", {'align':align_request}, locals())

def phylo_tree(request):
    tree_request = TreeForm(request.POST or None, request.FILES)
    if tree_request.is_valid():
        tree = Alignement()
        tree.mail = tree_request.cleaned_data['your_email']
        tree.file = tree_request.cleaned_data['file_field']
        tree.save()
        script = settings.BASE_DIR+'/ngs/simple_phylogeny.py'
        output = settings.MEDIA_ROOT+'/ngs/tree_result'
        tool = subprocess.Popen(['python', script, '--email', tree.mail,'--outfile','tree', tree.file.path], close_fds=True, cwd=output)
        tool.communicate()
        tool.communicate()
        return HttpResponseRedirect(reverse("phylogenic visualization"))

    return render(request, "ngs/phylo_tree.html",{'tree': tree_request},locals())


def phylo_visu(request):
    tree = settings.MEDIA_ROOT + '/ngs/tree_result/tree.tree.ph'
    itool = itolapi.Itol()
    itool.add_file(tree)
    itool.params['treeName'] = 'test_tree'
    status = itool.upload()
    assert status != False
    tree_link = itool.get_webpage()
    return render(request, "ngs/phylo_visu.html", {"tree": tree_link}, locals())

