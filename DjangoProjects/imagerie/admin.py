from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Image)
admin.site.register(SubmittedImage)
admin.site.register(GroundTruthImage)
admin.site.register(TypeImage)
admin.site.register(ContentImage)
admin.site.register(Specie)
admin.site.register(Taxon)
admin.site.register(RankTaxon)
admin.site.register(CNNArchitecture)
admin.site.register(CNN)
