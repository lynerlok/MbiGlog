from datetime import timedelta
from django.utils.timezone import now
from django.core.management.base import BaseCommand

from imagerie.models import *


class Command(BaseCommand):
    args = '<directory_of_images_and_annotation_path>'
    help = 'our help string comes here'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print(len(Request.objects.all()))
        Request.objects.filter(date__lt=now() - timedelta(minutes=5)).delete()
        print(len(Request.objects.all()))

