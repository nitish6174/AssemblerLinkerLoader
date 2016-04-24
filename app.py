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
		offset = int(request.form['offset'])

		loadfile = files[-1].split('.')[0]
		mainfile=loadfile+'.asm'
		symbols,symbol_table=assembler.assemble(files)
		linker.link(mainfile, symbols)
		loader.load(mainfile, offset)
		machine.convert(mainfile)

		f=open("Output/"+loadfile+'.pass1','r')
		code=f.read()
		f.close()
		code = code.split('\n')
		for i in range(0,len(code)):
			code[i] = code[i].replace(' ','&nbsp;')
			code[i] = "<span id=\""+str(i+1)+"\">"+code[i]+"</span><br>"
		pass1code = ''.join(code)

		f=open("Output/"+loadfile+'.pass2','r')
		code=f.read()
		f.close()
		code = code.split('\n')
		for i in range(0,len(code)):
			code[i] = "<span id=\""+str(i+1)+"\">"+code[i]+"</span><br>"
		pass2code = ''.join(code)

		f=open("Output/"+loadfile+'.asm','r')
		code=f.read()
		f.close()
		code = code.split('\n')
		for i in range(0,len(code)):
			code[i] = "<span id=\""+str(i+1)+"\">"+code[i]+"</span><br>"
		link_code = ''.join(code)

		return json.dumps({'symbols':symbols,'symbol_table':symbol_table,'loadfile':loadfile,'pass1code':pass1code,'pass2code':pass2code,'link_code':link_code})
	
@app.route('/simulate', methods=['POST'])
def simulate():
	if request.method == 'POST':
		loadfile = request.form['loadfile']
		offset = int(request.form['offset'])

		res_regs = []
		res_mems = []
		res_flags = []
		res_code = []

		def display(prevs, nexts):
			# print '\nRegisters:'
			# for key in reg:
			# 	print key+' : '+str(reg[key])
			# print 'Memory:'
			# print mem[:100]
			# print 'Flags : '+str(flag)
			# print 'Prev Statement:'+str(prevs)
			# print 'Next Statement:'+str(nexts)
			# print 'Prev Statement:'+lines[str(prevs)]
			# print 'Next Statement:'+lines[str(nexts)]
			res_regs.append(reg.copy())
			res_mems.append(mem[:100])
			res_flags.append(flag[:])
			res_code.append(str(prevs)+" ("+lines[str(prevs)]+")")

		def set_flag(acc):
			if acc == 0:
				flag[0]=1
				flag[1]=0
				flag[2]=0
			elif acc > 0:
				flag[1]=1
				flag[0]=0
				flag[2]=0
			else:
				flag[2]=1
				flag[1]=0
				flag[0]=0

		f=open("Output/"+loadfile+'.asm','r')
		data=f.read()
		f.close()

		opcodes = {}
		code=data.splitlines()
		lines = {}
		reg={'A':0, 'B':0, 'C':0, 'D':0, 'E':0, 'H':0, 'L':0}
		mem=[0]*1024
		sp=1023
		flag=[0]*5
		dispflag=0

		f=open('opcode_len.txt','r')
		data=f.read()
		f.close()
		lin=data.splitlines()
		for line in lin:
			line=line.split(' ')
			opcodes[line[0]]=int(line[1])

		j=offset
		for line in code:
			lines[str(j)]=line
			if line.startswith('DB'):
				mem[j]=int(line.split(' ')[1])
			j += opcodes[line.split(' ')[0]]

		i=j
		byte=0
		byte=offset
		while byte < i:
			line=lines[str(byte)]
			line_split = line.split(' ')
			if len(line_split) > 1:
				line_split[1] = line_split[1].strip(',')
			if line.startswith('MOV'):
				reg[line_split[1]]=reg[line_split[2]]
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('MVI'):
				reg[line_split[1]]=int(line_split[2])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('LDA'):
				reg['A']=mem[int(line_split[1])]
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('ADI'):
				reg['A']=reg['A'] + int(line_split[1])
				set_flag(reg['A'])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('SUI'):
				reg['A']=reg['A'] - int(line_split[1])
				set_flag(reg['A'])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('SUB'):
				reg['A']=reg['A'] - reg[line_split[1]]
				set_flag(reg['A'])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('ADD'):
				reg['A']=reg['A'] + reg[line_split[1]]
				set_flag(reg['A'])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('STA'):
				mem[int(line_split[1])]=reg['A']
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('PUSH'):
				if line_split[1] is 'D':
					mem[sp]=reg['D']
					mem[sp-1]=reg['E']
				elif line_split[1] is 'B':
					mem[sp]=reg['B']
					mem[sp-1]=reg['C']
				else:
					mem[sp]=reg['H']
					mem[sp-1]=reg['L']
				sp=sp-2
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('POP'):
				if line_split[1] is 'D':
					reg['D']=mem[sp+1]
					reg['E']=mem[sp]
				elif line_split[1] is 'B':
					reg['B']=mem[sp+1]
					reg['C']=mem[sp]
				else:
					reg['H']=mem[sp+1]
					reg['L']=mem[sp]
				sp=sp+2
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('ORI'):
				reg['A']=reg['A'] | int(line_split[1])
				set_flag(reg['A'])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('ORA'):
				reg['A']=reg['A'] | reg[line_split[1]]
				set_flag(reg['A'])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('JNZ'):
				byte_old=byte
				if flag[0] == 0:
					byte=int(line_split[1])
				else:
					byte += opcodes[line_split[0]]
				display(byte_old, byte)
			elif line.startswith('JZ'):
				byte_old=byte
				if flag[0] == 1:
					byte=int(line_split[1])
				else:
					byte += opcodes[line_split[0]]
				display(byte_old, byte)
			elif line.startswith('JP'):
				byte_old=byte
				if flag[1] == 1:
					byte=int(line_split[1])
				else:
					byte += opcodes[line_split[0]]
				display(byte_old, byte)
			elif line.startswith('JMP'):
				byte_old=byte
				byte=int(line_split[1])
				display(byte_old, byte)
			elif line.startswith('JM'):
				byte_old=byte
				byte=int(line_split[1]) -1
				byte += opcodes[line_split[0]]
				display(byte_old, byte)
			elif line.startswith('ANI'):
				reg['A']=reg['A'] & int(line_split[1])
				set_flag(reg['A'])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('ANA'):
				reg['A']=reg['A'] & reg[line_split[1]]
				set_flag(reg['A'])
				byte += opcodes[line_split[0]]
				display(byte-opcodes[line_split[0]], byte)
			elif line.startswith('HLT'):
				byte += opcodes[line_split[0]]
				# for key in reg:
				# 	print key+' : '+str(reg[key])

		# return json.dumps({'offset':[offset],'steps':[steps]})
		return json.dumps({'res_regs':res_regs,'res_mems':res_mems,'res_flags':res_flags,'res_code':res_code})

if __name__ == '__main__':
	app.run(host='0.0.0.0')