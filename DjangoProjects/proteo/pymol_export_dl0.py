#launch : python pymol_export_dl.py idPDB

#sudo apt-get install pymol

#!/usr/bin/python
import __main__
__main__.pymol_argv = [ 'pymol', '-qc'] # Quiet and no GUI

import sys, time, os
import pymol

pymol.finish_launching()

##
# Read User Input
sfile = sys.argv[1]

# Load Structures

pymol.cmd.fetch(sfile,name=sfile,type='pdb',async=0,path=None)
pymol.cmd.disable("all")
pymol.cmd.enable(sfile)
pymol.cmd.show("cartoon")
pymol.cmd.png(sfile+'.png')
pymol.cmd.save(sfile+'.obj',selection='(all)',state=-1,format='obj')

# Get out!
pymol.cmd.quit()
