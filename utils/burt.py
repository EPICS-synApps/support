#!/usr/bin/env python
"""
usage:
	import burt
	burt.write("myBurtSnapshotFile.snap", verbose=1)
"""

import sys
import ca
from ca_util import *


# Human readable exception description
#	try:
#		x = x + 1
#	except:
#		print formatExceptionInfo()
import sys
import traceback
def formatExceptionInfo(maxTBlevel=5):
	cla, exc, trbk = sys.exc_info()
	excName = cla.__name__
	try:
		excArgs = exc.__dict__["args"]
	except KeyError:
		excArgs = "<no args>"
	excTb = traceback.format_tb(trbk, maxTBlevel)
	return (excName, excArgs, excTb)

def write(snapFile, verbose=0):
	file = open(snapFile, "r")
	inBurtHeader = 0
	failed_puts = {}
	for rawLine in file:
		#print "inBurtHeader = ", inBurtHeader, "  rawLine=", rawLine
		if inBurtHeader:
			# look for end
			if rawLine[:19] == '--- End BURT header':
				inBurtHeader = 0
			continue
		else:
			if rawLine[:21] == '--- Start BURT header':
				inBurtHeader = 1
				continue

		# parse lines of the form: <name> <num> <value>
		words = rawLine.split(' ',2)
		if len(words) < 3 :
			continue
		words[2] = words[2].strip('\n').lstrip(' ')
		if verbose: print "words=", words
		if int(words[1]) != 1:
			print "burt.py: Not ready for arrays"
		else:
			if words[2] == '\\0': words[2] = ""
			if (len(words[2]) > 1) and (words[2][0] == '"') and (words[2][-1] == '"'):
				words[2] = words[2].strip('"')
			if words[2] == ' ': words[2] = ""
			if verbose:
				print "\ncaput('%s', '%s')" % (words[0], words[2])
			try:
				caput(words[0], words[2], req_type=ca.DBR_STRING, timeout=3, retries=10, read_check_tolerance=0.001)
			except:
				failed_puts[words[0]] = words[2]
				if verbose:
					print formatExceptionInfo()
	file.close()
	for key in failed_puts.keys():
		print "failed to set '%s' to the value '%s'" % (key, failed_puts[key])
	del failed_puts

def main():
	#print "sys.arvg:", sys.argv
	if len(sys.argv) < 2:
		print "usage: burt <snapFile>"
		return
	write(sys.argv[1])

if __name__ == "__main__":
	main()
