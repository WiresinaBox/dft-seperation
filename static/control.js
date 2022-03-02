'use strict';

const e = React.createElement;

var complexSelect = document.getElementById('complex-select');

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
