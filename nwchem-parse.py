import os
import sys


class nwchem_parser():
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
