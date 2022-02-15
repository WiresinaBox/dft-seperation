import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins, utils
import nwchem_parse as nwparse
import time




class energy_level_ievents(plugins.PluginBase):
    """Holds all the references for energy levels and stuff for use with the interaction portion"""

    #Ok so PluginBase pulls from some special variables
    #JAVASCRIPT, js_args_, css_, dict_
    #dict_ passes all the necessary information into the JS portion
    
    JAVASCRIPT = """
    //Register and set up the empty plugin
    mpld3.register_plugin("energylevels", EnergyLevelsPlugin);
    EnergyLevelsPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    EnergyLevelsPlugin.prototype.constructor = EnergyLevelsPlugin;
    EnergyLevelsPlugin.prototype.requiredProps = ["ids", "data"]; //arguements pulled from the python side.
    EnergyLevelsPlugin.prototype.defaultProps = {} //keyword arguements
  
    //Constructor
    function EnergyLevelsPlugin(fig, props){
        mpld3.Plugin.call(this, fig, props);
    }


    //Called upon rendering.
    EnergyLevelsPlugin.prototype.draw = function(){
        //this.fig -> figure
        //this.props.VARIABLE_NAME
       
        //create extra HTML objects using d3
        

        infodiv = d3.select("body")
                    .append("div")
                        .attr("class", "infodiv")
                        .attr("name", "orbitalinfo")
                        .style("height", 200)
                        .style("width", "100%")
        infodiv.append("p")
            .attr("class", "infotext")
            .attr("id", "occ")
            .text('occ')
        infodiv.append("p")
            .attr("class", "infotext")
            .attr("id", "E")
            .text('E')
                

        textE = d3.select("#E")
        
        textocc = d3.select("#occ")


        var objList = []
        for (var i=0; i < this.props.ids.length; i++) {

            var obj = mpld3.get_element(this.props.ids[i], this.fig);
            // get_element might return null if the id is a Line2D for some reason. 
            var data = this.props.data[i];
            obj.elements()
                .datum(data)
                .on("mouseover", function(d,j) {
                                    changeText(d, j);
                                })
        }
        
        //d is the datum, specifies points and stuff. i is the index within d of the point just touched.
        function changeText(d, i){
            console.log(d);
            textE.text(d.E);
            textocc.text(d.occ);

        }
        

    }

    """

    def __init__(self, fig, ax):
        self._fig = fig
        self._ax = ax
        self._artistsDict = dict() #{artist:orbital}
        self._refreshcalls = 0
        #Javascript stuff.
        self.dict_ = dict()

    def add_artist(self, artist, orbital):
        """Appends things like Line2D and what not"""
        if isinstance(artist, list):
            for a in artist:
                self._artistsDict[a] = orbital
        else:
            self._artistsDict[artist] = orbital
   
    def setup_data(self):
        """This sets up all the data and element ids for usage in the javascript protion"""
        items = self._artistsDict.items()
        artists = []
        orbitalDat = []
        for tup in items:
            a, dat = tup
            if isinstance(a, matplotlib.lines.Line2D): suffix = 'pts'
            else: suffix = None
            artists.append(utils.get_id(a, suffix))
            orbitalDat.append(dat.get_data())


        self.dict_["type"] ="energylevels"
        self.dict_["ids"] = artists 
        self.dict_["data"] = orbitalDat

    def connect_tooltip_plugin(self, fig = 'self'):
        if fig == 'self': fig = self._fig
        artists = [tup[0] for tup in self._artistsDict.items()]
        orbitalDat = ["E:{}, occ:{}".format(tup[1].E, tup[1].occ) for tup in self._artistsDict.items()]
        print('Connecting')
        for artist, orbital in self._artistsDict.items():
            tooltip = plugins.LineLabelTooltip(artist, label = 'E:{}, occ:{}'.format(orbital.E, orbital.occ))
            print(artist, tooltip)
            plugins.connect(fig, tooltip)
        #tooltip = plugins.LineLabelTooltip(artists, label=orbitalDat)

        #plugins.connect(fig, tooltip)

    def refresh(self, event): #Call on mouse release
        if self._refreshcalls > 0:
            self._fig.canvas.draw()
            self._fig.canvas.flush_events()
            self_refreshcalls = 0

    def orbital_pick_info(self, event):
        """Interactive component for plot_energy_level?"""
        line = event.artist
        mouseevent=event.mouseevent
        try:
            orbital = self._artistsDict[line]
        except KeyError:
            raise KeyError('energy_level_ievents.orbital_pick_info(): Corresponding orbital not found.')
        E = orbital.E
        
        self._refreshcalls +=1
        line.set_color('tab:green')
        print('{}, E : {}, atoms: {} '.format(orbital, orbital.E, orbital.basisatoms))

    

