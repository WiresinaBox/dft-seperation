import flask
import api
from api import blueprint as parser_api #Get the local copy in .api
#import flask_classful as flaskc
import nwchem_parse as nwparse
import matplotlib.pyplot as plt
import plotutil as pltu
import mpld3
from mpld3 import plugins, utils
import json
import glob
import os
import numpy as np
import webbrowser
#OUTLINE FOR FUTURE:
#1. JS/Python interface: Flask
#2. UI: React
#3. Structure visualization: Pymol

#General idea is to be able to upload/select a series of different run files to compare basic parameteres
#1. Total Energy/DFT Energy plot. Line graph
#2. Pymol structure visualization
#3. Energy level diagrams, each structure side by side to see evolution
#4. Energy level filter by certain parameters

#parsers = {'testing1':'dummy parser1', 'testing2':'dummy parser2'}
#fns = glob.glob('../outfiles/la-9water-3C301-3+/nwchem.out*')
#fns = glob.glob('../outfiles/la-19water-3C301/nwchem.out*')

outSaveDir = 'nwchem_outfiles'
jsonSaveDir = 'nwchem_jsonfiles'

try: os.mkdir(outSaveDir)
except: pass
try: os.mkdir(jsonSaveDir)
except: pass

#fns = glob.glob('{}/*'.format(outSaveDir))
fns = sorted(glob.glob('{}/*'.format(jsonSaveDir))) #Will preferentially load the json save files if they exist
if len(fns) == 0:
    print('No files found in nwchem_outfiles directory! Place some in here to be analyzed.')
for fn in fns:
    print('Found:', fn)

#parsers = {'testing1':'dummy parser1', 'testing2':'dummy parser2'}
parserDict = {fn.split('/')[-1].partition('.json')[0]:{'filename': fn} for fn in fns}


def getParserInfoFromCall(complexList, **kwargs):
    returnDict=dict()
    for complexName in complexList:
        parserInfo = parserDict[complexName]
        returnDict[complexName] = parserInfo
    return returnDict

def getParsersFromCall(complexList, **kwargs):
    """Returns a list of parsers from the requested string names. Will save previously generated parsers"""
    returnList = []
    #for parserInfo in getParserInfoFromCall(complexList):
    for parserKey, parserInfo in getParserInfoFromCall(complexList).items():
        if 'parser' in parserInfo:
            returnList.append(parserInfo['parser'])
        else:
            print('Loading: {}'.format(parserKey))
            p = nwparse.nwchem_parser(parserInfo['filename'], name = parserKey)
            parserInfo['parser']=p #add new parser in
            returnList.append(p)
            #p.save_json(saveDir=jsonSaveDir) #HEADS UP. DO WE WANT TO ALWAYS SAVE HERE?
    return returnList

def getEnergyPlot(complexList, viewSize = (1000, 1000), dpi=150, **kwargs):
    parserInfosList = getParserInfoFromCall(complexList)
    parserList = getParsersFromCall(complexList)#same ordering

    fig, ax = pltu.plot_total_energies(parserList, label=complexList, marker='o', viewSize=viewSize, dpi=dpi)
    html = mpld3.fig_to_html(fig)
    htmlParser = pltu.mpld3HTMLParser()
    htmlParser.feed(html)
    return json.dumps(htmlParser.tagDict)

def getEnergyLevelPlot(complexList, orbitalSpecies=[], viewSize = (1000, 1000), dpi=150, **kwargs):
    parserInfosList = getParserInfoFromCall(complexList)
    parserList = getParsersFromCall(complexList)#same ordering
    
    fig, ax = plt.subplots(1,1, figsize=(viewSize[0]*0.7/dpi , viewSize[1]*1.5/dpi), tight_layout=True,)
   
    if orbitalSpecies == ['']: 
        conjunction = False
        orbitalSpecies= None
    else: conjunction = True
    ylim = [np.inf, -np.inf]
    for i,p in enumerate(parserList):
        orbitalListFull = p.get_orbitals(basisSpecies = None, spin='both', asList = True)
        orbitalList = p.get_orbitals(basisSpecies = orbitalSpecies, spin='both', asList = True, conjunction=conjunction)
        orbitalE = [O.E for O in orbitalList]
        if len(orbitalE) > 0:
            ylim[0] = min(ylim[0], np.min(orbitalE))
            ylim[1] = max(ylim[1], np.max(orbitalE))
        
        #Plot all orbitals underneath it but transparent
        fig, ax,handlesFull  = pltu.plot_energy_level(orbitalListFull, fig = fig, ax = ax, interactive=False, overwriteStyle={'zorder':0, 'alpha':0.1}, xlevel = i)


        HOMO, LUMO = p.get_HOMO_LUMO(basisSpecies = orbitalSpecies, spin='both', setFlags=True, conjunction=True)
        fig, ax, handles = pltu.plot_energy_level(orbitalList, fig = fig, ax = ax, xlabel='{}\n[{}]'.format(str(orbitalSpecies), p.name), interactive=True, overwriteStyle={'alpha':1}, xlevel=i)
    if len(parserList) > 0:
        ax.legend(handles=handles)
    ax.set_xlim((0, len(parserList)))
    if not np.any(np.isinf(ylim)):
        ax.set_ylim(ylim)
    html = mpld3.fig_to_html(fig)
    htmlParser = pltu.mpld3HTMLParser()
    htmlParser.feed(html)
    return json.dumps(htmlParser.tagDict)

