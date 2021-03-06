


//resuable

//rect components have 1. render, 2. props (defined by caller), 3. state (instance data that can change). If a component's states change, it rerenders
//React.createElement("DOMtype", {attributes}, [CHILDREN] 

//const listComponent(props) {
//        return React.createElement('h1', {'className':'listElement'}, props.name)
//}

//function complexListItem (props) {
//        return React.createElement('div', {'className':'listElement', 'key':props.key},
//                React.createElement('p', null, props.name,)
//        );
//}
//
//class complexList extends React.Component{
//        constructor(props){
//                super(props);
//                this.state={complexes:[]};
//                this.state.complexes.push(...props.complexes);
//        }
//
//	//This gets called when ReactDOM renders it
//	render() {
//                var elements = new Array();
//                for (var i = 0; i < this.state.complexes.length; i++) {
//                        var val = this.state.complexes[i];
//                        elements.push(complexListItem({'name': val, 'key':val.toString()}))
//                }
//
//		return React.createElement('div', null, elements);
//	}
//}
//
//class reactButton extends React.Component{
//        constructor(props){ //called when initialized. Use it to set defaults
//                super(props);
//        }
//        render() {
//                return React.createElement('div', {'className':'divButton', 'onClick':this.props.onClick}, `${this.props.name}`)
//        }
//}


//Requires: props.name, props.cb (callback function), index
function listElement (props) {
        if (props.key === undefined){
                var key = props.name;
        } else{
                var key = props.key;
        };
        var onClick = function (e) {
                var target = e.target
                var i = parseInt(target.getAttribute('index'))
                props.cb(i);
                return i
        }
        var active = ''
        if (props.active === true) {
                active = 'active'
        }
        return React.createElement('button', {'className':`list-group-item btn-sm ${active}`, 'key':key, 'onClick':onClick, 'index':props.index}, props.name)
}

class complexList extends React.Component{
        constructor(props){
                super(props);
                this.state = {};
                this.state.complexes=[]; 
                this.currentActive = null;
                this.currentActiveIndex = null;
                //process on load
                if (typeof props.complexes != 'undefined'){
                        this.push(props.complexes);
                }
                if (typeof props.json != 'undefined'){
                        this.loadFromJson(props.json);
                }
                //bind functions to each instance
                this.push.bind(this);
                this.loadFromJson.bind(this);
                this.setAllUnActive.bind(this);
                this.cb.bind(this);
                this.renderElements.bind(this);
                this.getSelected.bind(this);
        }

        push (val){
                if (!(val instanceof Array)) {
                        var values = [val]
                } else {
                        var values = val
                }

                if (typeof val != 'undefined') {
                        var tempState = {...this.state}
                        for (var i = 0; i < values.length; i++) {
                                tempState.complexes.push({'complex':values[i], 'active':false});
                        this.setState(tempState);

                        }
                }
        }

        loadFromJson(json){
                if (typeof json === 'string') {
                        var dataArray = JSON.parse(JSON.parse(json));
                        this.push(dataArray);
                }
        }

        //Callback, like giving a reference to a child so they can call back to a parent. make sure to bind your callback function!
        setAllUnActive () {
                var tempState = {...this.state}
                for (var i = 0; i < tempState.complexes.length; i++){
                        this.state.complexes[i].active= false;
                }
                tempState.currentActive= null;
                tempState.currentActiveIndex= null;
                this.setState(tempState);

        }

        getComplexes() {
                return(this.state.complexes)
        }
        //returns the current selected item.
        getSelected () {
                if (typeof this.state.currentActive != 'undefined'){
                        return(this.state.currentActive.complex)
                }
        }

        removeSelected () {
                var tempState = {...this.state}
                var i = this.state.currentActiveIndex;
                if (typeof i === 'number') {
                        tempState.complexes.splice(i, 1);
                        if (i < tempState.complexes.length) {
                                var newActive = tempState.complexes[i];
                                newActive.active=true;
                                tempState.currentActive = newActive;
                                this.setState(tempState);
                        }else{
                                this.setState(tempState);
                                this.setAllUnActive()
                        }
                }
                //this.setAllUnActive()
        }


        cb (index){
                this.setAllUnActive()
                var tempState = {...this.state}
                tempState.complexes[index].active = true
                tempState.currentActive=tempState.complexes[index];
                tempState.currentActiveIndex = index
                this.setState(tempState);
        }

