

var complexSelect = document.getElementById('complex-select');
var complexLists = document.getElementById('complexListsDiv');

//resuable
function loadComplexNames (data) {
      var dataArray = JSON.parse(JSON.parse(data));
      for (let i = 0; i < dataArray.length; i++) {
	var opt = document.createElement('option');
	opt.value = dataArray[i];
	opt.innerHTML = dataArray[i];
	complexSelect.appendChild(opt);
	};
    }

$(document).ready(function() {
	console.log('Ready!');
	//Get options from the other side.
	$.ajax({
	  method: "GET",
	  url:"/api/filename", //use this to define which api you're talking to
	  success: loadComplexNames, 
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


class complexList extends React.Component{
	//This gets called when ReactDOM renders it
	render() {
		return React.createElement('div', null, '${this.props.name}');
	}
}

ReactDOM.render(
	React.createElement(complexList, {name: 'hi'}, null),
	document.getElementById('complexListsDiv')
);
