document.querySelector('#generateButton').onclick = function() {
	filetext = document.querySelector('#filetext').value;
	$.ajax({
		url: 'generate',
		type: 'POST',
		data: {
			files: filetext
		},
		success: function(data) {
			data = JSON.parse(data);
			symbols = data["symbols"];
			unlinked_code = data["unlinked_code"];
			linked_code = data["linked_code"];
			$('#symbolTable').html('');
			for (var key in symbols)
			{
				appendtext = '<strong>'+key+':</strong><br>';
				appendtext += JSON.stringify(symbols[key])+'<br>';
				$('#symbolTable').html($('#symbolTable').html()+appendtext);
			}
			$('#unlinked_code').html(unlinked_code);
			$('#linked_code').html(linked_code);
		}
	});
}
