import os
import sys


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
    energy_total = None
    energy_1e = None
    energy_2e = None
    energy_HOMO = None
    energy_LUMO = None

    def __init__(self, fn):
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
            
            if line.startswith('DFT Final'): section = 'moanalysis'
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
                print(part, module, section)
                if prevsection == 'jobinfo': self._jobinfo_parser(lineBuffer)
                if prevsection == 'nonvarinfo': self._nonvarinfo_parser(lineBuffer)


                prevsection = section
                lineBuffer = []
            
            #Stats recording sections
            lineBuffer.append(line)

    #Put methods here to grab data from each section.
    def _jobinfo_parser(self, lines):
        """Parses the job info section."""
        for line in lines:
            print(line)
    def _nonvarinfo_parser(self, lines):
        for line in lines[2:-1]:
            dat = line.partition('=')
            print(dat[0])
            if dat[0].strip() == 'Total energy': self.energy_total = float(dat[2])
            if dat[0].strip() == '1-e energy': self.energy_1e = float(dat[2])
            if dat[0].strip() == '2-e energy': self.energy_2e = float(dat[2])
            if dat[0].strip() == 'HOMO': self.energy_HOMO = float(dat[2]) #Highest occupied molecular orbital
            if dat[0].strip() == 'LUMO': self.energy_LUMO = float(dat[2]) #Lowest unoccupied molecular orbital

if __name__ == '__main__':
    fn = sys.argv[1]
    nw = nwchem_parser(fn)
    print(nw.energy_total, nw.energy_1e, nw.energy_2e, nw.energy_HOMO, nw.energy_LUMO)
