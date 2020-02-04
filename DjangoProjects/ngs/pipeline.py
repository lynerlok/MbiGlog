from django.contrib import messages
import os
from django.conf import settings
import subprocess
from pathlib import Path

# Dictionnaire de stockage des paires fastq-origine/fastq-traités
dicofastq = {'fastq origine': ''}


# Fonction de lancement de l'outil fastq
def go_fastqc(fastq):
    rc=1
    while(rc != 0):
        fastqc = subprocess.Popen(fastq.archive + " | xargs -n1 -P2 fastqc $1",shell=True)
        fastqcstream=fastqc.communicate()[0]
        rc=fastqc.returncode
    if rc==0:
        return rc

# def get_html():
#     html=subprocess.Popen("ls")