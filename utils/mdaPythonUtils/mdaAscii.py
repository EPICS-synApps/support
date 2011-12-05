#!/usr/bin/env python

import sys
from mda import *

def getFormat(d, rank):
	# number of positioners, detectors
	np = d[rank].np
	nd = d[rank].nd

	min_column_width = 15
	# make sure there's room for the names, etc.
	phead_fmt = []
	dhead_fmt = []
	pdata_fmt = []
	ddata_fmt = []
	columns = 1
	for i in range(np):
		cw = max(min_column_width, len(d[rank].p[i].name)+1)
		cw = max(cw, len(d[rank].p[i].desc)+1)
		cw = max(cw, len(d[rank].p[i].fieldName)+1)
		phead_fmt.append("%%-%2ds" % (cw-1))
		pdata_fmt.append("%%- %2d.8f" % (cw-1))
		columns = columns + cw
	for i in range(nd):
		cw = max(min_column_width, len(d[rank].d[i].name)+1)
		cw = max(cw, len(d[rank].d[i].desc)+1)
		cw = max(cw, len(d[rank].d[i].fieldName)+1)
		dhead_fmt.append("%%-%2ds" % (cw-1))
		ddata_fmt.append("%%- %2d.8f" % (cw-1))
		columns = columns + cw
	return (phead_fmt, dhead_fmt, pdata_fmt, ddata_fmt, columns)

def main():
	showInfo = 1
	showData = 1
	showEnv = 0
	verbose = 0

	print sys.argv

	fname = None
	if len(sys.argv)>1:
		print "sys.argv[1] = ", sys.argv[1]
		if sys.argv[1] == "help" or sys.argv[1][:2] == "-h":
			print "usage: %s [-idev] [filename]" % sys.argv[0]
			print "example: mdaAscii.py -i xxx_0001.mda"
			print "   flags:"
			print "      i -- show information"
			print "      d -- show data (only 1D data is shown)"
			print "      e -- show scan-environment PV's"
			print "      a -- show all (information, data, and scan-environment PV's)"
			print "      v -- tell file reader to be verbose"
			print "\nIf no filename is specified, a file requester window will open."
			return()
		if sys.argv[1][0] == '-':
			showInfo = 0
			showData = 0
			showEnv = 0
			if ('i' in sys.argv[1]): showInfo = 1
			if ('d' in sys.argv[1]): showData = 1
			if ('e' in sys.argv[1]): showEnv = 1
			if ('v' in sys.argv[1]): verbose = 4
			if ('a' in sys.argv[1]): showInfo = showData = showEnv = 1
			if len(sys.argv) > 2:
				fname = sys.argv[2]
		else:
			fname = sys.argv[1]

	d = readMDA(fname, 4, verbose, 0)
	rank = d[0]['rank']

	(phead_fmt, dhead_fmt, pdata_fmt, ddata_fmt, columns) = getFormat(d, 1)
	# header
	if (showInfo):
		print "### ", d[0]['filename'], " is a ", d[0]['rank'], "dimensional file."
		print "### Number of data points      = [",
		for i in range(d[0]['rank'],1,-1): print "%-d," % d[i].curr_pt,
		print d[1].curr_pt, "]"

		print "### Number of detector signals = [",
		for i in range(d[0]['rank'],1,-1): print "%-d," % d[i].nd,
		print d[1].nd, "]"

	if (showEnv):	
		# scan-environment PV values
		print "#\n# Scan-environment PV values:"
		ourKeys = d[0]['ourKeys']
		maxKeyLen = 0
		for i in d[0].keys():
			if (i not in ourKeys):
				if len(i) > maxKeyLen: maxKeyLen = len(i)
		for i in d[0].keys():
			if (i not in ourKeys):
				print "#", i, (maxKeyLen-len(i))*' ', d[0][i]

	if showInfo:
		print "#\n# ", str(d[1])
		print "#  scan date, time: ", d[1].time
		sep = "#"*columns
		print sep

		# 1D data
		# print table head
		print "#",
		for j in range(d[1].np):
			print phead_fmt[j] % (d[1].p[j].fieldName),
		for j in range(d[1].nd):
			print dhead_fmt[j] % (d[1].d[j].fieldName),
		print

		print "#",
		for j in range(d[1].np):
			print phead_fmt[j] % (d[1].p[j].name),
		for j in range(d[1].nd):
			print dhead_fmt[j] % (d[1].d[j].name),
		print

		print "#",
		for j in range(d[1].np):
			print phead_fmt[j] % (d[1].p[j].desc),
		for j in range(d[1].nd):
			print dhead_fmt[j] % (d[1].d[j].desc),
		print

		print sep

	if (showData):
		# 1D data
		for i in range(d[1].curr_pt):
			print "",
			for j in range(d[1].np):
				print pdata_fmt[j] % (d[1].p[j].data[i]),
			for j in range(d[1].nd):
				print ddata_fmt[j] % (d[1].d[j].data[i]),
			print

		# 2D data
		if rank >= 2:
			print "# 2D data"
			for i in range(d[2].np):
				print "\n# Positioner %d (.%s) PV:'%s' desc:'%s'" % (i, d[2].p[i].fieldName, d[2].p[i].name, d[2].p[i].desc)
				for j in range(d[1].curr_pt):
					for k in range(d[2].curr_pt):
						print "%f" % d[2].p[i].data[j][k],
					print

			for i in range(d[2].nd):
				print "\n# Detector %d (.%s) PV:'%s' desc:'%s'" % (i, d[2].d[i].fieldName, d[2].d[i].name, d[2].d[i].desc)
				for j in range(d[1].curr_pt):
					for k in range(d[2].curr_pt):
						try:
							print "%f" % d[2].d[i].data[j][k],
						except IndexError:
							print "Index Error printing 'd[2].d[i].data[j][k]'"
							print "... i=%d,j=%d,k=%d" % (i,j,k)
							print "... len(d[2].d)=", len(d[2].d)
							print "... len(d[2].d[i].data)=", len(d[2].d[i].data)
							print "... len(d[2].d[i].data[j])=", len(d[2].d[i].data[j])
					print
if __name__ == "__main__":
        main()
