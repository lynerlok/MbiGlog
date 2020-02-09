"""
ANDRÉ Charlotte
GALLARDO Jean Clément
LECOMTE Maxime
LAPORTE Antoine
MERCHADOU Kévin
GALLARDO Jean-Clément
"""

from django.shortcuts import render, redirect
from metabo.models import *
from .forms import NGSForm, GeneForm
from django.conf import settings
from pathlib import Path

from .models import Component, Pathway
from .scripts import correlation as co
import json


def home(request):
    return render(request, "metabo/home.html", locals())


# Function to upload a list of gene along with their expression
def upload_ngs_file(request):
    if request.method == 'POST':
        ngs_data_form = NGSForm(request.POST, request.FILES)
        if ngs_data_form.is_valid():
            file = ngs_data_form.cleaned_data['NGS_data']
            path = handle_binary_uploaded_file(file)
            data = co.reader(path.as_posix())
            dic = co.strToFloat(data)
            result_correlation = co.corrPearson(dic)
            correlDict = co.translateMatrix(result_correlation)
            output = co.meltDict(correlDict, 0.9)
            co.saveResult(output, "home/static/metabo/geneTMP.txt")
            output = json.dumps(output)
            return render(request, 'metabo/visualize.html', locals())
    else:
        ngs_data_form = NGSForm()

    if request.method == 'POST' and not ngs_data_form.is_valid():
        gene_data_form = GeneForm(request.POST, request.FILES)
        ngs_data = NGSForm()
        geneList = []
        if gene_data_form.is_valid():
            file = gene_data_form.cleaned_data['Gene_data']
            res = file.split(" ")
            return render(request, 'metabo/cytoscape.html', locals())
    else:
        gene_data_form = GeneForm()
    return render(request, 'metabo/ngs_input.html', locals())


def handle_binary_uploaded_file(f):
    tmp = Path(settings.MEDIA_ROOT) / "tmp.txt"
    with tmp.open('wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return tmp

    # geneList = ['AT5G52560', 'AT4G16130']
    # geneList = res


def graph(request):
    if request.method == 'POST':
        gene_data_form = GeneForm(request.POST, request.FILES)
        ngs_data = NGSForm()
        geneList = []
        if gene_data_form.is_valid():
            file = gene_data_form.cleaned_data['Gene_data']
            res = file.split(" ")

            json_net = {}
            geneList = res
            print(res)
            for i in geneList:
                gene, _ = Gene.objects.get_or_create(id_gene=i)
                gene.get_or_create_pathways()
                Metabolite.createMetabolites()
                pwy = Pathway.objects.filter(genes__id_gene=i)
                for p in pwy:
                    reactions = p.reactions.all()
                    genes = p.genes.all()
                    json_net[p.name] = {}
                    json_net[p.name]['Genes'] = []
                    for g in genes:
                        json_net[p.name]['Genes'].append(g.id_gene)
                    for r in reactions:
                        bilan = r.bilans.all()
                        json_net[p.name][r.name] = {}
                        enzyme = r.enzyme.all()
                        json_net[p.name][r.name]['enzyme'] = {}
                        if len(enzyme) > 0:
                            json_net[p.name][r.name]['enzyme']['name'] = enzyme[0].name
                            comp = Component.objects.filter(enzymes_id=enzyme[0].name)
                            if len(comp) > 0:
                                json_net[p.name][r.name]['enzyme']['component'] = comp[0].name
                        for met in bilan:
                            json_net[p.name][r.name]['reactif'] = met.reactif
                            json_net[p.name][r.name]['produit'] = met.produit
                            json_net[p.name][r.name]['cofactors'] = met.cofactors
            json_string2 = json.dumps(json_net)
            return render(request, 'metabo/cytoscape.html', locals())
        else:
            gene_data_form = GeneForm()
    return render(request, 'metabo/cytoscape.html', locals())


def visualize(request):
    return render(request, 'metabo/visualize.html', locals())
