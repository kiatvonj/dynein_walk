#! /usr/bin/python

import re
import string
# Converts the output of Mathematica scripts (in Standard Form) in Motion_Equations/ to C++ code

# input: DyneinBrownianBothboundSolutionsUnsimplified.txt, DyneinBrownianLeftboundSolutionsUnsimplified.txt, DyneinBrownianRightboundSolutionsUnsimplified.txt, 
# output: dynein_motion_functions.cpp

text_both =  open('Motion_Equations/DyneinBrownianBothboundSolutionsUnsimplified.txt', 'r').read()
text_left =  open('Motion_Equations/DyneinBrownianLeftboundSolutionsUnsimplified.txt', 'r').read()
text_right = open('Motion_Equations/DyneinBrownianRightboundSolutionsUnsimplified.txt', 'r').read()

text = text_left + text_right + text_both
out = open('dynein_motion_functions.cpp', 'w')


out.write("#include \"dynein_struct.h\"\n\n")

#line = 0
#while (string.find(text, "\n")) != -1:												# Annotate output .cpp with line numbers of original file
	#idx = string.find(text, "\n")
	#text = text[:idx] + "/* " + str(int(line)) + " */" + text[idx+2:]
	#line += 1

#	Replacement rules

text = re.sub(r'\{\{Derivative\[2\]\[bla\]\[t\] -\>', 'BLA_DERIVATIVE_2: ', text)		# Build temp structure to hold different expressions
text = re.sub(r'Derivative\[2\]\[mla\]\[t\] -\>', 'MLA_DERIVATIVE_2: ', text)
text = re.sub(r'Derivative\[2\]\[mra\]\[t\] -\>', 'MRA_DERIVATIVE_2: ', text)
text = re.sub(r'Derivative\[2\]\[bra\]\[t\] -\>', 'BRA_DERIVATIVE_2: ', text)

print "replace.py: Changing Mathematica symbols to C symbols"
text = re.sub('\n', '', text)															# Remove all line breaks
text = re.sub(r'[ ]{2,}', '', text)			 											# Delete all large spaces
text = re.sub(r'(\([a-z]*)\^\\\[Prime\]\\\[Prime\]\)\[t\] \-\>', r'\n\1":\n', text)		# Change 'Derivative[1]...' to 'get_d_...'
text = re.sub(r'Derivative\[1\]\[([a-z]*)\]\[t\]', r'get_d_\1()', text)
text = re.sub(r'Derivative\[2\]\[([a-z]*)\]\[t\]', r'get_dd_\1()', text)

text = re.sub(r'([a-z]*)\[t\]', r'get_\1()', text)										# Change 'bla[t]' etc to 'get_bla(t)'
text = re.sub('Pi', 'M_PI', text)														# Write pi in C
text = re.sub(r'Sin', 'sin', text)														
text = re.sub(r'Cos', 'cos', text)
text = re.sub(r'\[', '(', text)															# Change Mathematica brackets to C parens
text = re.sub(r'\]', ')', text)
text = re.sub(r'([a-zA-Z]+)\^2', r'square(\1)', text)									# Change ^2/^3 to local square/cube functions for single-variable expressions
text = re.sub(r'([a-zA-Z]+)\^3', r'cube(\1)', text)
text = re.sub(r'([a-zA-Z]+)\^5', r'fifth(\1)', text)

print "replace.py: Changing Mathematica variable names to C variable names"
text = re.sub('Lt', 'lt', text)															# Convert from Mathematica variable naming scheme to C variable naming scheme
text = re.sub('Ls', 'ls', text)
text = re.sub('mA', 'ma', text)
text = re.sub('bA', 'ba', text)
text = re.sub('tA', 'ta', text)
text = re.sub(r'F([mbrl]{2})x', r'f\1x', text)
text = re.sub(r'F([mbrl]{2})y', r'f\1y', text)
text = re.sub('Ftx', 'ftx', text)
text = re.sub('Fty', 'fty', text)

print "replace.py: Changing Mathematica squares / cubes to C squares / cubes"
idx = 0
while string.find(text, ")^2") != -1:													 # Change ^2/^3 to local square/cube functions for multi-variable expressions	
	idx = string.find(text, ")^2")
	i = idx
	v = 1
	while (v != 0):
		i = i - 1
		if text[i] == ")":
			v = v + 1
		elif text[i] == "(":
			v = v - 1
	if text[i-3:i] == "cos":
		text = text[:i-3] + "square(" + text[i-3:idx+1] + ")" + text[idx+3:]
		continue
			
	elif text[i-3:i] == "sin":
		text = text[:i-3] + "square(" + text[i-3:idx+1] + ")" + text[idx+3:]
		continue
		
	elif text[i-9:i-5] == "get_":
		text = text[:i-9] + "square(" + text[i-9:idx+1] + ")" + text[idx+3:]
		continue
		
	else:
		text = text[:i] + "square" + text[i:idx+1] + text[idx+3:]
	