        renderElements(){
                var children = [];
                for (var i = 0; i < this.state.complexes.length; i++){
                        var data = this.state.complexes[i]
                        children.push(listElement({'name': data.complex, 'key':`${data.complex}-${i}`, 'index':i, 'active':data.active, 'cb':this.cb.bind(this),} ));
                }
                return children
        }


        render() {
                var children = new Array()
                if (this.props.title) {
                        children.push(React.createElement("b", {'className':'listTitle'}, this.props.title));
                }
                children.push(...this.renderElements())
                var ele = React.createElement("div", {'className':"list-group",}, children);
                return ele
        }
}


function reactButton(props){
        if (props.key === undefined){
                var key = props.name;
        } else{
                var key = props.key;
        };
        var onClick = function (e) {
                var target = e.target
                props.cb(props.action);
                return props.action
        }
        var active = ''
        if (props.active === true) {
                active = 'active'
        }
        return React.createElement('button', {'className':`btn btn-primary ${active}`, 'key':key, 'onClick':onClick, 'style':{'margin-right':'0.25em',}}, props.name)
}

//Requires: props.name, props.cb (callback function), 
function dropdownElement (props) {
        if (props.key === undefined){
                var key = props.name;
        } else{
                var key = props.key;
        };
        var onClick = function (e) {
                var target = e.target
                var name = target.textContent
                props.cb(name);
                return name
        }
        var active = ''
        if (props.active === true) {
                active = 'active'
        }
        return React.createElement('button', {'className':`list-group-item btn-sm ${active}`, 'key':key, 'onClick':onClick}, props.name)
}

//requires props.key, props.name, props.items, props.cb
class reactDropdown extends React.Component{
        constructor(props){
                super(props);
                this.state = {}
                this.state.items = new Map;
                this.state.currentActive = undefined;
                this.state.supercb = props.cb //The call back to the original object. reactDropdown intercepts it to update elements.
                this.state.name = props.name
                if (props.key === undefined){
                        var key = props.name;
                } else{
                        var key = props.key;
                };
                //this.state.listElement=this.renderElements(); 
                
               
        }

        push(val){
                if (!(val instanceof Array)) {
                        var values = [val]
                } else {
                        var values = val
                }

                if (typeof val != 'undefined') {
                        var tempState = {...this.state}
                        for (var i = 0; i < values.length; i++) {
                                this.state.items.set(val[i], {'active':false});
                        this.setState(tempState);

                        }
                }
        }

        renderElements(){
                var elementArray = []
                var items = Array.from(this.state.items.entries())
                for (var i = 0; i < items.length; i++) {
                        var complex = items[i][0]
                        var tup = items[i][1]
                        elementArray.push(React.createElement(dropdownElement, {'key':i, 'name':complex, 'cb':this.cb.bind(this), 'active':tup.active}, null));
                }
                return React.createElement('ul', {'className':'dropdown-menu', 'aria-labelledby':'dropdownMenuLink'}, elementArray);

        }
       
        unsetAll(){
                var tempState = {...this.state}
                var keys = this.state.items.keys()
                for (var i = 0; i < this.state.items.size; i++){
                        tempState.items.get(keys.next().value).active=false
                }
                tempState.currentActive = undefined;
                this.setState(tempState);
        }
        cb (val){
                this.unsetAll()
                var tempState = {...this.state}
                tempState.items.get(val).active=true
                tempState.currentActive=val
                this.setState(tempState);
                this.state.supercb(val);
        }
        render(){
                if (this.state.items.size < this.props.items.length){
                        this.push(this.props.items);
                }
                 
                return React.createElement('div', {'className':'dropdown'}, [
                        React.createElement('a', {
                                'className': 'btn btn-primary dropdown-toggle', 
                                'href':'#', 
                                'role':'button',
                                'data-bs-toggle':'dropdown',
                                'aria-expanded':'false',
                        }, this.state.name),
                        this.renderElements(),
                        
                        
                ])
        }

}

class selectControls extends React.Component{
        constructor(props){
                super(props);
                this.state = {}
                this.state.plotFuncs = new Map();
        }
        
        cb (action) { //given to the buttons
                switch(action){
                        case 'add':
                                var complex = this.state.getInputSelected()
                                this.state.pushOutput(complex);
                                break;
                        case 'remove':
                                this.state.removeSelected()
                                break;
                        case 'plot':
                                this.plotSelected();
                                break;
                        default:
                                console.log(`selectControls: Unknown action ${action}`)
                }
        }

