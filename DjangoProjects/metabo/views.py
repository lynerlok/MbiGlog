from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from metabo.models import *
from .forms import NGSForm
from django.conf import settings
from pathlib import Path
from .scripts import correlation as co
import json


# Create your views here.
def home(request):
    # geneList = ['AT5G52560','AT4G16130']#'GQT-5255'
    # for i in geneList:
    #     gene, _ = Gene.objects.get_or_create(id_gene=i)
    #     gene.get_or_create_pathways()
    #     Enzyme.create_enzyme_metabolite()

    return render(request, "metabo/home.html", locals())


def upload_file(request):
    if request.method == 'POST':
        form = NGSForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['NGS_data']
            path = handle_uploaded_file(file)

            ###Traitement via le script python
            data = co.reader(path.as_posix())
            dic = co.strToFloat(data)
            result_correlation = co.corrPearson(dic)
            correlDict = co.translateMatrix(result_correlation)
            output = co.meltDict(correlDict, 0.9)
            # return redirect('mtb_graph')
            output = json.dumps(output)
            return render(request, 'metabo/graph.html', locals())
    else:
        form = NGSForm()
    return render(request, 'metabo/ngs.html', {'form': form})


def handle_uploaded_file(f):
    tmp = Path(settings.MEDIA_ROOT) / "tmp.txt"
    with tmp.open('wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return tmp


def graph(request):
    json_net = {}

    geneList = ['AT5G52560', 'AT4G16130']

    for i in geneList:
        gene, _ = Gene.objects.get_or_create(id_gene=i)
        gene.get_or_create_pathways()
        Metabolite.createMetabolites()

        pwy = Pathway.objects.filter(genes__id_gene=i)
        for p in pwy:
            reactions = p.reactions.all()
            genes=p.genes.all()
            json_net[p.name] = {}
            json_net[p.name]['Genes']=[]
            for g in genes:
                json_net[p.name]['Genes'].append(g.id_gene)
            for r in reactions:
                bilan = r.bilans.all()
                json_net[p.name][r.name] = {}
                enzyme = r.enzyme.all()


                json_net[p.name][r.name]['enzyme']={}
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
    return render(request, "metabo/graph.html", locals())
