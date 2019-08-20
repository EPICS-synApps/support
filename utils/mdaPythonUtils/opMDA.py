#!/usr/bin/env python
import sys
from mda import *

def usage():
	print "usage:"
	print "   %s file1 op (file2 | scalar_value) = result_file" % sys.argv[0]
	print "   op must be one of '+', '-', '*', 'x','/', '>', '<'"
	print "example2:"
	print "   xxx_0001.mda + xxx_0002.mda = sum_1_2.mda"
	print "   xxx_0001.mda * 1.732 = xxx_0001_norm.mda"
	return

def main():
	root = Tkinter.Tk()
	if len(sys.argv) < 3 or sys.argv[1] == '?' or sys.argv[1] == "help" or sys.argv[1][:2] == "-h":
		usage()
		return()
	else:
		file1 = sys.argv[1]
		op = sys.argv[2]
		file2 = sys.argv[3]
		equal = sys.argv[4]
		resultFile = sys.argv[5]
		print file1, op, file2, " --> ", resultFile
	if not (op in ['+', '-', '/', '*', 'x', '>', '<']):
		usage()
		return
	#print "type(op) = ", type(op)
	d1 = readMDA(file1)
	if file2[0] in ['-', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'] :
		d2 = float(file2)
		#print "d2=",d2,"  type(d2)=", type(d2)
	else:
		d2 = readMDA(file2)
	s = opMDA(op,d1,d2)
	if (isScan(s)):
		writeMDA(s, resultFile)

if __name__ == "__main__":
        main()