        setInputList(cList){
                var tempState = {...this.state}
                tempState.getInputSelected = cList.getSelected.bind(cList);
                this.setState(tempState);
        }

        setOutputList(oList){
                var tempState = {...this.state}
                tempState.pushOutput = oList.push.bind(oList);
                this.setState(tempState);
        }

        setRemoveList(rList){
                var tempState = {...this.state}
                tempState.removeSelected = rList.removeSelected.bind(rList);
                this.setState(tempState);
        }

        setPlotList(pList){
                var tempState = {...this.state}
                tempState.getPlotComplexes = pList.getComplexes.bind(pList); //binds it to the specific method within the list
                this.setState(tempState);
        }

        //method references to plot divs to push info into them
       
        setPlotHandler(plotType, pDiv){
                var tempState = {...this.state}
                tempState.plotFuncs.set(plotType, pDiv.setHTML.bind(pDiv)); //binds it to the specific method within the list
                this.setState(tempState);
        }

        plotSelected() {
                var complexes = this.state.getPlotComplexes()
                
                var plotType='all' //expand this later on to multiple plot types in control
                var plotFuncs = this.state.plotFuncs
                
                var complexNames = []
                for (var i = 0; i < complexes.length; i++){
                        complexNames.push(complexes[i].complex);
                }
                var plotRow = document.getElementById('plotRow');
                plotRow.innerHTML = '';
                setupPlotRow(); //Reset all plots



                var dataStr = JSON.stringify({'plotType':plotType,'complexList':complexNames, 'orbitalSpecies':document.getElementById('orbitalSpeciesInput').value, 'viewSize':[window.innerWidth, window.innerHeight]});
                $.ajax({
                  method: "POST",
                  url:"/api/plots", //use this to define which api you're talking to
                  data: dataStr, 
                  success: function (data) {
                        var plotData = Object.entries(data);
                        //console.log(json);
                        for (var i = 0; i < plotData.length; i++){
                                var pair = plotData[i];
                                var plotFunc = plotFuncs.get(pair[0]); //Plottype
                                console.log(plotFuncs);
                                plotFunc(JSON.parse(pair[1])); //plot data
                        }
                        },
                  dataType: "json"
                });

        }


        render(){
                var children = [];
                children.push(React.createElement('div', {'key':'selectButtons', 'style':{'flex':1} }, [
                        React.createElement(reactButton, {'key':'Add', 'name':'Add', 'action':'add', 'cb':this.cb.bind(this)}, null),
                        React.createElement(reactButton, {'key':'Remove', 'name':'Remove', 'action':'remove', 'cb':this.cb.bind(this)}, null),
                        React.createElement(reactButton, {'key':'Plot', 'name':'Plot', 'action':'plot', 'cb':this.cb.bind(this)}, null),
                        ]));
                children.push(React.createElement('div', {'key':'selectForm', 'style':{'flex':1} }, [
                        React.createElement('input', {'key': 'species', 'id': 'orbitalSpeciesInput', 'className':'form-control', 'type':'text', 'placeholder':'Filter Orbitals by Species (Seperate by Commas)', 'defaultValue':'La, S'}, null),

                        ]));
                return(React.createElement('div', {'id':'selectControls', 'style':{'display':'flex', 'flexDirection':'column', 'style':{'padding':'0.25em'}}}, children));
        }
}

//So HTML5 does not allow for scripts to run within innerHTML
//The solution to this is to create a new script element and append the script text as a child


class plotDiv extends React.Component{
        constructor (props) {
                super(props);
                this.state = {};
                this.state.id = 'plot_figure_'+props.id.toString();
                this.state.div={};
                this.state.script={};
                this.state.style={};
                if (typeof props.json === 'object') {
                        this.setHTML(props.json);
                }
        }

        _getHTML(html){
                return {__html:html}
        }

