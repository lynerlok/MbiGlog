"""
ANDRÉ Charlotte
GALLARDO Jean Clément
LECOMTE Maxime
LAPORTE Antoine
MERCHADOU Kévin
GALLARDO Jean-Clément
"""

from django.db import models
import xml.etree.ElementTree as ET
import requests
import re
import json


# Create your models here.


class Pathway(models.Model):
    """Build Pathway Table."""

    name = models.CharField(max_length=64)

    def save(self, *args, **kwargs):
        """
            overwrite save method.

        Parameters
        ----------
        *args : list
        **kwargs : dict

        """

        if Pathway.objects.filter(name=self.name).count() == 0:
            super(Pathway, self).save(*args, **kwargs)
            response = requests.get('https://websvc.biocyc.org/apixml',
                                    {'fn': 'genes-of-pathway', 'id': 'ARA:' + self.name})
            root = ET.fromstring(response.content)
            for element in root.iter('Gene'):
                if 'ID' in element.attrib:
                    gene, _ = Gene.objects.get_or_create(id_gene=re.sub(r'\-*', '', element.attrib['frameid']))
                    if self not in gene.pathways.all():
                        gene.pathways.add(self)


class Gene(models.Model):
    """Build Gene table."""
    id_gene = models.CharField(max_length=20,
                               primary_key=True)
    pathways = models.ManyToManyField(Pathway, related_name='genes')

    def get_or_create_pathways(self):
        """
            1. associate gene to pathway and reaction to pathway.
            2. associate metabolites to one reaction ( biocyc)
            3. create enzyme
        
        """
        responseBiocyc = requests.get('https://websvc.biocyc.org/apixml',
                                      {'fn': 'pathways-of-gene', 'id': 'ARA:' + self.id_gene})
        if responseBiocyc.status_code != 200:
            print("Gene not in Biocyc's database")
        else:
            root = ET.fromstring(responseBiocyc.content)
            if not Request.objects.filter(name=responseBiocyc.url).exists():
                for pathwayElement in root.findall('Pathway'):
                    pwy, _ = Pathway.objects.get_or_create(name=pathwayElement.attrib['frameid'])
                    pwy.save()
                    for reactionList in pathwayElement.findall('reaction-list'):
                        for reactionElement in reactionList.findall("Reaction"):
                            reaction, _ = Reaction.objects.get_or_create(name=reactionElement.attrib['frameid'])
                            reaction.save()
                            pwy.reactions.add(reaction)
                            reponseBiocycSubstrate = requests.get('https://websvc.biocyc.org/apixml',
                                                                  {'fn': 'substrates-of-reaction',
                                                                   'id': 'ARA:' + reaction.name})
                            rootSubstrates = ET.fromstring(reponseBiocycSubstrate.content)
                            rxn = ''
                            for substrate in rootSubstrates.findall('Compound'):
                                if 'CPD' in substrate.attrib['ID']:
                                    for cml in substrate.findall('cml'):
                                        for mol in cml.findall('molecule'):
                                            rxn += mol.attrib['title'] + ' '
                                elif (substrate.attrib['frameid'] == 'PROTON'):
                                    rxn += 'H+ '
                                elif (substrate.attrib['frameid'] == ('WATER')):
                                    rxn += 'H2O '
                                else:
                                    rxn += substrate.attrib['frameid'] + ' '
                            metabolite, _ = Metabolite.objects.get_or_create(ensemble=rxn)
                            reaction.metaboList.add(metabolite)
                        if self not in pwy.genes.all():
                            pwy.genes.add(self)
                request, _ = Request.objects.get_or_create(name=responseBiocyc.url)
                request.save()
                Enzyme.create_enzyme_metabolite()

    @staticmethod
    def gene_from_name(name, list):
        """  method to get name of gene.

        Parameters
        ----------
        name : string
            name of the enzymatic protein
        list : queryset
            List of severals dictionnary of id gene

        Returns
        -------
            name of each gene in queryset

        """
        for i in range(len(list)):
            if list[i].id_gene == name:
                return list[i]


