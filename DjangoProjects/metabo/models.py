from django.db import models
import xml.etree.ElementTree as ET
import requests
import io
import re
import json


# Create your models here.


class Pathway(models.Model):
    name = models.CharField(max_length=64)

    # 'id':'ARA:PWY-82'

    def save(self, *args, **kwargs):
        if Pathway.objects.filter(name=self.name).count() == 0:
            super(Pathway, self).save(*args, **kwargs)
            response = requests.get('https://websvc.biocyc.org/apixml',
                                    {'fn': 'genes-of-pathway', 'id': 'ARA:' + self.name})
            root = ET.fromstring(response.content)
            for element in root.iter('Gene'):
                if 'ID' in element.attrib:
                    gene, _ = Gene.objects.get_or_create(id_gene=element.attrib['frameid'])

                    if self not in gene.pathways.all():
                        gene.pathways.add(self)


class Gene(models.Model):
    id_gene = models.CharField(max_length=20,
                               primary_key=True)  ## todo recupere common-name in  gene of pwy pour rentrer id uniprot
    pathways = models.ManyToManyField(Pathway, related_name='genes')

    def get_or_create_pathways(self):
        responseBiocyc = requests.get('https://websvc.biocyc.org/apixml',
                                {'fn': 'pathways-of-gene', 'id': 'ARA:' + self.id_gene})
        root = ET.fromstring(responseBiocyc.content)
        enzyme = Enzyme.get_or_create_enzyme(id_gene=self.id_gene)
        for pathwayElement in root.findall('Pathway'):
            pwy, _ = Pathway.objects.get_or_create(name=pathwayElement.attrib['frameid'])
            pwy.save()
            for reactionList in pathwayElement.findall('reaction-list'):
                for reactionElement in reactionList.findall("Reaction"):
                    reaction, _ = Reaction.objects.get_or_create(name=reactionElement.attrib['frameid'],enzyme=enzyme.name)
                    reaction.save()
                    pwy.reactions.add(reaction)
            if self not in pwy.genes.all():
                pwy.genes.add(self)


class Enzyme(models.Model):
    name = models.TextField()
    gene = models.ForeignKey(Gene, related_name='enzymes', on_delete=models.CASCADE, null=True)

    def get_or_create_enzyme(self, id_gene=''):
        response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                {'offset': '0', 'size': '1', 'gene': id_gene, 'organism': 'Arabidopsis thaliana',
                                 'taxid': '3702'}, headers={"Accept": "application/json"})
        protein = json.loads(response.text)
        met = protein[0]["comments"][1]["reaction"]['name']
        enzName = protein[0]['protein']['recommendedName']['fullName']['value']
        enzyme, _ = Enzyme.objects.get_or_create(name=enzName,
                                                  gene=Gene.objects.get(id_gene=id_gene))
        enzyme.save()
        return enzyme
        #met_without_equal = met.split("=")
        #reactant = met_without_equal[0].split(' + ')
        #product = met_without_equal[1].split(' + ')
        #reaction = enzyme.reactions.values(name)
        #print(reaction)


        # responseBody = response.text
        # enzN = re.findall(r'<fullName>[A-Z]+\-*\_*[a-z]*\s*[a-z]*', responseBody)
        # react = re.findall(r'<text>',responseBody)
        # for x in enzN:
        #     enzName, _ = Enzyme.objects.get_or_create(name=x.replace('<fullName>', ''),
        #                                               gene=Gene.objects.get(id_gene=id_gene))
        #     enzName.save()


class Reaction(models.Model):
    name = models.TextField()
    pathway = models.ManyToManyField(Pathway, related_name='reactions')
    enzyme = models.ForeignKey(Enzyme, related_name='reactions', on_delete=models.CASCADE, null=True)
    # pathways = models.ManyToManyField(Pathway,related_name='reactionName')

    # for metabolite in self.metabolite_set:   ## va chercher les metabolites pour 1 reaction

    # def save(self, *args, **kwargs):
    #    response = requests.get('https://websvc.biocyc.org/apixml',
    #                            {'fn': 'pathways-of-gene', 'id':Gene.id_gene})
    #    root = ET.fromstring(response.content)
    #    for element in root.iter('Reaction'):
    #        if 'ID' in element.attrib:
    #            pathway = Pathway.objects.get_or_create(name=element.attrib['ID'])
    #            if self not in pathway.reactionName:
    #                pathway.reactionName.add(self)
    #    super(Reaction, self).save(*args, **kwargs)


#
# class CoFactor(models.Model):
#     name = models.TextField()
#     enzymeCof = models.ManyToManyField(Enzyme, related_name='cofactors')
#
#     def save(self, *args, **kwargs):
#         response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
#                                 {'offset': '0', 'size': '100', 'gene': Gene.id_gene, 'organism': 'Arabidopsis thaliana',
#                                  'taxid': '3702'})
#         r = requests.get(response, headers={"Accept": "application/xml"})
#         responseBody = r.text
#         buf = io.StringIO(responseBody)
#         line = buf.readline()
#         cof = re.findall(r'<name>\w+\([0-9]*[\+|\-]\)', line)
#         for x in cof:
#             cofs = CoFactor.objects.get_or_create(cofactors=x.replace('<name>', ''))
#             if self not in cofs.cofactors:
#                 cofs.cofactors.add(self)
#         super(CoFactor, self).save(*args, **kwargs)


class Component(models.Model):
    name = models.CharField(max_length=50)
    pathways = models.ManyToManyField(Pathway, related_name='componentName')

    def save(self, *args, **kwargs):
        response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                {'offset': '0', 'size': '100', 'protein': 'Pyruvate Kinase',
                                 'organism': 'Arabidopsis thaliana',
                                 'taxid': '3702'})
        r = requests.get(response, headers={"Accept": "application/xml"})
        responseBody = r.text
        buf = io.StringIO(responseBody)
        line = buf.readline()
        loc = re.findall(r'C:[a-z]*\s*[a-z]*', line)
        location = []
        for x in loc:
            if x not in location:
                location = Component.objects.get_or_create(componentName=x)
            if self not in location.componentName:
                location.componentName.add(self)
        super(Component, self).save(*args, **kwargs)


class Metabolite(models.Model):
    # ARA:RXN-3
    name = models.CharField(max_length=50)
    reaction = models.ManyToManyField(Reaction, related_name='metaboList')