        setHTML(json){
                var tempState = {...this.state}
                tempState.div = json.div
                tempState.script = json.script
                tempState.style = json.style
                this.setState(tempState);
                this.renderPlot()
        }
        renderPlot() {
                //Adds some normal HTML stuff as a node to the React element.
                var plotContainer = document.getElementById(this.state.id)
                plotContainer.textContent=''; //clears the div
                var plotScript = document.createElement('script')
                if (typeof this.state.script.data != 'undefined') {
                        plotScript.appendChild(document.createTextNode("import { plotHandlerRef } from '/static/control.js';\n"));
                        var inlineScript = document.createTextNode(this.state.script.data);
                        plotScript.appendChild(inlineScript);
                }
                //for passing in references to other plot modules using plotHandlerRef
                plotScript.setAttribute('type', 'module');
                
                var plotStyle = document.createElement('style') 
                if (typeof this.state.style.data != 'undefined') {
                        var inlineStyle = document.createTextNode(this.state.style.data);
                        plotStyle.appendChild(inlineStyle);
                }
                var plotDiv = document.createElement('div')
                plotDiv.setAttribute('id', this.state.div.attrs.id)
                if (typeof this.state.div.data != 'undefined') {
                        var inlineDiv = document.createTextNode(this.state.div.data);
                        plotDiv.appendChild(inlineDiv);
                } 
                plotContainer.appendChild(plotStyle);
                plotContainer.appendChild(plotDiv);
                plotContainer.appendChild(plotScript);

        }
        render() {

                return(React.createElement('div', {'className':'plotContainer', 'id':this.state.id})) 
        }

}

//Chemdoodle components

class tablePlot extends React.Component{
        constructor(props) {
                super(props)
                this.state = {}
                this.state.data = new Map; //'structkey':[{'label':'str', 'headers':[...data], 'data':[{'label':'rowlabel', data:[...], ...]}]
                this.state.children = []; 
                if (typeof props.json === 'object') {
                        this.setHTML(props.json);
                }
        }

        renderTables(key) {
        //Returns list of inner children
                var tempState = {...this.state}
                var children = [];
                var dataArray = this.state.data.get(key);
                console.log('renderTables', key, dataArray);
                if (typeof dataArray === 'undefined') {return children}
                for (var k = 0; k < dataArray.length; k++) {
                        var data = dataArray[k];
                        console.log('lets go', data)
                        //create all children and shove them into div at the end.
                        var childrenTable = [];
                        //var key = pair[0];
                        //var data = pair[1];
                        //label
                        if (typeof data.label != 'undefined') {
                                childrenTable.push(React.createElement('h4', {'className':'infoheading', 'key':'h4-'+k}, data.label));
                        }
                        //create table rows
		        var rows = [];
                        for (var i = 0; i < data.data.length; i++){
                                var rowObj = data.data[i];
                                var rowChildren = [];
                                rowChildren.push(React.createElement('th', {'scope':'row', 'key':'th-'+k+'-'+i}, rowObj.label))
                                for (var j = 0; j < rowObj.data.length; j++) {
                                        rowChildren.push(React.createElement('td', {'scope':'row', 'key':'td'+k+'-'+j+'-'+k}, rowObj.data[j]));
                                }
                                rows.push(React.createElement('tr', {'key':'tableRow'+i.toString(), 'key':'tr'+k+'-'+i}, rowChildren));
                        }
                        var headers = [];
                        for (var i = 0; i < data.headers.length; i++){
                                var header = data.headers[i];
                                headers.push(React.createElement('th', {'scope':'row', 'key':'header-th-'+k+'-'+i}, header))
                                
                        
                        }
                        //Create table head + add row
                        childrenTable.push(React.createElement('table', {'className':'table'}, [
                                        React.createElement('thead', {'key':'header-'+k}, [
                                                React.createElement('tr', {'key':'headerRow-'+k}, headers)
                                        ]),
                                        React.createElement('tbody', {'key':'tableBody-'+k}, rows)
                        ]));
                        children.push(React.createElement('div', {'key':'tableDiv', 'style':{'paddingRight':'1em'}, 'key':'table-'+k, }, childrenTable));
                }
                tempState.children = children; 
                this.setState(tempState);
        }

        setHTML(json){
                //takes in data from the backend
                var tempState = {...this.state}
                var pairs = Object.entries(json);
                for (var i = 0; i < pairs.length; i++){
                        var pair = pairs[i];
                        var key = pair[0];
                        var dat = pair[1];
                        tempState.data.set(key, dat);
                }
                this.setState(tempState);
        }

        render() {

                return React.createElement('div', {'id': this.state.id, 'className': 'tableContainer', 'style':{'display':'flex','flexDirection':'row', 'flexWrap':'wrap' }}, this.state.children)

        }

}


