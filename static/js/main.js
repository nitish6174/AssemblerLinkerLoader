sim_step = 0;
res_regs = []
res_mems = []
res_flags = []
reg_code = []

$('.code_tab').click(function(){
	$('.code_tab.checked').removeClass('checked');
	$(this).addClass('checked');
	$('.code').hide();
	$('.code#'+$(this).attr('data-show')).show();
});

function call_process()
{
	filetext = document.querySelector('#filetext').value;
	offset = document.querySelector('#offset').value;
	if(offset==undefined||offset=="")
		offset = '0';
	$.ajax({
		url: 'generate',
		type: 'POST',
		data: {
			files: filetext,
			offset: offset
		},
		success: function(data) {
			data = JSON.parse(data);
			symbols = data["symbols"];
			symbol_table = data["symbol_table"];
			loadfile = data["loadfile"];
			pass1code = data["pass1code"];
			pass2code = data["pass2code"];
			link_code = data["link_code"];
			$('#literalTable').html(' ');
			for (var key in symbols)
			{
				appendtext = '<strong>'+key+':</strong><br>';
				appendtext += JSON.stringify(symbols[key])+'<br>';
				$('#literalTable').html($('#literalTable').html()+appendtext);
			}
			$('#symbolTable').html(JSON.stringify(symbol_table));
			$('#pass1code').html(pass1code);
			$('#pass2code').html(pass2code);
			$('#link_code').html(link_code);
			$('input[name="loadfile"]').val(loadfile);
		}
	});
	sim_step = 0;
}

function call_simulation()
{
	loadfile = document.querySelector('input[name="loadfile"]').value;
	offset = document.querySelector('#offset').value;
	if(offset==undefined||offset=="")
		offset = '0';
	$.ajax({
		url: 'simulate',
		type: 'POST',
		data: {
			loadfile: loadfile,
			offset: offset
		},
		success: function(data) {
			data = JSON.parse(data);
			console.log(data);
			res_regs = data["res_regs"];
			res_mems = data["res_mems"];
			res_flags = data["res_flags"];
			res_code = data["res_code"];
			next_step();
		}
	});
	sim_step = 0;
	$('#simulationResult').css('display','block');
}

function next_step()
{
	if(sim_step<res_regs.length)
	{
		$('#stepMessage').html("Current step : "+(sim_step+1).toString()+" (out of "+res_regs.length+")<br>");
		for(var key in res_regs[sim_step])
		{
			$('#regResCell'+key).html(res_regs[sim_step][key]);
		}
		for(var i=1;i<=res_mems[sim_step].length;i++)
		{
			$('#memResCell'+i).html(res_mems[sim_step][i-1]);
		}
		for(i=1;i<=res_flags[sim_step].length;i++)
		{
			$('#flagResCell'+i).html(res_flags[sim_step][i-1]);
		}
		$('#codeMessage').html(res_code[sim_step]);
		// $('#linked_code span#'+(sim_step+1).toString()).css('background-color','yellow');
		sim_step+=1;
	}
}