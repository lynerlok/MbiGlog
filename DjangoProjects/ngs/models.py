from django.db import models
from django.contrib import messages
import subprocess
from django.conf import settings
from os.path import join
from pathlib import Path
import subprocess
import os.path


class Request(models.Model):
    date = models.DateTimeField(auto_now_add=True)

class Genome(models.Model):
    dir = Path(settings.MEDIA_ROOT) / 'ngs' / 'genome/'
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    file = models.FileField(upload_to='ngs/genome')

    def __str__(self):
        return self.file.name

class Annotation(models.Model):
    dir = Path(settings.MEDIA_ROOT) / 'ngs' / 'annotations/'
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    file = models.FileField(upload_to='ngs/annotations')

class FastQ(models.Model):
    archive = models.FileField(upload_to='ngs/fastq/')
    request = models.ForeignKey(Request, on_delete=models.CASCADE)

    def generate_fastqc(self):
        rc = 1
        while (rc != 0):
            if os.path.isdir(FastQC.dir.as_posix())==False:
                process = subprocess.Popen("mkdir "+FastQC.dir.as_posix(), shell=True)
                process.communicate()
            fastqc_process = subprocess.Popen("fastqc " + self.archive.path + " -o " + FastQC.dir.as_posix(), shell=True)
            fastqcstream = fastqc_process.communicate()[0]
            rc = fastqc_process.returncode
        fastqc_name = Path(self.archive.path).name.split('.')[0] + '_fastqc.html'
        fastqc = FastQC(fastq=self, file=(FastQC.dir / fastqc_name).as_posix())
        fastqc.save()
        return fastqc


class FastQC(models.Model):
    dir = Path(settings.MEDIA_ROOT) / 'ngs' / 'fastqc/'
    fastq = models.ForeignKey(FastQ, on_delete=models.CASCADE)
    file = models.FileField(upload_to='ngs/fastqc/')


class Sequence(models.Model):
    file = models.FileField(upload_to='ngs/fasta')
    mail = models.EmailField(max_length=255)

    def __str__(self):
        return self.file.name


class Alignement(models.Model):
    file = models.FileField(upload_to='ngs/tree')
    mail = models.EmailField(max_length=255)

    def __str__(self):
        return self.file.name

class Sequence_fasta(models.Model):
    nomGene = models.CharField(max_length=255)
    sequence = models.TextField()
    nomEspece = models.CharField(max_length=255)

class User(models.Model):
    mail = models.EmailField().unique

class Alignement_result(models.Model):
    value = models.TextField()
    algo = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Sequences = models.ManyToManyField(Sequence_fasta, related_name="Alignements", blank=True)



class Arbre(models.Model):
    newick = models.TextField()
    alignement = models.OneToOneField(Alignement_result,on_delete=models.CASCADE)
