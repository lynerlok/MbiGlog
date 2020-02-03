from django.db import models
from django.contrib import messages
import subprocess
from django.conf import settings
from os.path import join
from pathlib import Path


class Request(models.Model):
    date = models.DateTimeField(auto_now_add=True)


class FastQ(models.Model):
    archive = models.FileField(upload_to='ngs/fastq/')
    request = models.ForeignKey(Request, on_delete=models.CASCADE)

    def generate_fastqc(self):
        rc = 1
        fastqc = subprocess.Popen("xargs -n1 -P2 fastqc" + self.archive.path + " -o " + FastQC.dir.as_posix(), shell=True)
        while (rc != 0):
            fastqcstream = fastqc.communicate()[0]
            rc = fastqc.returncode

        fastqc_name = Path(self.archive.path).name.split('.')[0] + '_fastqc.html'
        fastqc = FastQC(fastq=self, file=FastQC.dir / fastqc_name)
        fastqc.save()
        return fastqc


class FastQC(models.Model):
    dir = Path(settings.MEDIA_ROOT) / 'ngs' / 'fastqc'
    fastq = models.ForeignKey(FastQ, on_delete=models.CASCADE)
    file = models.FileField(upload_to='ngs/fastqc/')
