import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import nwchem_parse as nwparse
import plotutil as pltu
import mpld3
from mpld3 import plugins, utils
import figure_site as site
#A space for scratchwork for calling other modules

parser = argparse.ArgumentParser()
parser.add_argument('filepath', nargs = '+')
args = parser.parse_args()


def plotEnergies():
    fig, ax = plt.subplots(1,1)
    dataDir = '../outfiles'
    print(os.listdir(dataDir))
    for subDir in os.listdir(dataDir):
        subDirPath = dataDir + '/' + subDir
        if os.path.isdir(subDirPath):
            outFiles = sorted([fn for fn in os.listdir(subDirPath) if fn.startswith('nwchem.out')], key = lambda x: float(x.split('.')[2]))
            print(outFiles)
            parsers = []
            for i, fn in enumerate(outFiles):
                print('[{}/{}] {} | {}'.format(i+1, len(outFiles), subDir, fn))
                path = subDirPath+'/'+fn
                parsers.append(nwparse.nwchem_parser(path)) 
            pltu.plot_total_energies(parsers, label=subDir, marker='o', ax=ax)
            
    ax.legend()
    plt.savefig('energies.png')
    plt.show()    


#plotEnergies()
#quit()

fnList = args.filepath #nargs=+ returns a list of at least one.
parserList = []

for fn in fnList:
    p = nwparse.nwchem_parser(fn)
    parserList.append(p)
    print(p.dft_energies)
    atomList = p.get_atoms(species = 'La', asList = True)
    print(atomList)
    fig,ax = pltu.plot_atom_distances(atomList[0], species=None)
    #fig, ax = pltu.plot_total_energies([p, p, p], label=fn, marker='o')

    #for atom in atomList:
    #    print(atom.id)
    #    print(atom.get_neighbors_by_dist(6, species='O'))
ax.legend()
plt.show()    

quit()
fig, ax = plt.subplots(1,1, figsize=(6,7), tight_layout=True)
Site = site.sitePage()
for p in parserList:
    #print(p.get_orbital_dict())
    
    orbitalListFull = p.get_orbitals( basisSpecies = None, spin='both', asList = True)
    fig, ax,handlesFull  = pltu.plot_energy_level(orbitalListFull, fig = fig, ax = ax, xlabel='All Orbitals', interactive=False) #overwriteStyle={'zorder':0, 'alpha':0.05})
    
    orbitalList = p.get_orbitals( basisSpecies = 'La', spin='both', asList = True)
    HOMO, LUMO = p.get_HOMO_LUMO(basisSpecies = 'La', spin='both', setFlags=True)
    fig, ax, handles = pltu.plot_energy_level(orbitalList, fig = fig, ax = ax, xlabel='La Basis Func', interactive=True, xlevel=1)
    
    orbitalList = p.get_orbitals( basisSpecies = 'S', spin='both', asList = True)
    fig, ax,handlesSpin= pltu.plot_energy_level(orbitalList, fig = fig, ax = ax, xlabel='S Basis Func', interactive=False, xlevel=2)
    orbitalList = p.get_orbitals( basisSpecies = 'O', spin='both', asList = True)
    fig, ax,handlesSpin= pltu.plot_energy_level(orbitalList, fig = fig, ax = ax, xlabel='O, Basis Func', interactive=False, xlevel=3)
    
    orbitalList = p.get_orbitals( basisSpecies = 'P', spin='both', asList = True)
    fig, ax,handlesSpin= pltu.plot_energy_level(orbitalList, fig = fig, ax = ax, xlabel='P Basis Func', interactive=False, xlevel=4)
    

    #print(p.atom_species)
    #print('HOMO:', HOMO, HOMO.E)
    #print(p.HOMO.basisfuncs )
    #print('LUMO:', LUMO, LUMO.E)
    #print(p.LUMO.basisfuncs )
    #print('Shared Atoms:')
    #print(LUMO.basisatoms.intersection(HOMO.basisatoms))
    #labelSet = set()
    #for orbital in orbitalList: 
    #    if orbital.spin == 'up':linestyle = ':' 
    #    elif orbital.spin == 'down':linestyle = '-'  
    #    if orbital.occ == 1:color = 'tab:blue' 
    #    elif orbital.occ == 0:color = 'tab:red' 
    #    label = 'occ: {}'.format(orbital.occ)
    #    if label in labelSet: label = None
    #    else: labelSet.add(label)
    #    #print(orbital.vector, orbital.spin, orbital.occ, orbital.E)
    #    ax.plot([0,1], [orbital.E, orbital.E], color=color, label=label, zorder=1)
    #ax.plot([0,1], [LUMO.E, LUMO.E], color='tab:pink', label='LUMO',  linestyle='--', zorder=2)
    #ax.plot([0,1], [HOMO.E, HOMO.E], color='tab:cyan', label='HOMO',  linestyle = '--', zorder=2)
#print(handles)
ax.legend(handles=handles)
#plt.show()
#mpld3.show()
Site.add_parser(1, p)
Site.add_parser(2, p)
Site.add_parser(3, p)
Site.add_figure(1, fig)
Site.add_figure(2, fig)
Site.add_figure(3, fig)
Site.setup_HTML()
site.run(Site)
