# NWChem DFT and Vibrational Parsing and Interactive Demonstration

This project is a demonstration of parsing NWChem results, automating DFT cacluations, and creating interactive, web-based figures using available python libraries. Currently this project is able to

- Parse select portions of the NWChem DFT and Freq modules
 - Run information
 - Final converged geometry, gradient, and DFT energies
 - Orbitals and basis functions
 - Vibrational corrections, entropies, and heat capacities
- Convert matplotlib plots to a D3 and add extensive interactive components using mpld3
 - Geometry visualization using Chemdoodle web components and integrating interactivity with other plots.

## Requirements
- Python 3.6+
- Numpy
- Matplotlib
- mpld3
- flask, flask_restx
- mysql

## Usage

First, run

`python3 process_nwchem_outfiles.py <file1> <file2>...`

To process NWChem outfiles into parsed JSON files, this will substantially cut down on the time it takes to load data for the website interface. If no files are given, then `process_nwchem_outfiles.py` will process files in `./nwchem_outfiles`. Saved JSON files are then written to `./nwchem_jsonfiles`.

To launch the interactive site, run

`python3 figure_site.py`

and go to <http://127.0.0.1:5000/>. This launches a flask backend to serve the site, loads data from `./nwchem_jsonfiles` and creates the plot. However, currently it is in debug mode and will require more work to make it ready for a proper website. From the website interface, the DFT orbitals of multiple different results can be filtered by basis functions, analyzed side-by-side, and visualized in space. Currently the atomic orbitals aren't able to be visualized due to limitations in the libraries used. 

## Project Structure

### nwchem_parse.py
Contains the nwchem_parser, nwchem_atom, and nwchem_orbital classes. nwchem_parser() contains the necessary functions to populate the latter two, save, and load data.

### plotutil.py
Contains functions and mpld3 plugins to create the DFT energy and energy level plots. Two custom plugins implement the energy level interactivity which communicate with the Chemdoodle plot and replaces tick marks with custom labels (which apparently isn't a supported feature currently in mpld3)

### figure_site.py
Contains the loading, plotting, and calls flask to create the site. To add new plots, add another function handle to launchSite() at line 188. These plot functions should return a json string.

### api.py
Contains the routing for flask

`./templates` contains the html, javascript, and css files used by flask to create the website interface.