class chemdoodlePlot extends React.Component{
        constructor(props){
                super(props)
                this.state = {}
                this.state.id = 'canvas_figure_'+props.id.toString();
                var canvasType = props.canvasType;
                if (typeof canvasType === 'string'){
                        this.state.canvasType = canvasType; 
                } else {
                        this.state.canvasType = 'Ball and Stick';
                }
                this.state.molecules = new Map;
                this.state.energies = new Map;
		this.state.selectedAtoms = new Map; //key : [array]
                this.state.activeKey = undefined;


        }

        renderControlDiv(){
                if (typeof this.state.canvas !== 'undefined'){
                        var keys = Array.from(this.state.molecules.keys());
                        //console.log('hello', keys);
                        var tempState = {...this.state}

			var children = [];
                        var childrenDiv1 = []; //Complex Selection Div
                        var childrenDiv2 = []; //Energies 
                        var childrenDiv3 = []; //Atom Count
                        childrenDiv1.push(React.createElement(reactDropdown, {'name':'Complex', 'items':keys, 'cb':this.cb.bind(this)}, null))
			if (typeof tempState.activeKey === 'string') {
				childrenDiv1.push(React.createElement('h2', {'className':'infoheading'}, 'Complex'))
				childrenDiv1.push(React.createElement('div', {'className':'infoline'},
					[React.createElement('p', {'className': 'infotext'}, tempState.activeKey),
					]));
                                //children.push(React.createElement('h2', {'className':'infoheading'}, 'Info'))
				
                                //Energies
				//var pairs = Object.entries(this.state.energies.get(this.state.activeKey));
                                ////console.log(this.state.energies);
				//for (var i = 0; i < pairs.length; i++){
				//	var pair = pairs[i];
				//	childrenDiv2.push(React.createElement('div', {'className':'infoline'},[
				//		React.createElement('p', {'className': 'infolabel'}, pair[0].toString()+': '), 
				//		React.createElement('p', {'className': 'infotext'},   pair[1].toString()),
				//		]));
				//}

				//var mol = tempState.molecules.get(tempState.activeKey)
				//
                                //var rows = [];
                                ////Create table body
				//var pairs = Object.entries(this.state.energies.get(this.state.activeKey));
				//for (var i = 0; i < pairs.length; i++){
				//	var pair = pairs[i];
				//	rows.push(React.createElement('tr', {'key':'tableRow'+i.toString()}, [
				//		React.createElement('th', {'scope':'row', 'key':'E'+i.toString()}, pair[0].toString()),
				//		React.createElement('td', {'key':'Eval'+i.toString()}, pair[1].toString()),
				//	]));
				//}
                                ////Create table head + add row
				//childrenDiv2.push(React.createElement('table', {'className':'table'}, [
				//		React.createElement('thead', {'key':'tableHead'}, [
				//			React.createElement('tr', {'key':'headerRow'}, [
				//				React.createElement('th', {'scope':'row', 'key':'species'}, 'Type'),
				//				React.createElement('th', {'scope':'row', 'key':'count'}, '(Hartree, a.u.)'),
				//			]),
				//		]),
				//		React.createElement('tbody', {'key':'tableBody'}, rows)
				//]));
				//
				////Count up number of atoms	
				//if (typeof mol.count === 'undefined'){
				//	mol.count = {};
				//	for (var i = 0; i < mol.atoms.length; i++){
				//		var a = mol.atoms[i];
				//		if (typeof mol.count[a.label] === 'undefined') {
				//			mol.count[a.label] = 1;
				//		} else {
				//			mol.count[a.label] = mol.count[a.label] + 1;
				//		}
				//	}
				//	
				//}

				//var rows = [];
                                ////Create table body
                                //rows.push(React.createElement('tr', {'key':'tableRowTot'}, [
				//	React.createElement('th', {'scope':'row', 'key':'spectotal'}, 'Total'),
				//	React.createElement('td', {'key':'counttotal'}, mol.atoms.length.toString()),
				//]));
				//var pairs = Object.entries(mol.count);
				//for (var i = 0; i < pairs.length; i++){
				//	var pair = pairs[i];
				//	rows.push(React.createElement('tr', {'key':'tableRow'+i.toString()}, [
				//		React.createElement('th', {'scope':'row', 'key':'spec'+i.toString()}, pair[0].toString()),
				//		React.createElement('td', {'key':'count'+i.toString()}, pair[1].toString()),
				//	]));
				//}
                                ////Create table head + add row
				//childrenDiv3.push(React.createElement('table', {'className':'table'}, [
				//		React.createElement('thead', {'key':'tableHead'}, [
				//			React.createElement('tr', {'key':'headerRow'}, [
				//				React.createElement('th', {'scope':'row', 'key':'species'}, 'Species'),
				//				React.createElement('th', {'scope':'row', 'key':'count'}, 'Count'),
				//			]),
				//		]),
				//		React.createElement('tbody', {'key':'tableBody'}, rows)
				//]));


				
			}
                        //add in all divisions
                        children.push(React.createElement('div', {'key':'div1', 'style':{'padding':'1em'}}, childrenDiv1));
                        //children.push(React.createElement('div', {'key':'div2', 'style':{'padding':'1em'}}, childrenDiv2));
                        //children.push(React.createElement('div', {'key':'div3', 'style':{'padding':'1em'}}, childrenDiv3));
                        var controlDiv = React.createElement('div', {'className': 'container', 'style':{'flex':1, 'display':'flex', 'maxWidth':'100vw', 'minWidth':'5vw', 'flexDirection':'row'}}, children);
                        return controlDiv;
               } else {
                       return null
               }
        }

