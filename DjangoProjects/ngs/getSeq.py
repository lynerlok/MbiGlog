#!/usr/bin/env python
import os, sys, glob
from Bio import SeqIO, Entrez


def getFasta(input_id):

    try:
        print("Parsing...\t"+input_id)
        seqfile=Entrez.efetch(email="example@email.com",db="nucleotide",id=input_id,retmode="text",rettype="gb")
        gb_record=SeqIO.read(seqfile,"genbank")
        SeqIO.write(gb_record,input_id+".fasta","fasta")
    except Exception as exError:
        print("Error: Problem encountered while downloading files...")
        sys.exit()


getFasta(sys.argv[1])