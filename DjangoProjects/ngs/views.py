from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
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
import os

from django.shortcuts import render_to_response


# Create your views here.
def home(request):
    if 'expression' in request.POST:
        return HttpResponseRedirect(reverse("ngs pipeline home"))
    if 'phylogenie' in request.POST:
        return HttpResponseRedirect(reverse('phylogenic hub'))
    if 'proteomique' in request.POST:
        return HttpResponseRedirect(reverse('Proteo fasta'))
    return render(request, "ngs/home.html", locals())


def proteo(request):
    id_gen = IDProteoForm(request.GET or None)
    if id_gen.is_valid():
        id = id_gen.cleaned_data["id_field"]
        script = settings.BASE_DIR + '/ngs/getSeq.py'
        output = settings.MEDIA_ROOT + 'ngs/fasta_proteo'
        if os.path.isdir(output) == False:
            dir = settings.MEDIA_ROOT + 'ngs'
            process = subprocess.Popen(["mkdir", "fasta_proteo"], cwd=dir)
            process.communicate()
            tool = subprocess.Popen(["python", script, id], cwd=output)
            tool.communicate()
        else:
            tool = subprocess.Popen(["python", script, id], cwd=output)
            tool.communicate()
        return render(request, "ngs/proteo.html", {"id": id_gen}, locals())

    return render(request, "ngs/proteo.html", {"id": id_gen}, locals())


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
    r = Request.objects.get(pk=id_request)
    fastqcs = []
    for fastq in r.fastq_set.all():
        for fastqc in fastq.fastqc_set.all():
            fastqcs.append(fastqc)
    all_fastqc = FastQ.objects.all()
    trim_form = TrimOptionsForm(request.POST or None)
    if trim_form.is_valid():
        for fastq in all_fastqc:
            if trim_form.cleaned_data["name_field"] == Path(fastq.archive.path).name.split('.')[0]:
                trimo_path = settings.BASE_DIR + "/ngs/Trimmomatic-0.36/trimmomatic-0.36.jar"
                trim_name = Path(fastq.archive.path).name
                trim_filename = Path(fastq.archive.path).name + ".trim.fil.gz"
                leading = "LEADING:" + trim_form.cleaned_data["leading_field"]
                trailing = "TRAILING:" + trim_form.cleaned_data["trailing_field"]
                avgqual = "AVGQUAL:" + trim_form.cleaned_data["avgqual_field"]
                slid_wind = "SLIDINGWINDOW:" + trim_form.cleaned_data["slid_wind_field"] + ":30"
                minlen = "MINLEN:" + trim_form.cleaned_data["minlen_field"]
                output = settings.MEDIA_ROOT + "ngs/fastq"
                trimo = subprocess.Popen(
                    ["java", "-jar", trimo_path, "SE", trim_name, trim_filename, leading, trailing, avgqual, slid_wind,
                     minlen], close_fds=True, cwd=output)
                trimo.communicate()
                f = open(output + '/' + trim_filename)
                myFile = File(f)
                fastq.archive = myFile
                return redirect('ngs fastqc', id_request)
    if 'hisat' in request.POST:
        return redirect('hisat2')
    return render(request, "ngs/pipeline/fastqc.html", {"trim": trim_form, "fastqcs": fastqcs}, locals())


def hisat(request):
    if os.path.isdir(Genome.dir.as_posix()) == False:
        process = subprocess.Popen("mkdir " + Genome.dir.as_posix(), shell=True)
        process.communicate()
    if request.method == 'POST':
        genome_annotations_request = GenomeAnnotationsForm(request.POST or None, request.FILES, prefix='ga')
        if genome_annotations_request.is_valid():
            r = Request()
            r.save()
            genome = Genome()
            genome.request = r
            genome.file = genome_annotations_request.cleaned_data['genome_file']
            genome.save()
            annotations_gff = Annotation()
            annotations_gff.request = r
            annotations_gff.file = genome_annotations_request.cleaned_data['annotations_file_gff']
            annotations_gff.save()
            os.system("grep \"locus_type=protein_coding\" " + str(
                annotations_gff.file.file) + " |cut -f9 |cut -d';' -f1 |cut -d'=' -f2 > protein_coding")
            os.system("mv " + settings.BASE_DIR + "/" + "protein_coding " + genome.dir.as_posix() + "/")
            annotations_gtf = Annotation()
            annotations_gtf.request = r
            annotations_gtf.file = genome_annotations_request.cleaned_data['annotations_file_gtf']
            annotations_gtf.save()
            if os.path.isdir(Hisat.dir.as_posix()) == False:
                process = subprocess.Popen("mkdir " + Hisat.dir.as_posix(), shell=True)
                process.communicate()
            os.system("hisat2-build " + genome.file.path + " index")
            for i in range(1, 9):
                os.system("mv " + settings.BASE_DIR + "/" + "index." + str(i) + ".ht2 " + genome.dir.as_posix() + "/")
            for fastq in genome_annotations_request.cleaned_data['fastq']:
                fastq.generate_hisat(genome)
            return redirect('R analysis')
    else:
        genome_annotations_request = GenomeAnnotationsForm(prefix='ga')

    return render(request, "ngs/pipeline/hisat.html", locals())


def ranalysis(request):
    if os.path.isdir(settings.MEDIA_ROOT + "ngs/analysis/") == False:
        process = subprocess.Popen("mkdir " + settings.MEDIA_ROOT + "ngs/analysis/", shell=True)
        process.communicate()
    if request.method == 'POST':
        script_rstats = settings.BASE_DIR + '/ngs/post_analyse.R'
        process = subprocess.Popen("Rscript " + script_rstats + " " + Hisat.dir.as_posix() + " " + (
                settings.MEDIA_ROOT + str(Annotation.objects.filter(file__icontains=".gtf").first().file)) + " " + (
                                           settings.MEDIA_ROOT + 'ngs/analysis') + " " + (
                                           Genome.dir.as_posix() + '/protein_coding'), shell=True)
        process.communicate()
        return redirect('Results')
    return render(request, "ngs/pipeline/R_analysis.html", locals())


