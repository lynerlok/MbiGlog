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
from django.core.files import File
import subprocess
import itolapi


from django.shortcuts import render_to_response




# Create your views here.
def home(request):
    if 'expression' in request.POST:
        return HttpResponseRedirect(reverse("ngs pipeline home"))
    if 'phylogenie' in request.POST:
        return HttpResponseRedirect(reverse('phylogenic pipeline hub'))
    if 'proteomique' in request.POST:
        return  HttpResponseRedirect(reverse('Proteo fasta'))
    return render(request, "ngs/home.html", locals())


def proteo(request):
    id_gen = IDProteoForm(request.GET or None)
    if id_gen.is_valid():
        id = id_gen.cleaned_data["id_field"]
        script = settings.BASE_DIR +'/ngs/getSeq.py'
        output = settings.MEDIA_ROOT + 'ngs/fasta_proteo'
        if os.path.isdir(output) == False:
            dir = settings.MEDIA_ROOT + 'ngs'
            process = subprocess.Popen(["mkdir","fasta_proteo"], cwd=dir)
            process.communicate()
            tool = subprocess.Popen(["python", script, id], cwd=output)
            tool.communicate()
        else:
            tool = subprocess.Popen(["python", script,id], cwd=output)
            tool.communicate()
        return render(request, "ngs/proteo.html",{"id": id_gen}, locals())


    return render(request, "ngs/proteo.html",{"id": id_gen}, locals())




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
    all_fastqc =  FastQ.objects.all()
    trim_form = TrimOptionsForm(request.POST or None)
    fastqcs = []
    if trim_form.is_valid():
        for fastq in all_fastqc:
            if trim_form.cleaned_data["name_field"] == Path(fastq.archive.path).name.split('.')[0]:
                trimo_path =  settings.BASE_DIR+"/ngs/Trimmomatic-0.36/trimmomatic-0.36.jar"
                trim_name = Path(fastq.archive.path).name
                trim_filename = Path(fastq.archive.path).name+".trim.fil.gz"
                leading = "LEADING:"+ trim_form.cleaned_data["leading_field"]
                trailing ="TRAILING:"+ trim_form.cleaned_data["trailing_field"]
                avgqual = "AVGQUAL:"+ trim_form.cleaned_data["avgqual_field"]
                slid_wind ="SLIDINGWINDOW:"+ trim_form.cleaned_data["slid_wind_field"]+":30"
                minlen = "MINLEN:"+ trim_form.cleaned_data["minlen_field"]
                output = settings.MEDIA_ROOT+"ngs/fastq"
                trimo = subprocess.Popen(["java", "-jar", trimo_path, "SE",trim_name, trim_filename,leading,trailing,avgqual,slid_wind,minlen], close_fds=True, cwd=output)
                trimo.communicate()
                f = open(output+'/'+trim_filename)
                myFile =File(f)
                fastq.archive = myFile
                return redirect('ngs fastqc', id_request)

    r = Request.objects.get(pk=id_request)
    for fastq in r.fastq_set.all():
        for fastqc in fastq.fastqc_set.all():
            fastqcs.append(fastqc)
    if 'hisat' in request.POST:
        return redirect('hisat2')
    return render(request, "ngs/pipeline/fastqc.html", {"trim": trim_form}, locals())


def hisat(request):
    if os.path.isdir(Genome.dir.as_posix()) == False:
        process = subprocess.Popen("mkdir " + Genome.dir.as_posix(), shell=True)
        process.communicate()

    genome_annotations_request = GenomeAnnotationsForm(request.POST or None, request.FILES, prefix='ga')

    FastQFormSet = formset_factory(SelectFastQForm)

    if request.method == 'POST':
        formset = FastQFormSet(request.POST, files=request.FILES, prefix='fast_q_name')

        if genome_annotations_request.is_valid() and formset.is_valid():
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
            for form in formset:
                fastq = form.cleaned_data['fastq']
                fastq.generate_hisat()
            return redirect('R analysis')
    else:
        formset = FastQFormSet(prefix='fast_q_name')

    return render(request, "ngs/pipeline/hisat.html", locals())


def ranalysis(request):
    return render(request, "ngs/pipeline/R_analysis.html", locals())


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
