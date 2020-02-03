from django.test import TestCase
from .models import *
# Create your tests here.


class AnimalTestCase(TestCase):

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        geneList = ['AT5G52560','AT4G16130']#'GQT-5255'
        for i in geneList:
            gene, _ = Gene.objects.get_or_create(id_gene=i)
            gene.get_or_create_pathways()
            Enzyme.create_enzyme_metabolite()