def plot_energy_level(orbitals, fig = None, ax = None, legend=False,
        conditions = [
            [{'occ':1}, {'label':'filled', 'color':'tab:blue', 'zorder':1}], 
            [{'occ':0}, {'label':'unfilled', 'color':'tab:red', 'zorder':1}],
            [{'occ':1, 'isHOMO':True}, {'label':'HOMO', 'color':'tab:cyan', 'linewidth':4, 'zorder':2}], 
            [{'occ':0, 'isLUMO':True}, {'label':'LUMO', 'color':'tab:pink', 'linewidth':4, 'zorder':2}],
            ],
        interactive = False,
        overwriteStyle = {}
        ):
    """where orbitals is a list of nw_orbital objects"""

    if isinstance(ax, type(None)):
        fig, ax = plt.subplots(1,1)
    #worstcase scenario: line length is whole plot width. 72 ppi
    ttmarkersize = 5
    xpointsN = int(fig.get_figwidth()*72/ttmarkersize)
   
    eventHandler = energy_level_ievents(fig, ax)
    handles = dict()



    for orbital in orbitals:
        matchDict = {}
        matchDict['E'] = orbital.E
        matchDict['occ'] = orbital.occ
        matchDict['spin'] = orbital.spin
        matchDict['isHOMO'] = orbital.isHOMO
        matchDict['isLUMO'] = orbital.isLUMO
        #Uses the most specific conditions
        maxmatches = 0
        curstyle = {}
        curstyleid = -1
        for i, tup in enumerate(conditions):
            conditionDict, style = tup
            matches = len([1 for key, val in matchDict.items() if key in conditionDict and conditionDict[key] == val])
            if matches > maxmatches:
                maxmatches = matches
                curstyle = style
                curstyleid = i
        
        #infolabel='({},{}):'.format(orbital.vector, orbital.spin)
        #if 'label' in curstyle:
        #    plotlabel = curstyle['label']
        #    infolabel += ':{}'.format(plotlabel)
        #    curstyle.pop('label') #Remove label cause we're going to use it to store information.
        curstyle.update(overwriteStyle) 
        A = ax.plot(np.linspace(0,1,xpointsN), [orbital.E for i in range(xpointsN)],  **curstyle)

        if interactive:
            #A[0].set_picker(), 
            #A[0].set_pickradius(2)
            A[0].set_markersize(ttmarkersize) 
            A[0].set_marker('s')
            A[0].set_markerfacecolor((1,1,1,0))
            A[0].set_markeredgecolor((1,1,1,0))
            eventHandler.add_artist(A, orbital)
        
        atomlabel = ''
        for atom in orbital.basisatoms:
            atomlabel += '{}:{},\n'.format(atom.id, atom.species)
        
        #tooltip = plugins.PointLabelTooltip(A[0], labels = ['E:{}, atoms:{}'.format(orbital.E, atomlabel) for i in range(xpointsN)])
        #tooltip = plugins.LineLabelTooltip(A[0], label = 'E:{}, occ:{}'.format(orbital.E, orbital.occ))
        #plugins.connect(fig, tooltip)
        
        if curstyleid not in handles:
            handles[curstyleid] = A[0]

    if interactive:
        eventHandler.setup_data()
        plugins.connect(fig, eventHandler)
    
    #pickwrapper = lambda event : eventHandler.orbital_pick_info(event) #Dunno why this is needed but doesn't work without it 
    #refreshwrapper = lambda event : eventHandler.refresh(event) #Dunno why this is needed but doesn't work without it 
    #fig.canvas.mpl_connect('pick_event', pickwrapper)
    #fig.canvas.mpl_connect('button_release_event', refreshwrapper)
    #eventHandler.connect_tooltip_plugin(fig)

    print(handles)
    if legend:
        ax.legend(handles=list(handles.values()))
   
    return fig, ax, list(handles.values())