        renderCanvas(){
                var tempState = {...this.state}
                var plotContainer = document.getElementById(this.state.id);
                //Attach canvas to the container once
                if (typeof this.state.canvas === 'undefined'){

                        var canvas = document.createElement('canvas');
                        canvas.setAttribute('id', this.state.id+'_canvas');
                        canvas.style.flex=1;
                        plotContainer.appendChild(canvas);
                        //create chemdoodle canvas
                        var doodlecanvas = new ChemDoodle.TransformCanvas3D(this.state.id+'_canvas', parseInt(window.innerWidth*0.8), parseInt(window.innerHeight*0.6));
                        
			
                        //Add listener to resize canvas if viewport resizes
                        window.addEventListener('resize', function () {
                                doodlecanvas.resize(parseInt(window.innerWidth*0.8), parseInt(window.innerHeight*0.6));
                                
                        });

                        //set canvas styles and what not
                        doodlecanvas.styles.set3DRepresentation(this.state.canvasType);
                        doodlecanvas.styles.backgroundColor = undefined;
                        doodlecanvas.styles.atoms_displayLabels_3D = true;
                        doodlecanvas.styles.outline_3D = true;
                        doodlecanvas.emptyMessage='No Data Loaded!';
                        doodlecanvas.repaint();
                        tempState.canvas = doodlecanvas;
                        
                }
             

                this.setState(tempState);
        }

	addEnergies(key, energiesObj){
		var tempState = {...this.state}
                //console.log(key, energiesObj);
		tempState.energies.set(key, energiesObj);
		this.setState(tempState);

	}

        addMoleculeCML(key, cmlStr){
                var tempState = {...this.state}
		//console.log(cmlStr);
                var mol = ChemDoodle.readCML(cmlStr);
                mol[0].orbitals=new Map;
                var len = mol[0].atoms.length;
		for (var i = len-1; i > -1; i--) {
                        var a = mol[0].atoms[i];
                        if (a.label.startsWith('orbital')) {
                                var o = mol[0].atoms.pop()
                                var vector = parseInt(a.label.split('_')[1]);
                                //mol[0].orbitals.set(vector, a);
                                o.altLabel = vector;
                                o.isOrbital=true; //Adding another attribute cause I can do that in javascript.
                                o.label = 'C'; //label holds chemically relevant info. It won't draw if it's something other than an element.
                                mol[0].orbitals.set(vector, o);
                                //console.log(i, mol[0].orbitals); 
                                //a.dontDraw=true; 
                                //console.log(a);
                        } else {
                                a.isOrbital=false;
                        }

                }
		console.log('reading cml', mol, typeof mol, mol[0]);
                tempState.molecules.set(key, mol[0]);
		tempState.selectedAtoms.set(key, new Array);
                this.setState(tempState);
        }
        