class Enzyme(models.Model):
    """Build Enzyme table."""
    name = models.CharField(max_length=250, primary_key=True)
    gene = models.ForeignKey(Gene, related_name='enzymes', on_delete=models.CASCADE, null=True)

    @staticmethod
    def get_enzyme_names(liste):
        """ Method to get name of enzyme from the table Enzyme.

        Parameters
        ----------
        liste : list
            elements in the table Enzyme
            
        Returns
        -------
        type : 
            All the name of each enzyme

        """
        names = []
        for i in range(len(liste)):
            names.append(liste[i].name)
        return names

    @staticmethod
    def create_enzyme_metabolite():
        """
            1. Link enzyme to gene
            2. Link enzyme to reaction
            3. Link enzyme to compartment
        """
        for pwy in Pathway.objects.all():
            name = pwy.name
            genes = Gene.objects.filter(pathways__name=name)
            responseBiocyc = requests.get('https://websvc.biocyc.org/apixml',
                                          {'fn': 'enzymes-of-pathway', 'id': 'ARA:' + name, 'detail': 'full'})
            root = ET.fromstring(responseBiocyc.content)
            for protein in root.findall('Protein'):
                newname = re.sub(r'\-[A-Z]*', '', protein.attrib['frameid'])
                for db in protein.findall('dblink'):
                    for dbName in db.findall('dblink-db'):
                        if dbName.text == 'UNIPROT':
                            gene = Gene.gene_from_name(newname, genes)
                            if gene:
                                for entry in db.findall('dblink-oid'):
                                    response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                                                            {'accession': entry.text},
                                                            headers={"Accept": "application/json"})
                                    if response.status_code != 200:
                                        print('##########################  \n\n failed \n\n ##########################')
                                    else:
                                        protein = json.loads(response.text)

                                        if (len(protein) == 0):
                                            enzName = "unknown"
                                            met = "unknown"
                                            loc = "unknown"

                                        elif (len(protein) != 0):
                                            if 'recommendedName' not in protein[0]['protein']:
                                                enzName = protein[0]['protein']['submittedName'][0]['fullName']['value']
                                            else:
                                                enzName = protein[0]['protein']['recommendedName']['fullName']['value']
                                            enzymes = Enzyme.get_enzyme_names(Enzyme.objects.all())
                                            if enzName not in enzymes:
                                                enzyme = Enzyme(name=enzName)
                                                enzyme.save()
                                                if enzyme not in gene.enzymes.all():
                                                    gene.enzymes.add(enzyme)
                                                for r in root.iter('Reaction'):
                                                    reaction = Reaction.objects.filter(name=r.attrib['frameid'])
                                                    if len(reaction) == 0:
                                                        reaction, _ = Reaction.objects.get_or_create(
                                                            name=r.attrib['frameid'])
                                                        reaction.save()
                                                        enzyme.reactions.add(reaction)
                                                    else:
                                                        enzyme.reactions.add(reaction[0])
                                                    break

                                                for i in range(len(protein[0]["dbReferences"])):
                                                    if "properties" in protein[0]["dbReferences"][i]:
                                                        if "term" in protein[0]['dbReferences'][i]["properties"]:
                                                            if re.findall(r'C:[a-z]*\s*[a-z]*',
                                                                          protein[0]['dbReferences'][i]["properties"][
                                                                              "term"]):  ## works
                                                                location, _ = Component.objects.get_or_create(
                                                                    name=protein[0]['dbReferences'][i]["properties"][
                                                                        "term"])
                                                                if location not in Component.objects.all():
                                                                    location.save()
                                                                if location not in enzyme.componentName.all():
                                                                    enzyme.componentName.add(location)


