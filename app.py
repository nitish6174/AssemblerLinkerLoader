from flask import Flask,request,render_template
import sys
import json
# sys.path.insert(0, r'/mnt/B4A49A87A49A4BAC/Programming/Systems Programming/Assembler_Linker_Loader/process')
import assembler
import linker
import loader
import machine

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
	if request.method == 'GET':
		return render_template('index.html',links=False)

@app.route('/generate', methods=['POST'])
def generate():
	if request.method == 'POST':
		files = (request.form['files']).split(',')
		# # offset = request.form['offset']
		offset = 0

		mainfile=files[-1].split('.')[0]+'.asm'
		symbols=assembler.assemble(files)
		linker.link(mainfile, symbols)
		loader.load(mainfile, offset)
		machine.convert(mainfile)

		f=open("Output/"+mainfile,'r')
		code=f.read()
		f.close()
		code = code.split('\n')
		for i in range(0,len(code)):
			code[i] = "<span id=\""+str(i+1)+"\">"+code[i]+"</span><br>"
		# code = code.replace("\n","<br>")
		code = ''.join(code)
		# print code
		return json.dumps({'symbols':symbols,'code':code})
	
# @app.route('/simulate', methods=['POST'])
# def simulate():
#   filename = request.form['filename']
#   offset = request.form['offset']

if __name__ == '__main__':
	app.run(host='0.0.0.0')