	addMoleculeXYZ(key, xyzStr){
                var tempState = {...this.state}
		var cmlInterp = new ChemDoodle.io.CMLInterpreter();
		//console.log(xyzStr);
                var mol = ChemDoodle.readXYZ(xyzStr);
		var cmlMolStr = cmlInterp.write([mol]);
		
		//console.log('reading xyz', mol, typeof mol);
                //console.log(cmlMolStr);
		tempState.molecules.set(key, mol);
                this.setState(tempState);
        }
        //wrapper function to match plotDiv
        setHTML(json){
                var pairs = Object.entries(json);
                for (var i = 0; i < pairs.length; i++){
                        var pair = pairs[i];
                        var key = pair[0];
                        var dat = pair[1];
                        console.log(key, dat);
			this.addMoleculeCML(key, dat.struct);
			this.addEnergies(key, dat.dft_energies);
                }
                this.renderCanvas()
        }

        //callback function to get which complex 
        cb(key){
		this.swapCanvas(key);
        }
	swapCanvas(key){
		var tempState = {...this.state}
		var doodlecanvas = this.state.canvas
                //Set all orbital centers to not render
                var mol = this.state.molecules.get(key);
                console.log(mol.orbitals);
                //swap values in the energy table
                var tableHandler = plotHandlerRef.get('tableEnergy');
                tableHandler.renderTables(key);

                var selectOrbitalStyle = doodlecanvas.styles.copy();
                selectOrbitalStyle.surfaces_color = 'black';
                selectOrbitalStyle.atoms_useJMOLColors = false;
                selectOrbitalStyle.atoms_color = 'purple';
                
                var newMol = new ChemDoodle.structures.Molecule();
                for (var o of mol.orbitals.values()) {
                        o.styles = selectOrbitalStyle;
                        newMol.atoms.push(o);
                        //console.log(o);
                        //o.styles=doodlecanvas.styles.copy();
                        //o.styles.atoms_useJMOLColors = false;
                        //o.styles.atoms_color='white';
                        //o.styles.atoms_useVDWDiameters_3D=true;
                        //o.isLone=true;
                        //o.styles.atoms_useVDWMultiplier_3D=0;
                }
                //TODO USE loadContent([mol, mol], [shapes])
                //var newSurf = new ChemDoodle.structures.d3.VDWSurface(newMol.atoms, 30);
                doodlecanvas.styles.surfaces_color = 'black'
                doodlecanvas.styles.flat_color_3D = true;
		//doodlecanvas.loadMolecule(mol);
                
		//doodlecanvas.loadContent([mol], [newSurf])
                

		doodlecanvas.loadContent([mol, newMol])
                tempState.activeKey = key
		this.setState(tempState);

	}

		

        selectAtoms(structKey, atomIdArray, vector){
		//Autoswap to correct canvas
		//console.log(structKey, this.state.activeKey, structKey === this.state.activeKey);
		if (structKey != this.state.activeKey){ //Autoswap to correct canvas
			this.swapCanvas(structKey);

		}
                //Takes in an array of atomIds
                var tempState = {...this.state}
                var canvas = this.state.canvas;
                var mol = this.state.molecules.get(this.state.activeKey);
                
                var selectStyle = canvas.styles.copy();
                var defaultStyle = canvas.styles.copy();
                //var defaultOrbitalStyle = canvas.styles.copy();
                var selectOrbitalStyle = canvas.styles.copy();
                //set custom styles
                //selectOrbitalStyle.surfaces_style = 'Mesh';
                selectOrbitalStyle.atoms_useJMOLColors = false;
                selectOrbitalStyle.surfaces_color = 'black';
                selectOrbitalStyle.atoms_color = 'purple';
                
                //selectOrbitalStyle.atoms_vdwMultiplier_3D = 2;
                //selectStyle.atoms_useJMOLColors = false;
                //selectStyle.atoms_color = 'purple';
                selectStyle.outline_thickness=10;
                //selectStyle.atoms_displayLabels_3D = true;
                //selectStyle.outline_3D = true;
                //
               	
               
                
                //for (var ind of mol.orbitals.values()) {
                //        var o = mol.atoms[ind];
                //        console.log(o);
                //        o.styles=selectOrbitalStyle;
                //        //o.styles.atoms_color='purple';
                //}

		//Unselect all atoms
		for (var i = 0; i < tempState.selectedAtoms.get(tempState.activeKey).length; i++) {
			var a = tempState.selectedAtoms.get(tempState.activeKey)[i];
                        console.log(a);
                        a.styles = defaultStyle;

                        a.isSelected=false;
			canvas.updateScene();
		}

		//Set active atoms
                //console.log('atomIdArray', atomIdArray);
                tempState.selectedAtoms.set(tempState.activeKey, []);
		for (var i = 0; i < atomIdArray.length; i++) {
			var a = mol.atoms[atomIdArray[i]];
			a.styles = selectStyle; 
                        //tempState.selectedAtoms
                        a.isSelected=true;
                        tempState.selectedAtoms.get(tempState.activeKey).push(a);
		}
                //tempState.selectedAtoms.set(tempState.activeKey, atomIdArray);
	        
                if (typeof vector != 'undefined'){
                        var o = mol.orbitals.get(vector);
                        //console.log(o);
                        o.isSelected=true;
                        o.styles = selectOrbitalStyle;
                        //canvas.styles = selectOrbitalStyle; 
                        //tempState.selectedAtoms.get(tempState.activeKey).push(o);
                        var newMol = new ChemDoodle.structures.Molecule();
                        newMol.atoms[0] = o;
                        newMol.atoms[1] = o;
                        //var newSurf = new ChemDoodle.structures.d3.VDWSurface([o], 10);
                        canvas.loadContent([mol, newMol])
                }
                canvas.updateScene();


		//for (var i = 0; i < mol.atoms.length; i++){
		//        var a = mol.atoms[i];
		//        if (atomIdArray.includes(i)) {
		//                a.styles = selectStyle; 
		//                canvas.updateScene();
		//                
		//        } else {
		//                a.styles = defaultStyle;
		//        }
		//}
		canvas.repaint();
		this.setState(tempState);
        }
        
