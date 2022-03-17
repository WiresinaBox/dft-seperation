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
fns = glob.glob('../outfiles/la-9water-3C301-3+/nwchem.out*')
#parsers = {'testing1':'dummy parser1', 'testing2':'dummy parser2'}
parserDict = {fn.split('/')[-1]:{'filename': fn} for fn in fns}


def getParserInfoFromCall(complexList):
    returnList=[]
    for complexName in complexList:
        parserInfo = parserDict[complexName]
        returnList.append(parserInfo)
    return returnList

def getParsersFromCall(complexList):
    """Returns a list of parsers from the requested string names. Will save previously generated parsers"""
    returnList = []
    for parserInfo in getParserInfoFromCall(complexList):
        if 'parser' in parserInfo:
            returnList.append(parserInfo['parser'])
        else:
            p = nwparse.nwchem_parser(parserInfo['filename'])
            parserInfo['parser']=p #add new parser in
            returnList.append(p)

    return returnList

def getEnergyPlot(complexList):
    parserInfosList = getParserInfoFromCall(complexList)
    parserList = getParsersFromCall(complexList)#same ordering

    fig, ax = pltu.plot_total_energies(parserList, label=complexList, marker='o')
    html = mpld3.fig_to_html(fig)
    htmlParser = pltu.mpld3HTMLParser()
    htmlParser.feed(html)
    return json.dumps(htmlParser.tagDict)

def getEnergyLevelPlot(complexList):
    parserInfosList = getParserInfoFromCall(complexList)
    parserList = getParsersFromCall(complexList)#same ordering
    
    fig, ax = plt.subplots(1,1, figsize=(6,7), tight_layout=True)
    for i,p in enumerate(parserList):
        orbitalList = p.get_orbitals( basisSpecies = 'La', spin='both', asList = True)
        HOMO, LUMO = p.get_HOMO_LUMO(basisSpecies = 'La', spin='both', setFlags=True)
        fig, ax, handles = pltu.plot_energy_level(orbitalList, fig = fig, ax = ax, xlabel='La Basis Func', interactive=True, xlevel=i)
    if len(parserList) > 0:
        ax.legend(handles=handles)
    
    html = mpld3.fig_to_html(fig)
    htmlParser = pltu.mpld3HTMLParser()
    htmlParser.feed(html)
    return json.dumps(htmlParser.tagDict)

def getStructPlot(complexList):
    parserInfosList = getParserInfoFromCall(complexList)
    parserList = getParsersFromCall(complexList)#same ordering

    returnDict = {}
    for i, p in enumerate(parserList):
        complexName = complexList[i]
        
        returnDict[complexName] = p.xyz_string()
    print(returnDict)
    return json.dumps(returnDict)



def launchSite():
    app = flask.Flask(__name__, template_folder='./templates', static_folder='./templates/static')
    api.parserDict.update(parserDict)
    #Set all of the special functions it calls
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
