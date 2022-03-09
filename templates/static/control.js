

var complexSelect = document.getElementById('complex-select');
var complexLists = document.getElementById('complexListsDiv');

var addButton = document.getElementById('addComplexButton');
var removeButton = document.getElementById('removeComplexButton');

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
                        children.push(listElement({'name': data.complex, 'key':`${data.complex}-${i}`, 'index':i, 'active':data.active, 'cb':this.cb.bind(this)}));
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
        return React.createElement('button', {'className':`btn ${active}`, 'key':key, 'onClick':onClick}, props.name)
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
                var dataStr = JSON.stringify({'plotType':plotType,'complexList':complexNames});
                $.ajax({
                  method: "POST",
                  url:"/api/plots", //use this to define which api you're talking to
                  data: dataStr, 
                  success: function (data) {
                        var plotData = Object.entries(data);
                        //console.log(json);
                        for (var i = 0; i < plotData.length; i++){
                                var pair = plotData[i];
                                var plotFunc = plotFuncs.get(pair[0]);
                                plotFunc(JSON.parse(pair[1]));
                        }
                        },
                  dataType: "json"
                });

        }


        render(){
                return(React.createElement('div', {'id':'selectControls'}, [
                        React.createElement(reactButton, {'name':'Add', 'action':'add', 'cb':this.cb.bind(this)}, null),
                        React.createElement(reactButton, {'name':'Remove', 'action':'remove', 'cb':this.cb.bind(this)}, null),
                        React.createElement(reactButton, {'name':'Plot', 'action':'plot', 'cb':this.cb.bind(this)}, null),
                        ])
                );
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
                        var inlineScript = document.createTextNode(this.state.script.data);
                        plotScript.appendChild(inlineScript);
                }
                
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

                return(React.createElement('div', {'className':'plot container', 'id':this.state.id})) 
        }

}

class plotManager extends React.Component{
        constructor (props) {
                super(props);
                this.state = {};
                this.state.children = [];
        }

        setHTMLFromArray(jsonArray){
                var tempState = {...this.state}
                for (var i = 0; i < jsonArray.length; i++) {
                        var json = JSON.parse(jsonArray[i]);
                        var child = React.createElement(plotDiv, {'id':i, 'json':json}, null);
                        tempState.children.push(child);
                        
                }
                this.setState(tempState);

        }
        render() {
                return(React.createElement('div', {'className':'plotManager container'}, this.state.children)) 
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
	
        $.ajax({ //Gets the available plots and creates them all to sit in the background until needed
	  method: "GET",
	  url:"/api/plots", //use this to define which api you're talking to
	  success: function (data) {
                var json = JSON.parse(data);
                var plotRow = document.getElementById("plotRow")
                for (var i = 0; i < json.length; i++){
                        var container = document.createElement('div')
                        container.setAttribute('id', `plot-container-${i} row`)
                        plotRow.appendChild(container);

                        
                        var plotHandler = ReactDOM.render(
                                React.createElement(plotDiv, {'id':json[i]}, null),
                                container,
                        );
                        
                        controls.setPlotHandler(json[i], plotHandler);
                }
                }, 
	  dataType: "html"
	});

	$("#complex-select").change(function (){
	  var complex = $(this).children("option:selected").val();
	  $.ajax({
	      method:"PUT",
	      data: complex,
	      url:"/api/filename",
	      success: function (data){
		  var dataArray = JSON.parse(JSON.parse(data));
		
	      },
	      dataType:"html"

	  });
	});
});




