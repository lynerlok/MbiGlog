from django.core.management.base import BaseCommand

from imagerie.models import *


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.test()

    def test(self):
        background = BackgroundType.objects.get(name='SheetAsBackground')
        organ = PlantOrgan.objects.get(name='Leaf')
        a, _ = AlexNet.objects.get_or_create(name="SL", specialized_background=background, specialized_organ=organ)
        a.train()
        background = BackgroundType.objects.get(name='NaturalBackground')
        for organ in PlantOrgan.objects.all():
            a, _ = AlexNet.objects.get_or_create(name=f"N{organ.name}", specialized_background=background,
                                                 specialized_organ=organ)
            try:
                a.train(nb_image_by_class=5)
            except:
                pass