from django.db import models
import xml.etree.ElementTree as ET
import requests
import io
import re


# Create your models here.


class Pathway(models.Model):
    # print('\n ------------------------------------ PATHWAY CLASS ----------------------------------- \n')
    name = models.CharField(max_length=64)

    # 'id':'ARA:PWY-82'

    def save(self, *args, **kwargs):
        if Pathway.objects.filter(name=self.name).count() == 0:
            super(Pathway, self).save(*args, **kwargs)
            response = requests.get('https://websvc.biocyc.org/apixml',
                                    {'fn': 'genes-of-pathway', 'id': 'ARA:'+self.name})
            root = ET.fromstring(response.content)
            for element in root.iter('Gene'):
                if 'ID' in element.attrib:
                    gene, _ = Gene.objects.get_or_create(id_gene=element.attrib['frameid'])

                    if self not in gene.pathways.all():
                        gene.pathways.add(self)



class Gene(models.Model):
    # print('\n ------------------------------------ GENE CLASS -------------------------------------- \n')

    id_gene = models.CharField(max_length=20, primary_key=True)  ## todo recupere common-name in  gene of pwy pour rentrer id uniprot
    pathways = models.ManyToManyField(Pathway, related_name='genes')


    def get_or_create_pathways(self):
        response = requests.get('https://websvc.biocyc.org/apixml',
                                {'fn': 'pathways-of-gene', 'id': 'ARA:' + self.id_gene})
        root = ET.fromstring(response.content)
        for element in root.iter('Pathway'):
            if 'ID' in element.attrib:
                pathway, _ = Pathway.objects.get_or_create(name=element.attrib['frameid'])
                pathway.save()
                if self not in pathway.genes.all():
                    pathway.genes.add(self)





class Enzyme(models.Model):
    # print('\n ------------------------------------ ENZYME CLASS ------------------------------------- \n')

    name = models.TextField()
    pathways = models.ManyToManyField(Pathway,related_name='enzymes')

    def save(self, *args, **kwargs):
        response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                {'offset': '0', 'size':'100','gene': Gene.id_gene,'organism':'Arabidopsis thaliana','taxid':'3702'})
        r = requests.get(response, headers={"Accept": "application/xml"})
        responseBody = r.text
        buf = io.StringIO(responseBody)
        line = buf.readline()
        enzN = re.findall(r'<fullName>[A-Z]+\-*\_*[a-z]*\s*[a-z]*', line)
        for x in enzN:
            enzName = Enzyme.objects.get_or_create(name=x.replace('<fullName>', ''))
            if self not in enzName.enzymes:
                enzName.enzymes.add(self)

        super(Enzyme, self).save(*args, **kwargs)



class Reaction(models.Model):
    # print('\n ------------------------------------ REACTION CLASS ----------------------------------- \n')

    name = models.TextField()
    pathways = models.ManyToManyField(Pathway,related_name='reactionName')

    # for metabolite in self.metabolite_set:   ## va chercher les metabolites pour 1 reaction


    def save(self, *args, **kwargs):
        response = requests.get('https://websvc.biocyc.org/apixml',
                                {'fn': 'pathways-of-gene', 'id':Gene.id_gene})
        root = ET.fromstring(response.content)
        for element in root.iter('Reaction'):
            if 'ID' in element.attrib:
                pathway = Pathway.objects.get_or_create(name=element.attrib['ID'])
                if self not in pathway.reactionName:
                    pathway.reactionName.add(self)
        super(Reaction, self).save(*args, **kwargs)

class CoFactor(models.Model):
    # print('\n ------------------------------------ COFACTOR CLASS ----------------------------------- \n')
    name = models.TextField()
    enzymeCof= models.ManyToManyField(Enzyme,related_name='cofactors')

    def save(self, *args, **kwargs):
        response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                {'offset': '0', 'size':'100','gene': Gene.id_gene,'organism':'Arabidopsis thaliana','taxid':'3702'})
        r = requests.get(response, headers={"Accept": "application/xml"})
        responseBody = r.text
        buf = io.StringIO(responseBody)
        line = buf.readline()
        cof = re.findall(r'<name>\w+\([0-9]*[\+|\-]\)', line)
        for x in cof:
            cofs =CoFactor.objects.get_or_create(cofactors=x.replace('<name>', ''))
            if self not in cofs.cofactors:
               cofs.cofactors.add(self)
        super(CoFactor, self).save(*args, **kwargs)




class Component(models.Model):
    # print('\n ------------------------------------ COMPONENT CLASS ---------------------------------- \n')
    name = models.CharField(max_length=50)
    pathways = models.ManyToManyField(Pathway,related_name='componentName')

    def save(self, *args, **kwargs):
        response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                {'offset': '0', 'size': '100', 'protein': 'Pyruvate Kinase', 'organism': 'Arabidopsis thaliana',
                                 'taxid': '3702'})
        r = requests.get(response, headers={"Accept": "application/xml"})
        responseBody = r.text
        buf = io.StringIO(responseBody)
        line = buf.readline()
        loc = re.findall(r'C:[a-z]*\s*[a-z]*', line)
        location = []
        for x in loc:
            if x not in location:
                location=Component.objects.get_or_create(componentName=x)
            if self not in location.componentName:
                location.componentName.add(self)
        super(Component, self).save(*args, **kwargs)

class Metabolite(models.Model):
    # print('\n ------------------------------------ METABOLITE CLASS --------------------------------- \n')
    #ARA:RXN-3
    name = models.CharField(max_length=50)
    reaction = models.ManyToManyField(Reaction, related_name='metaboList')

    def save(self, *args, **kwargs):
        response = requests.get('https://websvc.biocyc.org/apixml', {'fn': 'substrates-of-reaction', 'id': self.name})
        root = ET.fromstring(response.content)
        subsR = []
        subsReact = []
        for element in root.iter('common-name'):
            subsR.append(element.text)
        for e in subsR:
            subsReact = Metabolite.objects.get_or_create(metaboList=re.sub(r'\&|\;|<SUP>|</SUP>', '', e))
            if self not in subsReact.metaboList:
                subsReact.metaboList.add(self)
        super(Metabolite, self).save(*args, **kwargs)
