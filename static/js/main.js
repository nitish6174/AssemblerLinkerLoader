document.querySelector('#generateButton').onclick = function() {
	filetext = document.querySelector('#filetext').value;
	$.ajax({
		url: 'generate',
		type: 'POST',
		data: {
			files: filetext
		},
		success: function(data) {
			console.log(data);
			data = JSON.parse(data);
			symbols = data["symbols"];
			code = data["code"];
			// console.log(data);
			$('#symbolList').html('');
			for (var key in symbols)
			{
				appendtext = '<strong>'+key+':</strong><br>';
				appendtext += JSON.stringify(symbols[key])+'<br>';
				$('#symbolList').html($('#symbolList').html()+appendtext);
			}
			$('#assembly_code').html(code);			
		}
	});
}
