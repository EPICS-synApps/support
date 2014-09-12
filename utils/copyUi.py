#!/usr/bin/env python

import sys, os, glob, shutil

topdirs={}

def collectUi(destList, dirname, fileList):
	for f in fileList:
		if f.endswith(".ui") or f.endswith(".qss"):
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
		os.path.walk(directory, collectUi, topdirs[module][1])
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
		print "usage: copyUi.py sourcedir destdir"
		sys.exit(1)
	main(sys.argv[1], sys.argv[2])
