#!/usr/bin/env python

""" Fill a wxPython treeCtrl with the content of an MDA file"""
import os
import mda_f as mda
from f_xdrlib import *

def hexValuesAsString(numList, maxVals=None):
	s = '['
	for (i,val) in enumerate(numList):
		if (i==0):
			s += "%x" % val
		else:
			s += ", %x" % val
		if (maxVals < len(numList)) and (i >= maxVals):
			s += ", ..."
			break
	s += ']'
	return s

################################################################################
# read MDA file

def readScanFillTree(scanFile, tree, branch, unpacker=None):
	"""usage: (scan,num) = readScanFillTree(scanFile, tree, branch, unpacker=None)"""

	scan = mda.scanDim()	# data structure to hold scan info and data
	buf = scanFile.read(10000) # enough to read scan header
	if unpacker == None:
		u = Unpacker(buf)
	else:
		u = unpacker
		u.reset(buf)

	loc = scanFile.tell()
	scan.rank = u.unpack_int()
	tree.AppendItem(branch, "%08X %-12s %d" % (loc, 'rank', scan.rank))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	scan.npts = u.unpack_int()
	tree.AppendItem(branch, "%08X %-12s %d" % (loc, 'npts', scan.npts))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	scan.curr_pt = u.unpack_int()
	tree.AppendItem(branch, "%08X %-12s %d" % (loc, 'curr_pt', scan.curr_pt))

	if (scan.rank > 1):
		# if curr_pt < npts, plower_scans will have garbage for pointers to
		# scans that were planned for but not written
		loc = scanFile.tell() - (len(buf) - u.get_position())
		scan.plower_scans = u.unpack_farray(scan.npts, u.unpack_int)
		tree.AppendItem(branch, "%08X %-12s %s" % (loc, 'p_scans', hexValuesAsString(scan.plower_scans, 6)))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	namelength = u.unpack_int()
	scan.name = u.unpack_string()
	tree.AppendItem(branch, "%08X %-12s %s" % (loc, 'name', scan.name))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	timelength = u.unpack_int()
	scan.time = u.unpack_string()
	tree.AppendItem(branch, "%08X %-12s %s" % (loc, 'time', scan.time))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	scan.np = u.unpack_int()
	tree.AppendItem(branch, "%08X %-12s %s" % (loc, 'np', scan.np))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	scan.nd = u.unpack_int()
	tree.AppendItem(branch, "%08X %-12s %s" % (loc, 'nd', scan.nd))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	scan.nt = u.unpack_int()
	tree.AppendItem(branch, "%08X %-12s %s" % (loc, 'nt', scan.nt))


	for j in range(scan.np):
		scan.p.append(mda.scanPositioner())

		loc = scanFile.tell() - (len(buf) - u.get_position())
		scan.p[j].number = u.unpack_int()
		scan.p[j].fieldName = mda.posName(scan.p[j].number)
		pBranch = tree.AppendItem(branch, "%08X %s %s" % (loc, 'positioner', scan.p[j].fieldName))
		tree.AppendItem(pBranch, "%08X %-15s %s" % (loc, 'number', scan.p[j].number))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of name string
		if length: scan.p[j].name = u.unpack_string()
		tree.AppendItem(pBranch, "%08X %-15s %s" % (loc, 'drive PV', scan.p[j].name))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of desc string
		if length: scan.p[j].desc = u.unpack_string()
		tree.AppendItem(pBranch, "%08X %-15s '%s'" % (loc, 'drive desc', scan.p[j].desc))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of step_mode string
		if length: scan.p[j].step_mode = u.unpack_string()
		tree.AppendItem(pBranch, "%08X %-15s %s" % (loc, 'step mode', scan.p[j].step_mode))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of unit string
		if length: scan.p[j].unit = u.unpack_string()
		tree.AppendItem(pBranch, "%08X %-15s '%s'" % (loc, 'drive unit', scan.p[j].unit))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of readback_name string
		if length: scan.p[j].readback_name = u.unpack_string()
		tree.AppendItem(pBranch, "%08X %-15s %s" % (loc, 'readback PV', scan.p[j].readback_name))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of readback_desc string
		if length: scan.p[j].readback_desc = u.unpack_string()
		tree.AppendItem(pBranch, "%08X %-15s '%s'" % (loc, 'readback desc', scan.p[j].readback_desc))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of readback_unit string
		if length: scan.p[j].readback_unit = u.unpack_string()
		tree.AppendItem(pBranch, "%08X %-15s '%s'" % (loc, 'readback unit', scan.p[j].readback_unit))


	for j in range(scan.nd):
		scan.d.append(mda.scanDetector())

		loc = scanFile.tell() - (len(buf) - u.get_position())
		scan.d[j].number = u.unpack_int()
		scan.d[j].fieldName = mda.detName(scan.d[j].number)
		dBranch = tree.AppendItem(branch, "%08X %s %s" % (loc, 'detector  ', scan.d[j].fieldName))
		tree.AppendItem(dBranch, "%08X %-12s %s" % (loc, 'number', scan.d[j].number))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of name string
		if length: scan.d[j].name = u.unpack_string()
		tree.AppendItem(dBranch, "%08X %-12s %s" % (loc, 'PV name', scan.d[j].name))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of desc string
		if length: scan.d[j].desc = u.unpack_string()
		tree.AppendItem(dBranch, "%08X %-12s '%s'" % (loc, 'PV desc', scan.d[j].desc))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of unit string
		if length: scan.d[j].unit = u.unpack_string()
		tree.AppendItem(dBranch, "%08X %-12s '%s'" % (loc, 'PV unit', scan.d[j].unit))

	for j in range(scan.nt):
		scan.t.append(mda.scanTrigger())

		loc = scanFile.tell() - (len(buf) - u.get_position())
		tBranch = tree.AppendItem(branch, "%08X %s%d" % (loc, 'trigger    T', j+1))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		scan.t[j].number = u.unpack_int()
		tree.AppendItem(tBranch, "%08X %-12s %s" % (loc, 'number', scan.t[j].number))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		length = u.unpack_int() # length of name string
		if length: scan.t[j].name = u.unpack_string()
		tree.AppendItem(tBranch, "%08X %-12s %s" % (loc, 'PV name', scan.t[j].name))

		loc = scanFile.tell() - (len(buf) - u.get_position())
		scan.t[j].command = u.unpack_float()
		tree.AppendItem(tBranch, "%08X %-12s %.3f" % (loc, 'command', scan.t[j].command))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	tree.AppendItem(branch, "%08X-%08X %-12s %d doubles" % (loc, loc+scan.npts*scan.np*8-1, 'pos. data:', scan.npts*scan.np))

	loc += scan.npts * (scan.np * 8)
	tree.AppendItem(branch, "%08X-%08X %-12s %d floats" % (loc, loc+scan.npts*scan.nd*4-1, 'det. data:', scan.npts*scan.nd))

	return scan



