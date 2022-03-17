import numpy as np
import scipy as sp
import matplotlib
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins, utils
import nwchem_parse as nwparse
import time
from html.parser import HTMLParser

dist = lambda p1, p2: np.sqrt((p1-p2)**2)

figDict = dict()

class mpld3HTMLParser(HTMLParser):
    lastTag = None
    tagDict = {}
    
    def handle_starttag(self, tag, attrs):
        self.lastTag=tag
        self.tagDict[tag] = {'attrs':dict(attrs)}
    def handle_data(self, data):
        if data.strip() != '':
            self.tagDict[self.lastTag]['data'] = data

    def get_data(self, tag):
        if tag in self.tagDict:
            if 'data' in self.tagDict[tag]:
                return self.tagDict[tag]
            else:
                return None
        else:
            raise ValueError('plotutil.mpld3HTMLParser.get_data(): Tag not recognized: {}'.format(tag))


class replace_ticks(plugins.PluginBase):
    """So apparently mpld3 doesn't replace tick labels?? A minor detail but like. I wanna do it anyways"""
    JAVASCRIPT="""
    //Register and set up the empty plugin
    mpld3.register_plugin("tickmarks", TickMarkPlugin);
    TickMarkPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    TickMarkPlugin.prototype.constructor = TickMarkPlugin;
    TickMarkPlugin.prototype.requiredProps = ["xticks", "yticks"]; //arguements pulled from the python side.
    TickMarkPlugin.prototype.defaultProps = {} //keyword arguements
  
    //Constructor
    function TickMarkPlugin(fig, props){
        mpld3.Plugin.call(this, fig, props);
    }

    TickMarkPlugin.prototype.draw = function() {
        var obvconfig = {childList: true, subtree: true, attributes:true}
        var props = this.props
        var figid = this.fig.figid;
        var yaxis = d3.select('#'+figid).select(".mpld3-yaxis")
        var xaxis = d3.select('#'+figid).select(".mpld3-xaxis")
        updateAxis(props, xaxis, yaxis);
        //listen in for any changes to the axis and then reverse the changes
        var obv = new MutationObserver(function() {
                                                updateAxis(props, xaxis, yaxis);
                                                    })
        obv.observe(xaxis.node(), obvconfig);
        obv.observe(yaxis.node(), obvconfig);


    
    function updateAxis(props, xaxis, yaxis) {
        var yaxisticks = yaxis.selectAll(".tick").selectAll('text')
        var xaxisticks = xaxis.selectAll(".tick").selectAll('text')
        for (var j = 0; j < props.xticks.length; j++) {
            for (var i = 0; i < xaxisticks.length; i++) {
                var tick = xaxisticks[i][0]
                if (props.xticks[j][0] === tick.innerHTML) {
                    tick.innerHTML = props.xticks[j][1] 
                }
            }
        }
        
        for (var j = 0; j < props.yticks.length; j++) {
            for (var i = 0; i < yayisticks.length; i++) {
                var tick = yayisticks[i]
                if (props.yticks[j][0] === tick.innerHTML) {
                    tick.innerHTML = props.yticks[j][1] 
                }
            }
        }

    }
    }

    """

    def __init__(self, fig, ax, xticks = [], xticklabels = [], yticks = [], yticklabels = [], roundTicks=True):
        self._fig = fig
        self._ax = ax
        self._xticks = [str(val) for val in xticks]
        self._xticklabels =[str(val) for val in  xticklabels]
        self._yticks =[str(val) for val in  yticks]
        self._yticklabels =[str(val) for val in  yticklabels]
        if roundTicks:
            #This is a horrible abuse of type conversions I'm so sorry.
            self._xticks.extend([str(int(np.ceil(float(val)))) for val in self._xticks])
            self._yticks.extend([str(int(np.ceil(float(val)))) for val in self._yticks])
            self._xticklabels.extend(self._xticklabels)
            self._yticklabels.extend(self._yticklabels)
            print(self._xticks)
        self.dict_=dict()
        
        self._setup()

    def _setup(self):
        self.dict_ = {
                'type': 'tickmarks',
                'xticks' : list(zip(self._xticks, self._xticklabels)), 
                'yticks' : list(zip(self._yticks, self._yticklabels)) 
                }
        print(self.dict_)

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
    EnergyLevelsPlugin.prototype.requiredProps = ["spinMarkers", "selectMarkers", "levelLines", "data", "infolabels"]; //arguements pulled from the python side.
    EnergyLevelsPlugin.prototype.defaultProps = {} //keyword arguements

    //Constructor
    function EnergyLevelsPlugin(fig, props){
        mpld3.Plugin.call(this, fig, props);

        //add figure specific css
        mpld3.insert_css('#' + fig.figid + " path.hover ",
                        {"stroke-width": "3.0"});
    }


    //Called upon rendering.
    EnergyLevelsPlugin.prototype.draw = function(){
        //this.fig -> figure
        //this.props.VARIABLE_NAME
       
        //create extra HTML objects using d3
       
        var figdiv = d3.select('#'+this.fig.figid)
                                        .attr("class", "plotdiv")
                                        .style('display', 'flex')
                                        .style('flex-direction', 'row')

        //var eleveldiv = d3.select(this.id).append('div', 'b')
        //                                .attr("class", "figContainer")
       
        //use .node() to get the actual html element
        //eleveldiv.node().appendChild(figdiv.node())
        
        var infodiv = figdiv
                        .append("div")
                            .attr("class", "infodiv")
                            .attr("name", "orbitalinfo")
                            .style("height", 200)
                            .style("width", "100%")
                            .style('flex', 1)
        
        for (var i = 0; i < this.props.infolabels.length; i++) {
            var labelinfo = this.props.infolabels[i];
            if ( labelinfo.key === 'heading') {
                infodiv.append("h1")
                    .attr("class", "infoheading")
                    .text(labelinfo.text) 

            } else {
                infoline = infodiv.append('div')
                    .attr("class", "infoline")
                infoline.append("p")
                    .attr("class", "infolabel")
                    .text(labelinfo.text+': ')
                infoline.append("p")
                    .attr("class", "infotext")
                    .attr("id", labelinfo.key)
            }
        }

        
                
        textE = d3.select("#E")
        textocc = d3.select("#occ")
        textvector = d3.select("#vector")
        textspin = d3.select("#spin")
        textbasisatoms = d3.select("#basisatoms")
        textcenter = d3.select("#center")
        textr2 = d3.select("#r2")
        textbasisfuncs = d3.select("#basisfuncs")
       
        function foo(event){
            console.log('click!');
        }

        var objList = []

        for (var i=0; i < this.props.levelLines.length; i++) {
            var lineObj = mpld3.get_element(this.props.levelLines[i], this.fig);
            var data = this.props.data[i];
            var line = lineObj.path[0][0]
            line.setAttribute('select', false);
            line.addEventListener('mouseover', onHover.bind(null, line, data)); 
            line.addEventListener('mouseout', offHover.bind(null, line, data)); 
        }
        //for (var i=0; i < this.props.selectMarkers.length; i++) {
        //    //var lineObj = mpld3.get_element(this.props.levelLines[i], this.fig);
        //    var ghostObj = mpld3.get_element(this.props.selectMarkers[i], this.fig);
        //    //var spinsObj = mpld3.get_element(this.props.spinMarkers[i], this.fig);
        //    var data = this.props.data[i];
        //    
        //    var a = this.props.levelLines[i]
        //    // get_element might return null if the id is a Line2D for some reason. 
        //    //data.lineObj = lineObj 
        //    //data.spinsObj = spinsObj
        //    console.log(ghostObj);
        //    ghostObj.elements()
        //        .datum(data)
        //        .on("mouseover", function(d,j) {
        //                            d.lineObj.elements()
        //                                .style("stroke-width", 10);
        //                            changeText(d, j);
        //                        })
        //        .on("mouseout", function(d,j) {
        //                            d.lineObj.elements()
        //                                .style("stroke-width", d.markersize);
        //                            changeText(d, j);
        //                        })
        //}
        
        //d is the datum, specifies points and stuff. i is the index within d of the point just touched.
        function onHover(obj, d){
            //changeText(d);
            obj.style['stroke-width']=10;
            changeText(d);
        }
        function offHover(obj, d){
            obj.style['stroke-width']=d.linewidth;
        }
        
        function onClick(obj, d){
            console.log(obj);
            changeText(d);
            obj.setAttribute('select', true);
            obj.style['stroke-width']=d.linewidth;
        }

        function changeText(d){
            textE.text(d.E);
            textocc.text(d.occ);
            textvector.text(d.vector);
            textspin.text(d.spin);
            textbasisatoms.text(d.basisatoms);

        }
        

    }

    """

    css_="""
    .figContainer{
        display:grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr;
    }
    #plotdiv div{
        float: left;
    }
    .infolabel {
        display:inline;
    }
    .infotext {
        display:inline;
    }
    """


    def append_infolabel(self, key, text):
        self.infolabels.append({'key':key, 'text':text})

    def __init__(self, fig, ax):
        self._fig = fig
        self._ax = ax
        self._artistsDict = dict() #{artist:orbital}
        self._refreshcalls = 0
        #Javascript stuff.
        self.dict_ = dict()
        
        self.infolabels=[]
        
        self.append_infolabel('heading', 'Properties')
        
        self.append_infolabel('E','Energy')
        self.append_infolabel('occ','Occupancy')
        self.append_infolabel('spin', 'Spin')
        
        self.append_infolabel('heading', 'Location')
        
        self.append_infolabel('basisatoms','Basis Atoms')
        self.append_infolabel('center','Center')
        self.append_infolabel('r2', 'R^2')
        
        self.append_infolabel('heading', 'Basis Functions')
        self.append_infolabel('vector','DFT Vector')
        self.append_infolabel('basisfuncs','Basis Funcions')
        
        #self.append_infolabel('ms', 'ms')
        #self.append_infolabel('isHOMO', 'HOMO:')
        #self.append_infolabel('isLUMO', 'LUMO:')

#Write this up to interpolate arbitrary lines
#    def _gen_ghost_markers(line2D,pointMult = 3, marker = 'o', markersize=5,visible=False):
#        xy = line2D.get_xydata()
#        segLens = [dist(xy[i,:], xy[i+1, :]) for i in range(xy.shape[0]-1)]
#        totDist = sum(segLens)
#        totDist = sum(segLens)
#        N = int(xy.shape[0]*pointMult) #How many more interpolated points there will be.
#        step = N/segLens #dist between points
#        
#        newX=np.zeros(N)
#        newY=np.zeros(N)
#        lastNewPointDist = 0
#        lastPointDist = 0
#
#        for i in range(xy.shape[0]):
#            s = 
#            
    
    def _plot_ghost_markers(self,line2D, marker = 'o', markersize=5,visible=True):
        #Currently assumes flat line
        x = line2D.get_xdata()
        y = line2D.get_ydata()
        
        xlo, xhi = self._ax.get_xlim()
        
        xpointsN = int(self._fig.get_figwidth()*(np.abs(x[0]-x[-1]) / np.abs(xlo-xhi))*72/markersize)
        newx = np.linspace(x[0], x[-1], xpointsN)
        newy = np.zeros(newx.size) + y[0]
        ghostScatter = self._ax.scatter(newx, newy, marker=marker, s=markersize) 
       
        if not visible: 
            ghostScatter.set_edgecolor((1,1,1,0))
            ghostScatter.set_facecolor((1,1,1,0))
        return ghostScatter
            
    def _plot_spin_markers(self,line2D, orbital, offset=0.1,markersize=5):
        x = line2D.get_xdata()
        xlo = x[0]
        xhi = x[-1]
        xtick = (xlo + xhi)/2
        if orbital.occ > 0:
            if orbital.spin == 0.5:
                A = self._ax.scatter([xtick-offset], [orbital.E], marker = '$↑$', s = markersize, c=line2D.get_color())

            elif orbital.spin == -0.5:
                A = self._ax.scatter([xtick+offset], [orbital.E], marker = '$↓$', s = markersize, c=line2D.get_color())
            else:
                A = self._ax.scatter([xtick], [orbital.E], marker = 'o', s = markersize, c=line2D.get_color())
        else:
                A = self._ax.scatter([xtick], [orbital.E], s = 0 )
        return A

    def add_artist(self, artist, orbital, **kwargs):
        """Appends things like Line2D and what not"""
        if isinstance(artist, list):
            for a in artist:
                self._artistsDict[a] = orbital
        else:
            self._artistsDict[artist] = orbital
   
    def setup_data(self, spinMarkerSize=5, visibleGhosts=True):
        """This sets up all the data and element ids for usage in the javascript protion"""
        items = self._artistsDict.items()
        artists = []
        orbitalDat = []
        
        self.dict_["type"] ="energylevels"
        self.dict_["infolabels"] = self.infolabels 
        
        self.dict_["levelLines"] = []
        self.dict_["selectMarkers"] = []
        self.dict_["spinMarkers"] = [] 
        self.dict_["data"] = [] 
        
        for tup in items:
            a, orb = tup
            #ghost = self._plot_ghost_markers(a, visible = visibleGhosts)
            #spins = self._plot_spin_markers(a, orb, markersize=spinMarkerSize)
            if isinstance(a, matplotlib.lines.Line2D): suffix = 'pts'
            else: suffix = None
            suffix=None
            #self.dict_['spinMarkers'].append(utils.get_id(spins))
            #self.dict_['selectMarkers'].append(utils.get_id(ghost))
            self.dict_['levelLines'].append(utils.get_id(a, suffix))
            dat = orb.get_data()
            dat.update({'linewidth':a.get_linewidth(),
                        'linecolor':a.get_color(),
                        })
            self.dict_['data'].append(dat)
        #print(self.dict_['levelLines'])


    def connect_tooltip_plugin(self, fig = 'self'):
        if fig == 'self': fig = self._fig
        artists = [tup[0] for tup in self._artistsDict.items()]
        orbitalDat = ["E:{}, occ:{}".format(tup[1].E, tup[1].occ) for tup in self._artistsDict.items()]
        print('Connecting')
        for artist, orbital in self._artistsDict.items():
            tooltip = plugins.LineLabelTooltip(artist, label = 'E:{}, occ:{}'.format(orbital.E, orbital.occ))
            #print(artist, tooltip)
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


def plot_atom_distances(atom, ax=None, species=None, bins=50, **kwargs):
    if isinstance(ax, type(None)): fig, ax = plt.subplots(1,1)
    else: fig = ax.figure
    if isinstance(species, str): species = [species]
    neighborAtoms = atom.get_neighbors_by_dist()
    speciesDict = dict()
    distRange = [np.inf, -np.inf]
    for i, tup in enumerate(neighborAtoms):
        natom = tup['atom']
        dist = tup['dist']
        if natom.species not in speciesDict:
            speciesDict[natom.species] = []
        speciesDict[natom.species].append(dist)
        if dist < distRange[0]: distRange[0] = dist
        if dist > distRange[1]: distRange[1] = dist
    
    for atomSpecies, vals in speciesDict.items():
        if isinstance(species, (tuple, list)):
            if atomSpecies not in species:
                continue
        ax.hist(vals, label=atomSpecies, range=distRange, bins=bins, **kwargs)
    
    ax.set_xlabel('Distance (Angstrom)')
    ax.set_ylabel('Counts')
    ax.legend()
    return fig, ax

def plot_total_energies(parsers,  ax = None, **kwargs):
    """takes in a list of nwchem parsers"""
    if isinstance(ax, type(None)): fig, ax = plt.subplots(1,1)
    else: fig = ax.figure

    if isinstance(parsers, nwparse.nwchem_parser):
        parsers = [parsers]
    xvals = []
    yvals = []
    for i, parser in enumerate(parsers):
        try:
            yvals.append(parser.dft_energies['total'])
            xvals.append(i)
        except KeyError:
            continue
    print(xvals, yvals)
    ax.plot(xvals, yvals, **kwargs)
    
    return fig, ax

def plot_energy_level(orbitals, fig = None, ax = None, legend=False, xlevel=0, xlabel=None,
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
    if not ax.lines: #If the axis is freshly created, nuke the xlabels
        #print('hi')
        ax.set_xticks([])
        ax.set_xticklabels([])
    #worstcase scenario: line length is whole plot width. 72 ppi
    ttmarkersize = 5
    #xpointsN = int(fig.get_figwidth()*72/ttmarkersize)
    xpointsN = 2 
   
    if isinstance(xlevel, (list, tuple, np.ndarray)):
        xlo = xlevel[0]
        xhi = xlevel[1]
    else:
        xlo = xlevel
        xhi = xlo + 1
    xtick = (xhi + xlo)/2
    
    xticks = list(ax.get_xticks())
    xlabels = [text.get_text() for text in ax.get_xticklabels()]
    if not isinstance(xlabel, type(None)):
        xticks.append(xtick)
        xlabels.append(xlabel)
        print(xlabels, xticks) 
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels)

    #To avoid duplication
    if utils.get_id(fig) not in figDict.keys():
        eventHandler = energy_level_ievents(fig, ax)
        figDict[utils.get_id(fig)] = eventHandler
        doPluginConnect = True
    else:
        eventHandler = figDict[utils.get_id(fig)]
        doPluginConnect = False
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
        A = ax.plot([xlo,xhi], [orbital.E, orbital.E],  **curstyle)
        #A = ax.plot(np.linspace(xlo,xhi,xpointsN), [orbital.E for i in range(xpointsN)],  **curstyle)
        #if orbital.spin == 0.5:
        #    A = ax.plot([xlo,xtick-0.1,xhi], [orbital.E for i in range(3)],  **curstyle)
        #    A[0].set_markersize(ttmarkersize) 
        #    A[0].set_marker('$↑$')

        #elif orbital.spin == -0.5:
        #    A = ax.plot([xlo,xtick+0.1,xhi], [orbital.E for i in range(3)],  **curstyle)
        #    A[0].set_markersize(ttmarkersize) 
        #    A[0].set_marker('$↓$')
        #else:
        #    A = ax.plot([xlo,xtick,xhi], [orbital.E for i in range(3)],  **curstyle)
        #    A[0].set_markersize(ttmarkersize) 
        #    A[0].set_marker('o')
            


        

        if interactive:
            #A[0].set_picker(), 
            #A[0].set_pickradius(2)
            #A[0].set_markersize(ttmarkersize) 
            #A[0].set_marker('s')
            #A[0].set_markerfacecolor((1,1,1,0))
            #A[0].set_markeredgecolor((1,1,1,0))
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
        eventHandler.setup_data(visibleGhosts=False)
    if doPluginConnect: 
        plugins.connect(fig, eventHandler)
    rticks = replace_ticks(fig, ax, xticks = xticks, xticklabels = xlabels)
    plugins.connect(fig, rticks)
    
    #pickwrapper = lambda event : eventHandler.orbital_pick_info(event) #Dunno why this is needed but doesn't work without it 
    #refreshwrapper = lambda event : eventHandler.refresh(event) #Dunno why this is needed but doesn't work without it 
    #fig.canvas.mpl_connect('pick_event', pickwrapper)
    #fig.canvas.mpl_connect('button_release_event', refreshwrapper)
    #eventHandler.connect_tooltip_plugin(fig)

    print(handles)
    if legend:
        ax.legend(handles=list(handles.values()))
   
    return fig, ax, list(handles.values())


