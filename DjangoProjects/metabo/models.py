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
    # gene = models.ManyToManyField(Pathway)
    #
    # response = requests.get('https://websvc.biocyc.org/apixml',
    #                         {'fn': 'genes-of-pathway', 'id':'ARA:PWY-82'})
    # root = ET.fromstring(response.content)
    #
    # for element in root.iter('Gene'):
    #     if 'ID' in element.attrib:
    #         print(element.attrib['frameid'])

class Enzyme(models.Model):
    name = models.TextField()
    # cofactor_in = models.ManyToManyField(CoFactor)
    # cofactor_out = models.ManyToManyField(CoFactor)
    # requestURL = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=100&gene=AT5G52560&organism=Arabidopsis%20thaliana&taxid=3702"
    # r = requests.get(requestURL, headers={"Accept": "application/xml"})
    # responseBody = r.text
    # buf = io.StringIO(responseBody)
    # line = buf.readline()
    # cofactors = re.findall(r'<name>\w+\([0-9]*[\+|\-]\)',line)
    # enzName = re.findall(r'<fullName>[A-Z]+\-*\_*[a-z]*\s*[a-z]*',line)
    # print(enzName)
    # print(cofactors)

class CoFactor(models.Model):
    # cofactor_in = models.TextField()
    # cofactor_out = models.TextField()
    pass



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


class Component(models.Model):
    name = models.CharField(max_length=50)
    # pwyList = models.ManyToManyField(Pathway)
    # requestURL = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=100&protein=Pyruvate%20kinase&taxid=3702"
    # r = requests.get(requestURL, headers={"Accept": "application/xml"})
    # responseBody = r.text
    # buf = io.StringIO(responseBody)
    # line = buf.readline()
    # location = re.findall(r'C:[a-z]*\s*[a-z]*',line)
    # pathway = re.findall(r'\"UniPathway\"\s*id=\"UPA00109\"',line)
    # print(location)
    # print(pathway)

class Metabolite(models.Model):
    name = models.CharField(max_length=50)
    # reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE) ## todo manytomany
    # #
    # def metabo(self):
    #     response = requests.get('https://websvc.biocyc.org/apixml', {'fn': 'substrates-of-reaction', 'id': 'ARA:RXN-3'})
    #     root = ET.fromstring(response.content)

    #     for element in root.iter('common-name'):
    #         print(element.text)


