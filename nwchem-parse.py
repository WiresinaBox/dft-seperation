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
    

    def __init__(self, fn):
        self.fn = fn
        inFile = open(fn, 'r')
        
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
            elif line.startswith('Memory information'): section = 'meminfo'
            elif line.startswith('Directory information'): section = 'dirinfo'
            
            if line.startswith('NWChem Input Module'): module = 'input'
            if line.startswith('Geometry'): section = 'geo'

            #Stats recording sections
            if section == 'jobinfo': lineBuffer.append(line)
            
            
            
            #Checks if the section has changed. If so call the appropriate function.
            if section != prevsection:
                if prevsection == 'jobinfo': self._jobinfo_parser(lineBuffer)


                prevsection = section
                lineBuffer = []

    #Put methods here to grab data from each section.
    def _jobinfo_parser(self, lines):
        """Parses the job info section."""
        for line in lines:
            print(line)


if __name__ == '__main__':
    fn = sys.argv[1]
    nwchem_parser(fn)
