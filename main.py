import re
import assembler,linker,loader,machine

files=[]
print 'Enter files to processed together (in order of execution):'
while True:
	print 'File Name:',
	fname=raw_input()
	if fname is '':
		break;
	files.append(fname)
print 'Enter Offset:',
# offset=int(raw_input())
offset = 0

print ""
mainfile=files[-1].split('.')[0]+'.asm'
symbols,symbol_table=assembler.assemble(files)
linker.link(mainfile, symbols)
loader.load(mainfile, offset)
machine.convert(mainfile)

print '\nSymbol Table:'
for key in symbols:
	print 'File: '+key
	print symbols[key]
