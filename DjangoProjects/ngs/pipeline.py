from django.contrib import messages
import os
from django.conf import settings
import subprocess

# Dictionnaire de stockage des paires fastq-origine/fastq-traités
dicofastq = {'fastq origine': ''}


# Fonction de lancement de l'outil fastq
def go_fastqc():
    os.system('cd '+ settings.MEDIA_ROOT + ' | pwd | echo $pwd')
    # os.system('cd ' + settings.MEDIA_ROOT + ' | ls *.fastq.gz | xargs -n1 -P2 fastqc $1')
