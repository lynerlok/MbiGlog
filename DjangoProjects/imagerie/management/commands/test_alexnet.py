from django.core.management.base import BaseCommand
from django.db.models import Q

from imagerie.models import *


# from imagerie.tf_models.AlexNet import AlexNet


class Command(BaseCommand):
    args = '<directory_of_images_and_annotation_path>'
    help = 'our help string comes here'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.test()

    def test(self):
        natural = BackgroundType.objects.get(name='NaturalBackground')
        leaf = PlantOrgan.objects.get(name='Leaf')
        a, _ = AlexNet.objects.get_or_create(name="NL", specialized_background=natural, specialized_organ=leaf)
        images = GroundTruthImage.objects.filter(
            Q(specie__name='Olea europaea') | Q(specie__name='Phillyrea angustifolia'))
        a.train()
