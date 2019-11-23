from pathlib import Path
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand

from imagerie.models import *


class Command(BaseCommand):
    args = '<directory_of_images_and_annotation_path>'
    help = 'our help string comes here'
    taxon_names = ["Regnum", 'Class', 'Subclass', 'Superorder', 'Order', 'Family', 'Genus', 'Species']
    taxon_ranks = [RankTaxon.objects.get_or_create(name=name) for name in taxon_names]

    def add_arguments(self, parser):
        parser.add_argument('dir_path')

    def _get_or_create_taxon(self, taxons, pos=0, previous=None):
        if pos == 7:
            return previous
        taxon = taxons.find(self.taxon_names[pos]).text
        if taxon:
            taxon, _ = Taxon.objects.get_or_create(rank=self.taxon_ranks[pos], name=taxon, sup_taxon=previous)
            return self._get_or_create_taxon(taxons, pos + 1, previous=taxon)
        else:
            return previous

    def _populate_db(self, dir_path):
        for file_path in Path(dir_path).iterdir():
            if file_path.suffix == ".xml":
                image = file_path.name.replace('xml', 'jpg')
                annot_path = file_path.absolute().as_posix()
                image_path = file_path.absolute().as_posix().replace('xml', 'jpg')

                xml = ET.parse(annot_path)
                root = xml.getroot()
                typeImage, _ = TypeImage.objects.get_or_create(name=root.find('Type').text)
                content, _ = ContentImage.objects.get_or_create(name=root.find('Content').text)
                taxons = root.find('Taxon')
                genus = self._get_or_create_taxon(taxons, pos=0, previous=None)
                specie, _ = Specie.objects.get_or_create(rank=self.taxon_ranks[7], name=root.find('ClassId').text,
                                                         sup_taxon=genus,
                                                         vernacular_name=root.find('VernacularNames').text,
                                                         latin_name=root.find('ClassId').text)

                gtimage, _ = GroundTruthImage.objects.get_or_create(specie=specie, content=content, type=typeImage,
                                                                    image=image_path)
                print(image, 'saved')

    def handle(self, *args, **options):
        self._populate_db(options["dir_path"])