def getStructPlot(complexList, **kwargs):
    parserInfosList = getParserInfoFromCall(complexList)
    parserList = getParsersFromCall(complexList)#same ordering

    returnDict = {}
    for i, p in enumerate(parserList):
        complexName = complexList[i]
        
        #returnDict[complexName] = p.xyz_string()
        returnDict[complexName] = {'struct':p.cml_string(), 'dft_energies':p.dft_energies}
    #print(returnDict)
    return json.dumps(returnDict)

def getTablePlot(complexList, **kwargs):
    parserInfosList = getParserInfoFromCall(complexList)
    parserList = getParsersFromCall(complexList)#same ordering

    returnDict = {}
    for i, p in enumerate(parserList):
        complexName = complexList[i]
        if complexName not in returnDict:
            returnDict[complexName] = []
        #Put anything here and it'll be automatically shoved into tables
        #returnDict[complexName] =[ {'label':label, 'headers':['header1'...], 'data': [{'label':rowlabel, 'data'}]} ]
        #DFT Energies
        returnDict[complexName].append({
                'label':'DFT Energies', 
                'headers':['Type', 'Hartrees (a.u.)' ], 
                'data':[{'label':key, 'data':[val]} for key, val in p.dft_energies.items()]
                })
        countDict = {}
        #Atom Count Dict
        for a in p.atom_dict.values():
                if a.species not in countDict: countDict[a.species] = 1
                else: countDict[a.species] += 1
        countData = sorted([{'label':species, 'data':[count]} for species, count in countDict.items()], key = lambda x: x['label'])
        countData.insert(0, {'label':'Total', 'data':[len(p.atom_dict)]})
        returnDict[complexName].append({
                'label':'Species', 
                'headers':['Species', 'Count' ], 
                'data': countData,
                })
        #Vibrational constants
        returnDict[complexName].append({
                'label':'Freq. Correction',
                'headers':['', p._freq_correction_dict['unit']],
                'data': [{'label':key, 'data':[val]} for key, val in p._freq_correction_dict.items() if key != 'unit'], 
                })
        returnDict[complexName].append({
                'label':'Freq. Entropy',
                'headers':['', p._freq_entropy_dict['unit']],
                'data': [{'label':key, 'data':[val]} for key, val in p._freq_entropy_dict.items() if key in ['Translational', 'Rotational', 'Vibrational']],
                })
        returnDict[complexName].append({
                'label':'Freq. Heat Capacity (Cv)',
                'headers':['', p._freq_Cv_dict['unit']],
                'data': [{'label':key, 'data':[val]} for key, val in p._freq_Cv_dict.items() if key in ['Translational', 'Rotational', 'Vibrational']],
                })
        print(p._freq_Cv_dict)
        print(p._freq_entropy_dict)
        print(p._freq_correction_dict)
    #print(returnDict)
    return json.dumps(returnDict)


def launchSite():
    app = flask.Flask(__name__, template_folder='./templates', static_folder='./templates/static')
    api.parserDict.update(parserDict)
    #Set all of the special functions it calls
    api.plotFuncDict['tableEnergy'] = getTablePlot
    api.plotFuncDict['structure'] = getStructPlot
    api.plotFuncDict['levels'] = getEnergyLevelPlot 
    api.plotFuncDict['energy'] = getEnergyPlot 
     
    app.register_blueprint(parser_api, url_prefix='/api')
    #parser_api.init_app(apibp)


    @app.route('/')
    def index():
        return flask.render_template('index.html', name='index')
    return app



if __name__=='__main__':
    app = launchSite()
    #webbrowser.open('http://127.0.0.1:5000/')#Just for debug change this if you ever host the site
    app.run(debug=True)
    


#class siteData:
#    """
#    General idea is to initially pass all of the necessary parsers, references, and additonal matplotlib figures to this class
#    Then this object does the dirty work of rendering it all. Should it get a request from the website for more information,
#    it can draw on the stuff inputed here.
#    """
#    HTML = ''
#    parser_dict = dict() #Keyword so we can grab them later from a dropdown or something.
#    figure_dict = dict()
#    route ='' 
#    debug =''
#    def __init__(self,  route='/', debug=True):
#        self.route = route
#        self.debug = debug
#    def add_figure(self, key, fig): 
#        figHTML = mpld3.fig_to_html(fig, template_type='simple')
#        self.figure_dict[str(key)] = {'fig':fig, 'html':figHTML}
#    def add_parser(self, key, parser):
#        print('adding parser')
#        self.parser_dict[str(key)] = parser 
#        print(self.parser_dict)
#    def setup_HTML(self):
#        self.HTML += '<html>\n<body>'
#        for key, data in self.figure_dict.items():
#            self.HTML+=data['html']
#
#        self.HTML += '</body>\n</html>'
#
#class sitePage(flaskc.FlaskView, siteData): 
#    #Every method in this class but NOT in the base classes will be turned into a route.
#    route_base='/'
#    def index(self):
#        return flask.render_template('layout.html')
#        #return "hi!" 
#
#    def put(self):
#        print(self.parser_dict)
#        return json.dumps(list(self.parser_dict.keys()))
#    
#    def patch(self, dat):
#        print(dat, type(dat))
#        #return json.dumps(mpld3.fig_to_dict(self.figure_dict[dat]['fig']))
#        return self.figure_dict[dat]['html']
#
##Note, if you're getting an error 405, it's probably because there's a required areguement it's not putting in.
#
#def run(pageClass, **kwargs):
#    app.run(**kwargs)
#
##Do all the registrations here.
#sitePage.register(app)
#
#if __name__ == "__main__":
#    app.run(debug=True) 
#
