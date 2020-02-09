#requiert le module wget (pip3 install wget / pip install wget)
# coding: utf-8

import sys
#import wget
import os

id_pdb = sys.argv[1]

def runpsipred(id_pdb): #lance psipred via le fichier .fasta
    print("Running PSIPRED.....")
    return os.system("tcsh /media/Datas/Proteo/psipred/BLAST+/runpsipredplus /media/Datas/Poteo/psipred/data/"+id_pdb+".fasta")
runpsipred(id_pdb)
