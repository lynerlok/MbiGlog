from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from imagerie.models import *
import os
import xml.etree.ElementTree as ET


class Command(BaseCommand):
    args = '<directory_of_images_and_annotation_path>'
    help = 'our help string comes here'

    def add_arguments(self, parser):
        parser.add_argument('dir_path')

    def _populate_db(self, dir_path):
        REGNUM, _ = RankTaxon.objects.get_or_create(name='Regnum')
        CLASS, _ = RankTaxon.objects.get_or_create(name='Class')
        SUBCLASS, _ = RankTaxon.objects.get_or_create(name='Subclass')
        SUPERORDER, _ = RankTaxon.objects.get_or_create(name='Superorder')
        ORDER, _ = RankTaxon.objects.get_or_create(name='Order')
        FAMILY, _ = RankTaxon.objects.get_or_create(name='Family')
        GENUS, _ = RankTaxon.objects.get_or_create(name='Genus')
        SPECIES, _ = RankTaxon.objects.get_or_create(name='Species')
        try:
            i = 0
            while True:
                image = f'{i}.jpg'
                annot_path = os.path.join(dir_path, f'{i}.xml')
                image_path = os.path.join(dir_path, image)

                xml = ET.parse(annot_path)
                root = xml.getroot()
                typeImage, _ = TypeImage.objects.get_or_create(name=root.find('Type').text)
                content, _ = ContentImage.objects.get_or_create(name=root.find('Content').text)
                taxons = root.find('Taxon')
                regnum, _ = Taxon.objects.get_or_create(rank=REGNUM, name=taxons.find('Regnum').text, sup_taxon=None)
                class_, _ = Taxon.objects.get_or_create(rank=CLASS, name=taxons.find('Class').text,
                                                        sup_taxon=regnum)
                subclass, _ = Taxon.objects.get_or_create(rank=SUBCLASS, name=taxons.find('Subclass').text,
                                                          sup_taxon=class_)
                superorder, _ = Taxon.objects.get_or_create(rank=SUPERORDER, name=taxons.find('Superorder').text,
                                                            sup_taxon=subclass)
                order, _ = Taxon.objects.get_or_create(rank=ORDER, name=taxons.find('Order').text,
                                                       sup_taxon=superorder)
                family, _ = Taxon.objects.get_or_create(rank=FAMILY, name=taxons.find('Family').text, sup_taxon=order)
                genus, _ = Taxon.objects.get_or_create(rank=GENUS, name=taxons.find('Genus').text, sup_taxon=family)
                specie, _ = Specie.objects.get_or_create(rank=SPECIES, name=taxons.find('Species').text,
                                                         sup_taxon=genus,
                                                         vernacular_name=root.find('VernacularNames').text,
                                                         latin_name=root.find('ClassId').text)
                gtimage = GroundTruthImage(specie=specie, content=content, type=typeImage)
                with open(image_path, 'rb') as f:
                    data = f.read()
                gtimage.image.save(image, ContentFile(data))
                gtimage.save()
                print(image, 'saved')
                i += 1

        except FileNotFoundError:
            pass

    def handle(self, *args, **options):
        self._populate_db(options["dir_path"])