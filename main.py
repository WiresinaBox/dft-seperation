import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import nwchem_parse as nwparse


#A space for scratchwork for calling other modules

parser = argparse.ArgumentParser()
parser.add_argument('filepath', nargs = '+')
args = parser.parse_args()

fnList = args.filepath #nargs=+ returns a list of at least one.
parserList = []

for fn in fnList:
    p = nwparse.nwchem_parser(fn)
    parserList.append(p)
    
fig, ax = plt.subplots(1,1)
for p in parserList:
    #print(p.get_orbital_dict())
    orbitalList = p.get_orbitals( basisSpecies = None, spin='both', asList = True)
    #print(orbitalList)
    HOMO, LUMO = p.get_HOMO_LUMO(basisSpecies = 'La', spin='both')
    print(p.atom_species)
    print('HOMO:', HOMO, HOMO.E)
    print(p.HOMO.basisfuncs )
    print('LUMO:', LUMO, LUMO.E)
    print(p.LUMO.basisfuncs )
    print('Shared Atoms:')
    print(LUMO.basisatoms.intersection(HOMO.basisatoms))
    labelSet = set()
    for orbital in orbitalList: 
        if orbital.spin == 'up':linestyle = ':' 
        elif orbital.spin == 'down':linestyle = '-'  
        if orbital.occ == 1:color = 'tab:blue' 
        elif orbital.occ == 0:color = 'tab:red' 
        label = 'occ: {}'.format(orbital.occ)
        if label in labelSet: label = None
        else: labelSet.add(label)
        #print(orbital.vector, orbital.spin, orbital.occ, orbital.E)
        ax.plot([0,1], [orbital.E, orbital.E], color=color, label=label, zorder=1)
    ax.plot([0,1], [LUMO.E, LUMO.E], color='tab:pink', label='LUMO',  linestyle='--', zorder=2)
    ax.plot([0,1], [HOMO.E, HOMO.E], color='tab:cyan', label='HOMO',  linestyle = '--', zorder=2)

ax.legend()
plt.show()