class Reaction(models.Model):
    """ Build Reaction table."""
    name = models.TextField()
    pathway = models.ManyToManyField(Pathway, related_name='reactions')
    enzyme = models.ManyToManyField(Enzyme, related_name='reactions')


class Metabolite(models.Model):
    """Build Metabolite table."""
    ensemble = models.TextField()
    reaction = models.ManyToManyField(Reaction, related_name='metaboList')

    @staticmethod
    def createMetabolites():
        """ 
            Create metabolite from biocyc.
            Using intersection method to know which metabolites are in input and which are in output.
            Compare two reactions.
            Link metabolites to reaction
        """
        for pwy in Pathway.objects.all():
            reactions = pwy.reactions.all()
            metabolites = []
            for reaction in reactions:
                bilans = reaction.metaboList.all()
                metabolites.append(bilans)
            for i in range(len(metabolites)):
                try:
                    cof1 = ''
                    cof2 = ''
                    substrat1 = metabolites[i][0].ensemble.split(' ')
                    substrat1.pop()
                    substrat2 = metabolites[i + 1][0].ensemble.split(' ')
                    substrat2.pop()
                    ensemble1 = set(substrat1)
                    ensemble2 = set(substrat2)
                    for cof in substrat1:
                        if len(cof) < 4:
                            cof1 += cof + " "
                    for cof in substrat2:
                        if len(cof) < 4:
                            cof2 += cof + " "

                    bilan, _ = Bilan.objects.get_or_create(produit=str(ensemble1.intersection(ensemble2)),
                                                           reactif=str(ensemble1 - ensemble2.intersection(ensemble1)),
                                                           cofactors=cof1)

                    bilan2, _ = Bilan.objects.get_or_create(produit=str(ensemble2 - ensemble2.intersection(ensemble1)),
                                                            reactif=str(ensemble2.intersection(ensemble1)),
                                                            cofactors=cof2)

                    react = metabolites[i][0].reaction.all()
                    react2 = metabolites[i + 1][0].reaction.all()
                    if bilan not in Bilan.objects.all():
                        bilan.save()
                    if bilan not in react[0].bilans.all():
                        react[0].bilans.add(bilan)
                    if bilan2 not in Bilan.objects.all():
                        bilan2.save()
                    if bilan2 not in react2[0].bilans.all():
                        react2[0].bilans.add(bilan2)
                except:
                    if (i > 0):
                        cof1 = ''
                        cof2 = ''
                        substrat1 = metabolites[i - 1][0].ensemble.split(' ')
                        substrat1.pop()
                        substrat2 = metabolites[i][0].ensemble.split(' ')
                        substrat2.pop()

                        for cof in substrat1:
                            if len(cof) < 4:
                                cof1 += cof + " "
                                substrat1.remove(cof)
                        for cof in substrat2:
                            if len(cof) < 4:
                                cof2 += cof + " "
                                substrat2.remove(cof)
                        ensemble1 = set(substrat1)
                        ensemble2 = set(substrat2)
                        bilan2, _ = Bilan.objects.get_or_create(
                            produit=str(ensemble1 - ensemble2.intersection(ensemble1)),
                            reactif=str(ensemble2.intersection(ensemble1)), cofactors=cof2)
                        react2 = metabolites[i][0].reaction.all()
                        if bilan2 not in Bilan.objects.all():
                            bilan2.save()
                        if bilan2 not in react2[0].bilans.all():
                            react2[0].bilans.add(bilan2)


class Component(models.Model):
    """Build Component table"""
    name = models.CharField(max_length=50)
    enzymes = models.ForeignKey(Enzyme, related_name='componentName', on_delete=models.CASCADE, null=True)


class Request(models.Model):
    """Build Request table"""
    name = models.TextField()


class Bilan(models.Model):
    """Build Bilan table."""
    reactif = models.TextField()
    produit = models.TextField()
    cofactors = models.TextField()
    reaction = models.ManyToManyField(Reaction, related_name='bilans')
