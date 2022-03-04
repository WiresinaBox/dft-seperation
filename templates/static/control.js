

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
                this.push(props.complexes);
                this.loadFromJson(props.json);
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
                var tempState = {...this.state}
                for (var i = 0; i < values.length; i++) {
                        tempState.complexes.push({'complex':values[i], 'active':false});
                this.setState(tempState);

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

        //returns the current selected item.
        getSelected () {
                return(this.state.currentActive.complex)
        }

        removeSelected () {
                var tempState = {...this.state}
                var i = this.state.currentActiveIndex;
                if (typeof i === 'number') {
                        tempState.complexes.splice(i, 1);
                        console.log(i, tempState.complexes.length)
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
        }
        
        cb (action) { //given to the buttons
                console.log(action);
                switch(action){
                        case 'add':
                                var complex = this.state.getInputSelected()
                                this.state.pushOutput(complex);
                                break;
                        case 'remove':
                                this.state.removeSelected()
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


        render(){
                return(React.createElement('div', {'id':'selectControls'}, [
                        React.createElement(reactButton, {'name':'Add', 'action':'add', 'cb':this.cb.bind(this)}, null),
                        React.createElement(reactButton, {'name':'Remove', 'action':'remove', 'cb':this.cb.bind(this)}, null),
                        ])
                );
        }
}

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
controls.setInputList(availList);
controls.setOutputList(plotList);
controls.setRemoveList(plotList);

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

	$("#complex-select").change(function (){
	  var complex = $(this).children("option:selected").val();
	  console.log(complex);
	  $.ajax({
	      method:"PUT",
	      data: complex,
	      url:"/api/filename",
	      success: function (data){
		  var dataArray = JSON.parse(JSON.parse(data));
		  console.log(dataArray);  
		
	      },
	      dataType:"html"

	  });
	});
});




