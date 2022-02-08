import os
import sys
import numpy as np


class nw_orbital():
    """Contains information for each alpha/beta orbital"""

    @property
    def E(self): return self._E
    @E.setter
    def E(self, val): self._E = val
    @property
    def occ(self): return self._occ
    @occ.setter
    def occ(self, val): self._occ = val
    @property
    def vector(self): return self._vector
    @vector.setter
    def vector(self, val): self._vector = val
   
    @property
    def basisfuncs(self): return self._basisfuncs
    @basisfuncs.setter
    def basisfuncs(self, val): self._basisfuncs = val
    
    def add_basisfunc(self, bfn, coeff, atom, orbital):
        self._basisatoms.add(atom)
        self._basisfuncs.append((bfn, coeff, atom, orbital))
    
    @property
    def basisatoms(self): return self._basisatoms
    @basisatoms.setter
    def basisatoms(self, val): self._basisatoms = val


    @property
    def center(self): return self._center
    @center.setter
    def center(self, val): self._center = np.array(val)
    
    def set_spin(self, val): 
        if val in [1/2, "1/2", "0.5", 'alpha', 'up']: 
            self._spin = 'up'
            self._ms = 1/2
        elif val in [-1/2, "-1/2", "-0.5", 'beta', 'down']: 
            self._spin = 'down'
            self._ms = -1/2
    
    @property
    def spin(self): return self._spin
    @spin.setter
    def spin(self, val): self.set_spin(val)
    
    @property
    def ms(self): return self._ms
    @ms.setter
    def ms(self, val): self.set_spin(val) 

    def __init__(self,vector, E=None, occ=None, basisfuncs=[], spin=None):
        self._E = E
        self._occ = occ
        self._vector = vector
        self._basisatoms = set()
        self._basisfuncs = []# basisfuncsList
        for bfn, coeff, atom, orbital in basisfuncs:
            self.add_basisfunc(bfn, coeff, atom, orbital)

        self._center = None #tuple
        self._r2 = None 
        self._ms = None #1/2, -1/2
        self._spin = None #'up', 'down'

    def __repr__(self):
        return 'orbital({}, {}, {})'.format(self._vector, self._spin, self._occ)
    

class nw_atom():
    """Contains all the information for atom specific information. Species, Iterations, Orbital information etc."""
    
    @property
    def species(self): return self._species
    @species.setter
    def species(self, val): self._species = val
    @property
    def id(self): return self._id
    @id.setter
    def id(self, val): self._id = val
    @property
    def charge(self): return self._charge
    @charge.setter
    def charge(self, val): self._charge = val

    def __init__(self, id=None, species=None, charge=None):
        self._id = id
        self._species = species
        self._charge = charge

    def __repr__(self):
        return 'atom({},{})'.format(self._id, self._species)