        render() {
                return React.createElement('div', {'id': this.state.id, 'className': 'doodleContainer', 'style':{'display':'flex','flexDirection':'column-reverse' }}, this.renderControlDiv())

        }

}





//ADD COMPONENTS TO PAGE
var availList = ReactDOM.render(
        React.createElement(complexList, {'title':'Available Complexes', 'key':'availList'}, null),
        document.getElementById("selectLeft"),
);

var plotList = ReactDOM.render(
        React.createElement(complexList, {'title':'Complexes to Plot', 'key':'plotList'}, null),
        document.getElementById("listRow"),
);

var controls = ReactDOM.render(
        React.createElement(selectControls, null, null),
        document.getElementById('selectRight'),
);


//var plotRowManager = ReactDOM.render(
//        React.createElement(plotManager, null, null),
//        document.getElementById("plotRow"),
//);

//Bind specific functions to the controls
controls.setInputList(availList);
controls.setOutputList(plotList);
controls.setRemoveList(plotList);
controls.setPlotList(plotList);

//Use jQuery to communicate with the backend
var plotHandlerRef = new Map;
export { plotHandlerRef };

function setupPlotRow() {
        $.ajax({ //Gets the available plots and creates them all to sit in the background until needed
          method: "GET",
          url:"/api/plots", //use this to define which api you're talking to
          success: function (data) {
                var json = JSON.parse(data);
                var plotRow = document.getElementById("plotRow")
                //console.log(json);
                console.log(data, json);
                for (var i = 0; i < json.length; i++){
                        console.log(i, json[i]);
                        var container = document.createElement('div')
                        container.setAttribute('id', `plot-container-${i}`)
                        container.setAttribute('class', `row`)
                        plotRow.appendChild(container);
                        if (json[i] === 'structure') {
                                var plotHandler = ReactDOM.render(
                                        React.createElement(chemdoodlePlot, {'id':json[i]}, null),
                                        container,
                                );
                        } else if (json[i].startsWith('table')) {
                                var plotHandler = ReactDOM.render(
                                        React.createElement(tablePlot, {'id':json[i]}, null),
                                        container,
                                );
                        } else {
                                var plotHandler = ReactDOM.render(
                                        React.createElement(plotDiv, {'id':json[i]}, null),
                                        container,
                                );

                        }
                        plotHandlerRef.set(json[i], plotHandler);
                        controls.setPlotHandler(json[i], plotHandler);
                }
                }, 
          dataType: "html"
        });
}


$(document).ready(function() {
	console.log('Ready!');
	//Get options from the other side.
	$.ajax({
	  method: "GET",
	  url:"/api/filename", //use this to define which api you're talking to
	  success: function (json) {
                        availList.loadFromJson(json); 
                }, 
	  dataType: "html"
	});

        setupPlotRow();
	

});




