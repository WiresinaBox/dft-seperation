import nwchem_parse as nwparse
import sys
import os
import glob
#Pretty simple script to batch process a bunch of nwchem outfiles and turn them into json save files

outSaveDir = 'nwchem_outfiles'
jsonSaveDir = 'nwchem_jsonfiles'

try: os.mkdir(outSaveDir)
except: pass
try: os.mkdir(jsonSaveDir)
except: pass

fnList=sys.argv[1:]
if len(fnList) == 0:
    print('Defaulting to outfiles located at {}'.format(outSaveDir))
    fnList = glob.glob('{}/*'.format(outSaveDir))


for fn in fnList:
    try:
        print('Processing {}'.format(fn))
        p = nwparse.nwchem_parser(fn, name = fn.split('/')[1])
        p.save_json(saveDir = jsonSaveDir)
    except IsADirectoryError:
        pass