class nwchem_parser():
    #nwchem.out sections
    """
    ==SETUP==
    start RUN_NAME
    charge 0
    geometry noautoz
    BASIS
    ECP
    dft
    driver

    task dft optimize
    task dft freq <- task starts the following command.
    
    ==LOG==
    Job Information
    Memory information
    Directory information
    NWChem Input Module
        Scaling Coordinates
        Initial Geometry and Charge
        Effective Nuclear repulsion energy
        Nuclear Dipole moment
        Internuclear Distances
        Basis per Atom Type (AO and ECP)
            Summary of Basis
        Geometry Optimization
    
    ==ENERGY MINIMIZATION==
    Initial Geometry and Charge
    Effective Nuclear Replusion Energy
    Nuclear Dipole Moment
    NWChem DFT Module
        Summary of Basis
        'texas integral default override'
        General Information
        XC Information
        Grid Information
        Convergence Information
        Screening Tolerance Information
        Supeposition of Atomic Density (Sum of atomic energies)
        
        Non-variational initial energy
            Total, 1-e, 2-e, HOMO, LUMO Energies
        Total Density
            Atom -> Charge -> Shell Charges
        Spin Density
            Atom -> Charge -> Shell Charges
        Memory Info
        Convergence Log
            Iter -> Energy -> Delta -> RMS Density -> Time
        TOTAL DFT ENERGIES (one electron, coulomb, exchange-corr, nuclear repulsion etc...)
        
        DFT Final Alpha Molecular Orbital Analysis
            Occupancy -> Energy -> Bfn. Coefficient -> Atom 
        
        DFT Final Beta Molecular Orbital Analysis
            Occupancy -> Energy -> Bfn. Coefficient -> Atom

        Total Density Milikan 
        Spin Density Milikan
        Total Density Lowdin
        Spin Density Lowdin
            Atom -> Charge -> Per Shell Charge
        
        alpha-beta overlap
        
        center of mass
        moments of inertia
        multipole analysis of density
        
        Performance Info
    
    NWChem DFT Gradient Module
        Charge, Wavefunction
        Texas Integral Overwrites
        DFT Energy Gradients
        Energy per Step

    """

    
    #Getters and Setters
    @property
    def energies(self): return self._energies
    @energies.setter
    def energies(self, val): self._energies = val
    
    
    @property
    def atom_dict(self): return self._atom_dict
    @atom_dict.setter
    def atom_dict(self, val): self._atom_dict = val
    
    @property
    def atom_species(self): return self._atom_species
    @atom_species.setter
    def atom_species(self, val): self._atom_species = val
    
    @property
    def runinfo(self): return self._runinfo
    @runinfo.setter
    def runinfo(self, val): self._runinfo = val
    
    @property
    def orbital_dict_alpha(self): return self._orbital_dict_alpha
    @orbital_dict_alpha.setter
    def orbital_dict_alpha(self, val): self._orbital_dict_alpha = val
    
    @property
    def orbital_dict_beta(self): return self._orbital_dict_beta
    @orbital_dict_beta.setter
    def orbital_dict_beta(self, val): self._orbital_dict_beta = val
    
    @property
    def HOMO(self): return self._HOMO
    @HOMO.setter
    def HOMO(self, val): self._HOMO = val
    @property
    def LUMO(self): return self._LUMO
    @LUMO.setter
    def LUMO(self, val): self._LUMO = val
    
    def get_orbitals(self, vector=None, spin='both', basisId=None, basisSpecies = None, asList = False, conjunction=False):
        """Returns either a list or a dictionary of orbitals given certain conditions.

        if conjuction = True, then *all* basis function conditions must match. Otherwise only one condition has to match
        e.g. if conjunction = True, basisSpecies = 'La', then only will return orbitals where all basis functions are from lanthenide.
        """
        if spin == 'both':
            a= {(o.vector, o.spin):o for o in self._orbital_dict_alpha.values()}
            a.update({(o.vector, o.spin):o for o in self._orbital_dict_beta.values()})
        elif spin in [1/2, "1/2", "0.5", 'alpha', 'up']: 
            a= {(o.vector, o.spin):o for o in self._orbital_dict_alpha.values()}
        elif spin in [-1/2, "-1/2", "-0.5", 'beta', 'down']: 
            a= {(o.vector, o.spin):o for o in self._orbital_dict_beta.values()}
        

        vectorList = []
        basisIdList = []
        basisSpeciesList = []
        
        if isinstance(vector, (list, tuple)): vectorList.extend(vector)
        elif not isinstance(vector, type(None)): vectorList.append(vector)
        
        if isinstance(basisId, (list, tuple)): basisIdList.extend(basisId)
        elif not isinstance(basisId, type(None)): basisIdList.append(basisId)
        
        if isinstance(basisSpecies, (list, tuple)): basisSpeciesList.extend(basisSpecies)
        elif not isinstance(basisSpecies, type(None)): basisSpeciesList.append(basisSpecies)
       
        if asList: r = []
        else: r = {}
        for key, o in a.items():
            if o.vector in vectorList: vectorPass = True
            elif len(vectorList) == 0: vectorPass = True
            else: vectorPass = False
            
            #Probably an easier way to do this...
            if conjunction: idPass = True #all must pass or else turn to false
            else: idPass = False #takes one truth to turn it to true always
            if conjunction: speciesPass = True 
            else: speciesPass = False #
            
            for bfn, coeff, atom, function in o.basisfuncs:
                if conjunction: idPass = idPass and atom.id in basisIdList #One False will make it false
                else: idPass = idPass or atom.id in basisIdList #One truth will turn it to truth
                if conjunction: speciesPass = speciesPass and atom.species in basisSpeciesList #One False will make it false
                else: speciesPass = speciesPass or atom.species in basisSpeciesList #One truth will turn it to truth
                
                 
            #General cases
            if len(basisIdList) == 0: idPass = True
            if len(basisSpeciesList) == 0: speciesPass = True
            if vectorPass and idPass and speciesPass:
                if asList: r.append(o)
                else: r[key] = o

        return r 

    def get_HOMO_LUMO(self, **kwargs):
        """This method gets the homo and lumo based on conditions specified in get_atoms()"""
        if len(kwargs) == 0: return self._HOMO, self._LUMO
        orbitalList = self.get_orbitals(asList=True, **kwargs)
        HOMO = None
        LUMO = None
        for O in orbitalList:
            if (isinstance(HOMO, type(None)) or HOMO.E < O.E ) and O.occ == 1: HOMO = O 
            if (isinstance(LUMO, type(None)) or LUMO.E > O.E ) and O.occ == 0: LUMO = O 
        return HOMO, LUMO

    def get_atoms(self, id = None, species = None, alwaysAsList=False):
        """Returns a list of atoms given the specified constraints. If none are given then returns all atoms."""
        idList = []
        speciesList = []
        returnList = []
        if isinstance(id, (list, tuple)): idList.extend(id)
        elif not isinstance(id, type(None)): idList.append(id)
        if isinstance(species, (list, tuple)): speciesList.extend(species)
        elif not isinstance(species, type(None)): speciesList.append(species)
        for a in self._atom_dict.values():
            if len(idList) > 0 and a.id in idList:
                idpass = True 
            elif len(idList) == 0: 
                idpass = True
            else:
                idpass = False
            
            if len(speciesList) > 0 and a.species in speciesList:
                speciespass = True 
            elif len(speciesList) == 0: 
                speciespass = True
            else:
                speciespass = False

            if idpass and speciespass:
                returnList.append(a)
        if len(returnList) == 1 and not alwaysAsList: return returnList[0]
        else: return returnList
    
     

    def __init__(self, fn):
    
        self._runinfo = dict()
        self._atom_dict = dict()
        self._atom_species = set()
        self._orbital_dict_alpha = dict()
        self._orbital_dict_beta = dict()
        self._energies = dict()
        
        #orbitals
        self._HOMO = None
        self._LUMO = None

        self.fn = fn
        inFile = open(fn, 'r')
        
        part = 'start'
        module = 'start'
        prevsection = 'start'
        section = 'start'
        lineBuffer = [] #holds lines to then pass off to each method parser
        for linein in inFile:
            line = linein.strip()
            #Are whitespaces needed? I'm going to skip them
            if line == '': continue
            #Marks the start/end of sections
            if line.startswith('Job information'): section = 'jobinfo'
            if line.startswith('Memory information'): section = 'meminfo'
            if line.startswith('Directory information'): section = 'dirinfo'
            
            if line.startswith('NWChem Input Module'): module = 'input'
            if line.startswith('Geometry'): section = 'geo' #Also contains atomic mass and Zeff
            if line.startswith('Atomic Mass'): section = 'mass' 
            if line.startswith('Effective nuclear repulsion energy'): section = 'zeff' 
            if line.startswith('Nuclear Dipole moment'): section = 'ndm'
            if line.startswith('internuclear distances'): section = 'ind' #and internuclear angles
            if line.startswith('Basis'): section = 'basis'
            if line.startswith('Summary of'): section = 'basis_sum'
            if line.startswith('ECP'): section = 'ecp'
            if line.startswith('NWChem Geometry Optimization'): module = 'opt'
            
            
            if line.startswith('Energy Minimization'): part = 'enmin'
            if line.startswith('NWChem DFT Module'): module = 'dft'
            if line.startswith('General Information'): section = 'geninfo'
            if line.startswith('XC Information'): section = 'xcinfo'
            if line.startswith('Grid Information'): section = 'gridinfo'
            if line.startswith('Convergence Information'): section = 'convinfo'
            if line.startswith('Screening Tolerance Information'): section = 'screentolinfo'
            if line.startswith('Superposition of Atomic Density'): section = 'superposinfo'
            if line.startswith('Non-variational initial energy'): section = 'nonvarinfo' #Important!
            if line.startswith('Total Density'): section = 'totden'
            if line.startswith('Spin Density'): section = 'spinden'
            if line.startswith('Integral file'): section = 'intfile'
            if line.startswith('Grid_pts file'): section = 'gridfile'
            if line.startswith('convergence'): section = 'convergence'
            if line.startswith('Total DFT energy'): section = 'dftenergy'
            
            if line.startswith('DFT Final Alpha'): section = 'moalpha'
            if line.startswith('DFT Final Beta'): section = 'mobeta'
            if line.startswith('alpha - beta orbital overlaps'): section = 'aboverlap'
            if line.startswith('alpha - beta orbital overlaps'): section = 'aboverlap'
            if line.startswith('Expectation of S2'): section = 'S2'
            if line.startswith('Center of mass'): section = 'com'
            if line.startswith('moments of inertia'): section = 'moi'
            if line.startswith('Multipole analysis of the density'): section = 'multipole'
            if line.startswith('EAF file'): section = 'runinfo'
            
            if line.startswith('NWChem DFT Gradient Module'):module = 'dftgrad';  section = 'dftgrad'



            
            
            #Checks if the section has changed. If so call the appropriate function.
            if section != prevsection:
                #print(part, module, section)
                if prevsection == 'jobinfo': self._jobinfo_parser(lineBuffer)
                if prevsection == 'geo' and module == 'opt': self._geo_parser(lineBuffer)
                if prevsection == 'nonvarinfo': self._nonvarinfo_parser(lineBuffer)
                if prevsection == 'moalpha': self._moparser(lineBuffer, 'alpha')
                if prevsection == 'mobeta': self._moparser(lineBuffer, 'beta')

                prevsection = section
                lineBuffer = []
            
            #Stats recording sections
            lineBuffer.append(line)

    def __repr__(self):
        return 'nwchem_parser({})'.format(self.fn)
    #Put methods here to grab data from each section.
    def _jobinfo_parser(self, lines):
        """Parses the job info section."""
        for line in lines[2:]:
            dat = line.partition('=')
            #print(dat)
            if dat[0].strip() == 'date': self._runinfo['date'] = dat[2]
            if dat[0].strip() == 'nwchem branch': self._runinfo['NW_branch'] = dat[2]
            if dat[0].strip() == 'nwchem revision': self._runinfo['NW_revision'] = dat[2]
            if dat[0].strip() == 'ga revision': self._runinfo['GA_revision'] = dat[2]
            if dat[0].strip() == 'prefix': self._runinfo['prefix'] = dat[2]
        #print(self._runinfo)
    def _geo_parser(self, lines):
        for line in lines[5:]:
            dat = line.split()
            a = nw_atom(id = int(dat[0]), species = dat[1], charge = float(dat[2]))
            self._atom_dict[a.id] = a
            self._atom_species.add(a.species)
                
    def _nonvarinfo_parser(self, lines):
        for line in lines[2:-1]:
            dat = line.partition('=')
            if dat[0].strip() == 'Total energy': self._energies["total"] = float(dat[2])
            if dat[0].strip() == '1-e energy': self._energies["1e"] = float(dat[2])
            if dat[0].strip() == '2-e energy': self._energies["2e"] = float(dat[2])
            if dat[0].strip() == 'HOMO': self._energies["HOMO"] = float(dat[2]) #Highest occupied molecular orbital
            if dat[0].strip() == 'LUMO': self._energies["LUMO"] = float(dat[2]) #Lowest unoccupied molecular orbital
    def _moparser(self, lines, orbitType):
        curVect = None
        for line in lines[2:]:
            dat = line.split()
            if line.startswith('Vector'):
                if not isinstance(curVect, type(None)) and  int(dat[1]) != curVect:
                    #Append current orbital  
                    if orbitType == 'alpha': 
                        O.spin= orbitType
                        self._orbital_dict_alpha[O.vector] = O
                    elif orbitType == 'beta': 
                        O.spin = orbitType
                        self._orbital_dict_beta[O.vector] = O
                    if (isinstance(self._HOMO, type(None)) or self._HOMO.E < O.E ) and O.occ == 1: self._HOMO = O 
                    if (isinstance(self._LUMO, type(None)) or self._LUMO.E > O.E ) and O.occ == 0: self._LUMO = O 
                
                curVect = int(line[7:13].strip())
                O = nw_orbital(curVect)
                O.occ =  int(float(line[17:31].replace('D', 'E'))) #TODO: Doublecheck that D->E number format is ok
                O.E = float(line[33:48].replace('D', 'E'))
            elif line.startswith('MO Center'):
                x = float(dat[2].replace('D', 'E').strip(','))
                y = float(dat[3].replace('D', 'E').strip(','))
                z = float(dat[4].replace('D', 'E').strip(','))
                O.center = np.array([x,y,z])
                O.r2 = float(dat[6].replace('D', 'E'))
            elif line.startswith('-----'): pass
            elif line.startswith('Bfn.'): pass
            else:
                p1 = line[0:38].strip().split()
                p2 = line[38:].strip().split()
                #print('p1:',p1)
                #print('p2:',p2)
                if len(p1) > 0:
                    atom = self.get_atoms(id = int(p1[2]), species = p1[3])
                    O.add_basisfunc(int(p1[0]), float(p1[1]), atom, p1[4])
                if len(p2) > 0:
                    atom = self.get_atoms(id = int(p2[2]), species = p2[3])
                    O.add_basisfunc(int(p2[0]), float(p2[1]), atom, p2[4])
        if orbitType == 'alpha': 
            O.spin= orbitType
            self._orbital_dict_alpha[O.vector] = O
        elif orbitType == 'beta': 
            O.spin = orbitType
            self._orbital_dict_beta[O.vector] = O
        if (isinstance(self._HOMO, type(None)) or self._HOMO.E < O.E ) and O.occ == 1: self._HOMO = O 
        if (isinstance(self._LUMO, type(None)) or self._LUMO.E > O.E ) and O.occ == 0: self._LUMO = O 
    


if __name__ == '__main__':
    fn = sys.argv[1]
    nw = nwchem_parser(fn)
    #print(nw.energies) 
    #print(nw.runinfo)
    #print(nw.get_atoms(id = 5, alwaysAsList=True))
    #print(nw.get_orbital_dict())
    #print(nw)
