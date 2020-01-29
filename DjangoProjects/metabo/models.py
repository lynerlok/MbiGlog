from django.db import models
import xml.etree.ElementTree as ET
import requests
import io
import re
import json

# Create your models here.


class Pathway(models.Model):
    name = models.CharField(max_length=64)

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
                               primary_key=True)
    pathways = models.ManyToManyField(Pathway, related_name='genes')

    def get_or_create_pathways(self):
        responseBiocyc = requests.get('https://websvc.biocyc.org/apixml',
                                      {'fn': 'pathways-of-gene', 'id': 'ARA:' + self.id_gene})
        root = ET.fromstring(responseBiocyc.content)
        #enzyme = Enzyme.get_or_create_enzyme(id_gene=self.id_gene)
       # met = Reaction.get_or_create_metabo(id_gene=self.id_gene)
        for pathwayElement in root.findall('Pathway'):
            pwy, _ = Pathway.objects.get_or_create(name=pathwayElement.attrib['frameid'])
            pwy.save()
            for reactionList in pathwayElement.findall('reaction-list'):
                for reactionElement in reactionList.findall("Reaction"):
                    reaction, _ = Reaction.objects.get_or_create(name=reactionElement.attrib['frameid'], enzyme=None)
                    reaction.save()
                    pwy.reactions.add(reaction)
            if self not in pwy.genes.all():
                pwy.genes.add(self)

class Enzyme(models.Model):
    name = models.TextField()
    gene = models.ForeignKey(Gene, related_name='enzymes', on_delete=models.CASCADE, null=True)

    #print(Gene.objects.filter(pathways__name="PWY-82"))
    #print(Reaction.objects.filter(pathway__name="PWY-82"))
    def create_enzyme_metabolite(self):
        for pwy in Pathway.objects.all():
            #On parcourt les pwy
            #Requete Uniprot
            #Vérification du gène -> Vérification ID uniprot -> requête Uniprot -> association de l'enzyme au gène
            #Vérification de la réaction -> association des métabolites à la réaction
            name = pwy.name
            genes = Gene.objects.filter(pathways__name = name)
            reactions = Reaction.objects.filter(pathway__name = name)
            responseBiocyc = requests.get('https://websvc.biocyc.org/apixml',
                                      {'fn': 'enzymes-of-pathway', 'id': 'ARA:' + name, 'detail':'full'})
            root = ET.fromstring(responseBiocyc.content)


            for protein in root.findall('Protein'):
                newname = re.sub(r'\-[A-Z]*','',protein.attrib['frameid'])
                goodGene = Gene.objects.filter(id_gene = newname)


                for db in protein.findall('dblink'):
                    for dbName in db.findall('dblink-db'):
                        if dbName.text == 'UNIPROT':
                            for entry in db.findall('dblink-oid'):
                                response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',{'accession' : entry.text}, headers={"Accept": "application/json"})
                                protein = json.loads(response.text)
                                if (len(protein) == 0):
                                    enzName = "unknown"
                                    met = "unknown"
                                    loc = "unknown"
                                elif(len(protein) != 0):
                                    for i in range(len(protein[0]["dbReferences"])):
                                        if ("properties" in protein[0]["dbReferences"][i]):
                                            if ("term" in protein[0]['dbReferences'][i]["properties"]):
                                                if(re.findall(r'C:[a-z]*\s*[a-z]*',protein[0]['dbReferences'][i]["properties"]["term"])):   ## works
                                                    print(protein[0]['dbReferences'][i]["properties"]["term"])

                                        else:
                                            loc = "unknow"
                                    if ('recommendedName' not in protein[0]['protein']):
                                        enzName = protein[0]['protein']['submittedName'][0]['fullName']['value']
                                    else:
                                        enzName = protein[0]['protein']['recommendedName']['fullName']['value']
                                    enzyme = Enzyme(name=enzName)
                                    if (enzyme not in Enzyme.objects.all()):
                                        enzyme.save()
                                    for i in range(len(genes)):
                                        if enzyme not in genes[i].enzymes.all():
                                            genes[i].enzymes.add(enzyme)
                                    if ('comments' not in protein[0]):
                                        met = 'unknown'
                                    else:
                                        if ("reaction" not in protein[0]["comments"]):
                                            met = "unknown"
                                        else:
                                            met = protein[0]["comments"][1]["reaction"]['name']
                                            # met_without_equal = met.split("=")
                                            # react = met_without_equal[0].split(' + ')
                                            # prod = met_without_equal[1].split(' + ')
                                        metabolite, _ = Metabolite.objects.get_or_create(ensemble=met,)
                                        if metabolite not in Metabolite.objects.all():
                                            metabolite.save()
                                        for i in range(len(reactions)):
                                            if metabolite not in reactions[i].metaboList.all():
                                                reactions[i].metaboList.add(metabolite)




                '''if newname in genes:
                    """requette unirpot """
            for enzymeElement in root.findall('Reaction'):
                if enzymeElement.attrib['frameid'] in reactions:
                    """ requete unirpot """'''

            '''
            for g in range(len(genes)):
                response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                        {'offset': '0', 'size': '1', 'gene': genes[g].id_gene, 'organism': 'Arabidopsis thaliana',
                                         'taxid': '3702'}, headers={"Accept": "application/json"})
                if response.status_code != 200:
                    print('failed')
                else:
                    protein = json.loads(response.text)
                    if 'recommendedName' not in protein[0]['protein']:
                        enzName = protein[0]['protein']['submittedName'][0]['fullName']['value']
                    else:
                        enzName = protein[0]['protein']['recommendedName']['fullName']['value']
                    enzyme = Enzyme(name=enzName)
                    if enzyme not in Enzyme.objects.all():
                        enzyme.save()
                    if enzyme not in genes[g].enzymes.all():
                        genes[g].enzymes.add(enzyme)
                    if 'comments' not in protein[0]:
                        met = 'unknown'
                    else:
                        met = protein[0]["comments"][1]["reaction"]['name']
                        met_without_equal = met.split("=")
                        react = met_without_equal[0].split(' + ')
                        prod = met_without_equal[1].split(' + ')
                    metabolite, _ = Metabolite.objects.get_or_create(ensemble=met)
                    if metabolite not in Metabolite.objects.all():
                        metabolite.save()
                    if metabolite not in reactions[g].metaboList.all():
                        reactions[g].metaboList.add(metabolite)
                        '''


    # met_without_equal = met.split("=")
    # reactant = met_without_equal[0].split(' + ')
    # product = met_without_equal[1].split(' + ')
    # reaction = enzyme.reactions.values(name)
    # print(reaction)

    # responseBody = response.text
    # enzN = re.findall(r'<fullName>[A-Z]+\-*\_*[a-z]*\s*[a-z]*', responseBody)
    # react = re.findall(r'<text>',responseBody)
    # for x in enzN:
    #     enzName, _ = Enzyme.objects.get_or_create(name=x.replace('<fullName>', ''),
    #                                               gene=Gene.objects.get(id_gene=id_gene))
    #     enzName.save()
    @staticmethod
    def get_or_create_enzyme(id_gene=''):
        response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                {'offset': '0', 'size': '1', 'gene': id_gene, 'organism': 'Arabidopsis thaliana',
                                 'taxid': '3702'}, headers={"Accept": "application/json"})
        protein = json.loads(response.text)
        enzName = protein[0]['protein']['recommendedName']['fullName']['value']
        enzyme, _ = Enzyme.objects.get_or_create(name=enzName,
                                                 gene=Gene.objects.get(id_gene=id_gene))
        enzyme.save()
        #Component.searchComponent(enzName)
        return enzyme


