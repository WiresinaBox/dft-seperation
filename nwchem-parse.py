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
        
        for line in inFile:
            print(line)
            #Call methods, get data.  

    #Put methods here to grab data from each section.



if __name__ == '__main__':
    fn = sys.argv[1]
    nwchem_parser(fn)