idx = 0
while string.find(text, ")^3") != -1:
	idx = string.find(text, ")^3")
	i = idx
	v = 1
	while (v != 0):
		i = i - 1
		if text[i] == ")":
			v = v + 1
		elif text[i] == "(":
			v = v - 1
	if text[i-3:i] == "cos":
		text = text[:i-3] + "cube(" + text[i-3:idx+1] + ")" + text[idx+3:]
		continue
		
	elif text[i-3:i] == "sin":
		text = text[:i-3] + "cube(" + text[i-3:idx+1] + ")" + text[idx+3:]
		continue
		
	elif text[i-9:i-5] == "get_":
		text = text[:i-9] + "cube(" + text[i-9:idx+1] + ")" + text[idx+3:]
		continue
		
	else:
		text = text[:i] + "cube" + text[i:idx+1] + text[idx+3:]

print "replace.py: Adding multiplication symbols"
text = re.sub(r'([^ \t\r\f\v\-\+\\\*\-\>]+)[ \t\r\f\v]+([^ \t\r\f\v\-\+\\\*\-\>]+)', r'\1 * \2', text) # a b c d -> a * b c * d
text = re.sub(r'([^ \t\r\f\v\-\+\\\*\-\>]+)[ \t\r\f\v]+([^ \t\r\f\v\-\+\\\*\-\>]+)', r'\1 * \2', text) # a * b c * d -> a * b * c * d
text = re.sub(r'([0-9]+)', r'\1.0', text)
text = re.sub(r'([\+-]{1})', r'\1 ', text)

print "replace.py: Creating CPP file"
text = re.sub(r'BLA_DERIVATIVE_2\.0:([^,\n]*),', r'bla: \1\n', text)								   # Build temp structure to hold different expressions
text = re.sub(r'MLA_DERIVATIVE_2\.0:([^,\n]*),', r'mla: \1\n', text)
text = re.sub(r'MRA_DERIVATIVE_2\.0:([^,\n]*),', r'mra: \1\n', text)
text = re.sub(r'BRA_DERIVATIVE_2\.0:([^\}\n]*)\}\}', r'bra: \1\n', text)

text = re.sub(r' \* ', '', text)

text = re.sub(r'bla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\n',		# Create acceleration functions
r'bla: \1\nmla: \2\nmra: \3\nbra: \4\nbla: \5\nmla: \6\nmra: \7\nbra: \8\nbla: \9\nmla: \10\nmra: \11\nbra: \12\n' + 
r'double Dynein::get_dd_bla() {\n\tif (state == BOTHBOUND)\n\t\treturn \1;\n\telse if (state == LEFTBOUND)\n\t\treturn \5;\n\telse\n\t\treturn \9;\n}\n\n', text)

text = re.sub(r'bla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\n',
r'bla: \1\nmla: \2\nmra: \3\nbra: \4\nbla: \5\nmla: \6\nmra: \7\nbra: \8\nbla: \9\nmla: \10\nmra: \11\nbra: \12\n' + 
r'double Dynein::get_dd_mla() {\n\tif (state == BOTHBOUND)\n\t\treturn \2;\n\telse if (state == LEFTBOUND)\n\t\treturn \6;\n\telse\n\t\treturn \10;\n}\n\n', text)

text = re.sub(r'bla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\n',
r'bla: \1\nmla: \2\nmra: \3\nbra: \4\nbla: \5\nmla: \6\nmra: \7\nbra: \8\nbla: \9\nmla: \10\nmra: \11\nbra: \12\n' + 
r'double Dynein::get_dd_mra() {\n\tif (state == BOTHBOUND)\n\t\treturn \3;\n\telse if (state == LEFTBOUND)\n\t\treturn \7;\n\telse\n\t\treturn \11;\n}\n\n', text)

text = re.sub(r'bla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\n',
r'bla: \1\nmla: \2\nmra: \3\nbra: \4\nbla: \5\nmla: \6\nmra: \7\nbra: \8\nbla: \9\nmla: \10\nmra: \11\nbra: \12\n' + 
r'double Dynein::get_dd_bra() {\n\tif (state == BOTHBOUND)\n\t\treturn \4;\n\telse if (state == LEFTBOUND)\n\t\treturn \8;\n\telse\n\t\treturn \12;\n}\n\n', text)

text = re.sub(r'bla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\nbla: (.*)\nmla: (.*)\nmra: (.*)\nbra: (.*)\n', '', text)		# Remove temp structure

out.write(text)