def readMDA_FillTree(fname=None, maxdim=4, tree=None):
	"""usage readMDA(fname=None, maxdim=4, tree)"""

	dim = []

	if (fname == None):
		print "No file specified"
		return None
	if (tree == None):
		print "No tree specified"
		return None

	if (not os.path.isfile(fname)):
		if (not fname.endswith('.mda')):
			fname = fname + '.mda'
		if (not os.path.isfile(fname)):
			print fname, "not found"
			return None

	root = tree.AddRoot(fname)

	scanFile = open(fname, 'rb')
	buf = scanFile.read(100)	# to read header for scan of up to 5 dimensions
	u = Unpacker(buf)

	tree.AppendItem(root, "hex_loc item_name     item_value")

	# read file header
	version = u.unpack_float()
	tree.AppendItem(root, "%08X %-12s %.2f" % (0, 'version', version))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	scan_number = u.unpack_int()
	tree.AppendItem(root, "%08X %-12s %d" % (loc, 'scan_number', scan_number))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	rank = u.unpack_int()
	tree.AppendItem(root, "%08X %-12s %d" % (loc, 'rank', rank))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	dimensions = u.unpack_farray(rank, u.unpack_int)
	tree.AppendItem(root, "%08X %-12s %s" % (loc, 'dimensions', dimensions))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	isRegular = u.unpack_int()
	tree.AppendItem(root, "%08X %-12s %d" % (loc, 'isRegular', isRegular))

	loc = scanFile.tell() - (len(buf) - u.get_position())
	pExtra = u.unpack_int()
	tree.AppendItem(root, "%08X %-12s 0x%x" % (loc, 'pExtra', pExtra))

	# collect 1D data
	pmain_scan = scanFile.tell() - (len(buf) - u.get_position())
	scanFile.seek(pmain_scan)
	branch = tree.AppendItem(root, "scan")
	s = readScanFillTree(scanFile, tree, branch, unpacker=u)
	dim.append(s)
	dim[0].dim = 1

	if ((rank > 1) and (maxdim > 1)):
		sbranch = tree.AppendItem(branch, "inner scans")
		for i in range(dim[0].curr_pt):
			scanFile.seek(dim[0].plower_scans[i])
			branch1 = tree.AppendItem(sbranch, "%08X scan %d" % (scanFile.tell(), i))
			s1 = readScanFillTree(scanFile, tree, branch1, unpacker=u)
			if ((rank > 2) and (maxdim > 2)):
				sbranch1 = tree.AppendItem(branch1, "inner scans")
				for j in range(s1.curr_pt):
					scanFile.seek(s1.plower_scans[j])
					branch2 = tree.AppendItem(sbranch1, "%08X scan %d/%d" % (scanFile.tell(), i,j))
					s2 = readScanFillTree(scanFile, tree, branch2, unpacker=u)
					if ((rank > 3) and (maxdim > 3)):
						sbranch2 = tree.AppendItem(branch2, "inner scans")
						for k in range(s2.curr_pt):
							scanFile.seek(s2.plower_scans[k])
							branch3 = tree.AppendItem(sbranch2, "%08X scan %d/%d/%d" % (scanFile.tell(), i,j,k))
							s = readScanFillTree(scanFile, tree, branch3, unpacker=u)
							if ((i == 0) and (j == 0) and (k == 0)):
								dim.append(s)
								dim[3].dim = 4


	return root