class Reaction(models.Model):
    name = models.TextField()
    pathway = models.ManyToManyField(Pathway, related_name='reactions')
    enzyme = models.ForeignKey(Enzyme, related_name='reactions', on_delete=models.CASCADE, null=True)

    # @staticmethod
    # def get_or_create_metabo(id_gene=''):
    #     response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
    #                             {'offset': '0', 'size': '1', 'gene': id_gene, 'organism': 'Arabidopsis thaliana',
    #                              'taxid': '3702'}, headers={"Accept": "application/json"})
    #     protein = json.loads(response.text)
    #     met = protein[0]["comments"][1]["reaction"]['name']
    #     met_without_equal = met.split("=")
    #     react = met_without_equal[0].split(' + ')
    #     prod = met_without_equal[1].split(' + ')
    #     metabolite, _ = Metabolite.objects.get_or_create(ensemble=met, reaction=Reaction.name)
    #     print(metabolite.ensemble)
    #     metabolite.save()
        # reaction = enzyme.reactions.values(name)
        # print(reaction)

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


class Metabolite(models.Model):
    # ARA:RXN-3
    reactant = models.CharField(max_length=50)
    product = models.CharField(max_length=50)
    ensemble = models.TextField()
    reaction = models.ManyToManyField(Reaction, related_name='metaboList')

    # @staticmethod
    # def get_or_create_metabo(protein,name=''):
    #     met = protein[0]["comments"][1]["reaction"]['name']
    #     met_without_equal = met.split("=")
    #     react = met_without_equal[0].split(' + ')
    #     prod = met_without_equal[1].split(' + ')
    #     metabolite, _ = Metabolite.objects.get_or_create(reactant=react,
    #                                                      product=prod)
    #     # metabolite.save()
    #     return metabolite
    #     # reaction = enzyme.reactions.values(name)
    #     # print(reaction)


class Component(models.Model):
    name = models.CharField(max_length=50)
    pathways = models.ManyToManyField(Pathway, related_name='componentName')

    @staticmethod
    def searchComponent(nameE=''):
        response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                {'offset': '0', 'size': '100', 'protein': nameE,
                                 'organism': 'Arabidopsis thaliana',
                                 'taxid': '3702'}, headers={"Accept": "application/json"})
        comp = json.loads(response.text)
        loc = re.findall(r'C:[a-z]*\s*[a-z]*',comp[0]['dbReferences'])
        print('loc',loc)
        # print(comp[0]['dbReferences'][32]['properties']['term'])  #### working
        # print(len(comp[0]['dbReferences']))
        # print(comp[0]['dbReferences'][32]['properties'])
        # res = []
        # for i in range(len(comp[0]['dbReferences'])):
        #     if 'term' not in comp[0]['dbReferences'][i]['properties']:
        #         print('nope')
        #     if 'term' in comp[0]['dbReferences'][i]['properties']:
        #         print('yes')
        #         if len(comp[0]['dbReferences'][i]['properties']['term']) != 0:
        #             res.append(comp[0]['dbReferences'][32]['properties']['term'])
        # print(res)


        # buf = io.StringIO(responseBody)
        # line = buf.readline()
        # loc = re.findall(r'C:[a-z]*\s*[a-z]*', line)
        # location = []
        # for x in loc:
        #     if x not in location:
        #         location = Component.objects.get_or_create(componentName=x)
        #     if self not in location.componentName.all():
        #         location.componentName.add(self)

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