def results(request):
    media = settings.MEDIA_ROOT
    return render(request, "ngs/pipeline/Results.html",{"media" : settings.MEDIA_ROOT}, locals())


def phylo_hub(request):
    rna_list_request = RNAFileFieldForm(request.POST or None, request.FILES)

    if rna_list_request.is_valid():
        rna_list = Species_List()
        rna_list.file = rna_list_request.cleaned_data['file_field']
        email = rna_list_request.cleaned_data['email_field']
        rna_list.save()
        rna_list_path = settings.MEDIA_ROOT + 'ngs/tree/data_test_phylo.txt'
        rna_list = open(rna_list.file.path)
        script = settings.BASE_DIR + '/ngs/getSeq.py'
        output = settings.MEDIA_ROOT + 'ngs/fasta'

        # Step 1 - Get Fasta
        RNA_filepath = settings.MEDIA_ROOT + "ngs/RNA_request.txt"
        RNA_file = open(RNA_filepath, "a")
        for specie in rna_list:
            if os.path.isdir(output) == False:
                dir = settings.MEDIA_ROOT + 'ngs'
                process = subprocess.Popen(["mkdir", "fasta"], cwd=dir)
                process.communicate()
            tool = subprocess.Popen(["python", script, specie], cwd=output)
            tool.communicate()
            fasta_filename = specie + ".fasta"
            fasta = open(output + '/' + fasta_filename)
            for line in fasta:
                RNA_file.write(line)
            RNA_file.write("\n")
            fasta.close()
        RNA_file.close()

        # Step 2 - Perform Align
        script = settings.BASE_DIR + '/ngs/clustalo.py'
        output = settings.BASE_DIR + '/media/ngs/align_result'
        if os.path.isdir(output) == False:
            dir = settings.MEDIA_ROOT + 'ngs'
            process = subprocess.Popen(["mkdir", "align_result"], cwd=dir)
            process.communicate()
        tool = subprocess.Popen(
            ['python', script, '--email', email, '--outfile', 'AlignedData', '--stype', 'rna', RNA_filepath],
            close_fds=True, cwd=output)
        tool.communicate()
        tool.communicate()

        # Step 3 - Compute the tree
        align_filename = settings.MEDIA_ROOT + "ngs/align_result/AlignedData.aln-clustal_num.clustal_num"
        script = settings.BASE_DIR + '/ngs/simple_phylogeny.py'
        output = settings.MEDIA_ROOT + 'ngs/tree_result'
        if os.path.isdir(output) == False:
            dir = settings.MEDIA_ROOT + 'ngs'
            process = subprocess.Popen(["mkdir", "tree_result"], cwd=dir)
            process.communicate()
        print(align_filename)
        print(output)
        tool = subprocess.Popen(['python', script, '--email', email, '--outfile', 'tree', align_filename],
                                close_fds=True, cwd=output)
        tool.communicate()
        tool.communicate()
        return HttpResponseRedirect(reverse("phylogenic visualization"))

    if 'align' in request.POST:
        return HttpResponseRedirect(reverse("phylogenic pipeline align"))

    if 'tree' in request.POST:
        return HttpResponseRedirect(reverse("phylogenic compute tree"))

    return render(request, "ngs/phylo_hub.html", {"rna": rna_list_request}, locals())


def phylo_align(request):
    align_request = AlignFieldForm(request.POST or None, request.FILES)

    if align_request.is_valid():
        align = Sequence()
        align.mail = align_request.cleaned_data['your_email']
        align.file = align_request.cleaned_data['file_field']
        align.save()
        print(settings.BASE_DIR)
        script = settings.BASE_DIR + '/ngs/clustalo.py'
        output = settings.BASE_DIR + '/media/ngs/align_result'
        tool = subprocess.Popen(
            ['python', script, '--email', align.mail, '--outfile', 'AlignedData', '--stype', 'rna', align.file.path, ],
            close_fds=True, cwd=output)
        tool.communicate()
        tool.communicate()
        return HttpResponseRedirect(reverse("phylogenic compute tree"))

    return render(request, "ngs/phylo.html", {'align': align_request}, locals())


def phylo_tree(request):
    tree_request = TreeForm(request.POST or None, request.FILES)
    if tree_request.is_valid():
        tree = Alignement()
        tree.mail = tree_request.cleaned_data['your_email']
        tree.file = tree_request.cleaned_data['file_field']
        tree.save()
        script = settings.BASE_DIR + '/ngs/simple_phylogeny.py'
        output = settings.MEDIA_ROOT + '/ngs/tree_result'
        tool = subprocess.Popen(['python', script, '--email', tree.mail, '--outfile', 'tree', tree.file.path],
                                close_fds=True, cwd=output)
        tool.communicate()
        tool.communicate()
        return HttpResponseRedirect(reverse("phylogenic visualization"))

    return render(request, "ngs/phylo_tree.html", {'tree': tree_request}, locals())


def phylo_visu(request):
    tree = settings.MEDIA_ROOT + 'ngs/tree_result/tree.tree.ph'
    itool = itolapi.Itol()
    itool.add_file(tree)
    itool.params['treeName'] = 'test_tree'
    status = itool.upload()
    assert status != False
    tree_link = itool.get_webpage()
    return render(request, "ngs/phylo_visu.html", {"tree": tree_link}, locals())
