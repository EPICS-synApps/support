#!/bin/env python

import sys, os, glob, shutil

topdirs={}

def collectOpi(destList, dirname, fileList):
	for f in fileList:
		if f.endswith(".opi") or f.endswith(".def"):
			destList.append(os.path.join(dirname,f))

def main(src, dest):

	# find all directories
	files = glob.glob(os.path.join(src,"*"))
	for file in files:
		if os.path.isdir(dest) and os.path.samefile(file, dest):
			continue
		if os.path.isdir(file):
			baseFileName = os.path.basename(file).split("-")[0]
			topdirs[baseFileName]=[]
			topdirs[baseFileName].append(file)
			topdirs[baseFileName].append([])

	for module in topdirs.keys():
		directory = topdirs[module][0]
		print "searching directory ", directory
		os.path.walk(directory, collectOpi, topdirs[module][1])
		if len(topdirs[module][1]) > 0:
			if not os.path.isdir(dest):
				os.mkdir(dest)
			destDir = os.path.join(dest,module)
			if not os.path.isdir(destDir):
				os.mkdir(destDir)
			for file in topdirs[module][1]:
				#print "pretending to copy(%s,%s)" % (file, destDir)
				shutil.copy(file, destDir)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "usage: copyOpi.py sourcedir destdir"
		exit
	main(sys.argv[1], sys.argv[2])
