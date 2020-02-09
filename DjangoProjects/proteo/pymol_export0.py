#launch : python pymol_export_dl.py chemin/fichier.pdb

#sudo apt-get install pymol

#!/usr/bin/python
import __main__
__main__.pymol_argv = [ 'pymol', '-qc'] # Quiet and no GUI

import sys, time, os
import pymol

pymol.finish_launching()

##
# Read User Input
spath = os.path.abspath(sys.argv[1])
sname = spath.split('/')[-1].split('.')[0]

# Load Structures

pymol.cmd.load(spath, sname) 
pymol.cmd.disable("all")
pymol.cmd.enable(sname)
pymol.cmd.show("cartoon")
pymol.cmd.png(sname+".png")
pymol.cmd.save(sname+'.obj',selection='(all)',state=-1,format='obj')

# Get out!
pymol.cmd.quit()
