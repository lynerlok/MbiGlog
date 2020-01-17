from django.db import models
import xml.etree.ElementTree as ET
import requests

# Create your models here.


class Pathway(models.Model):
    name = models.CharField(max_length=64)
    geneList = models.TextField()
    enzyList = models.TextField()



class Gene(models.Model):
    id_gene = models.CharField(max_length=20) ## todo recupere common-name in  gene of pwy pour rentrer id uniprot
    gene = models.ManyToManyField(Pathway)

    response = requests.get('https://websvc.biocyc.org/apixml',
                            {'fn': 'genes-of-pathway', 'id':'ARA:PWY-82'})
    root = ET.fromstring(response.content)

    for element in root.iter('Gene'):
        if 'ID' in element.attrib:
            print(element.attrib['frameid'])

class Enzyme(models.Model):
    name = models.TextField()
    cofactor_in = models.TextField()
    cofactor_out = models.TextField()




class Reaction(models.Model):
    name = models.TextField()

    # for metabolite in self.metabolite_set:   ## va chercher les metabolites pour 1 reaction


    # def request_from_biocyc(self):            pathways-of-gene
    #     response = requests.get('https://websvc.biocyc.org/apixml',
    #                             {'fn': 'pathways-of-gene', 'id': 'ARA:AT5G52560'})
    #     root = ET.fromstring(response.content)
    #
    #     for element in root.iter('Reaction'):
    #         print(element.attrib['frameid'])
    #     return render(request, "metabo/home.html", locals())




class Metabolite(models.Model):
    name = models.CharField(max_length=50)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE) ## todo manytomany
    #
    # def metabo(self):
    #     response = requests.get('https://websvc.biocyc.org/apixml', {'fn': 'substrates-of-reaction', 'id': 'ARA:RXN-3'})
    #     root = ET.fromstring(response.content)

    #     for element in root.iter('common-name'):
    #         print(element.text)


