from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(FastQ)
admin.site.register(FastQC)
admin.site.register(Genome)
admin.site.register(Alignement)
admin.site.register(Annotation)
admin.site.register(Request)
admin.site.register(Sequence)