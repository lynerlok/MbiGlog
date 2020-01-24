from django.shortcuts import render
from metabo.models import *


# Create your views here.
def home(request):
    geneList = ['AT5G52560','AT4G16130']#'GQT-5255'
    for i in geneList:
        gene, _ = Gene.objects.get_or_create(id_gene=i)
        gene.get_or_create_pathways()
        #enz = Enzyme()
        #enz.get_or_create_enzyme(id_gene=gene.id_gene)
    return render(request, "metabo/home.html", locals())
