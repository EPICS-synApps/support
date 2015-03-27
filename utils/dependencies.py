#!/bin/env python

"""
Find all the (dbd, db, adl, and lib) explicit dependencies in synApps.
usage: dependencies.py supportDir outfile

Find the directories in 'supportDir' that are named in
supportDir/configure/RELEASE.  This is the list of modules. Search modules to
compile lists of resources published by each module (dbd, db, adl, and lib), and
resources used by each module but not published by it (dbdUsed, dbUsed, adlUsed,
and libUsed). From these lists, compile lists of the modules on which each
module depends (dbd_depends, db_depends, adl_depends, lib_depends).  Write the
lists to 'outfile'.  

"""

import sys, os, glob, shutil, copy

moduleDict={}

class moduleInfo:
	def __init__(self, filepath):
		self.filepath = filepath
		self.resourceDict = {"dbd":[], "db":[], "adl":[], "lib":[],
			"dbdUsed":[], "dbUsed":[], "adlUsed":[], "libUsed":[]}
		self.dependsOn = {"dbd":[], "db":[], "adl":[], "lib":[]}

def appendOnceOnly(l, i):
	"""append item i to list l if item is not already in list"""
	if l.count(i) == 0:
		l.append(i)

def examine_dbd(l, dir, f):
	"""find the .dbd files whose names occur in .dbd file f"""
	infile = open(os.path.join(dir,f),"r")
	lines = infile.readlines()
	for rawline in lines:
		line = rawline.strip()
		if (len(line) > 0) and (line[0] != "#"):
			words = line.split()
			for word in words:
				word = word.strip('"').strip("'")
				if word.endswith(".dbd"):
					appendOnceOnly(l, word)
def examine_db(l, dir, f):
	"""find the .db files whose names occur in file f"""
	infile = open(os.path.join(dir,f),"r")
	lines = infile.readlines()
	for rawline in lines:
		line = rawline.strip()
		if (len(line) > 0) and (line[0] != "#"):
			words = line.split()
			for word in words:
				word = word.strip('"').strip("'")
				if word.endswith(".db"):
					appendOnceOnly(l, os.path.basename(word))

def examine_adl(l, dir, f):
	"""find the .db files whose names occur in file f"""
	infile = open(os.path.join(dir,f),"r")
	lines = infile.readlines()
	for rawline in lines[4:]:	# skip past line that names the file
		line = rawline.strip()
		if (len(line) > 0) and (line[0] != "#"):
			line = line.replace("=", " ")
			words = line.split()
			for word in words:
				word = word.strip('"').strip("'")
				if word.endswith(".adl"):
					appendOnceOnly(l, os.path.basename(word))

def examine_Makefile(dbdList, dbdUsedList, libList, libUsedList, dir, f):
	"""find the dbd and lib files used by file f"""
	infile = open(os.path.join(dir,f),"r")
	lines = infile.readlines()
	for rawline in lines:
		line = rawline.strip()
		if (len(line) > 0) and (line[0] != "#") and (line.find("=") != -1):
			line = line.replace("+=", " ")
			line = line.replace("=", " ")
			words = line.split()
			# look for .dbd files published
			if words[0].startswith("DBD"):
				#print "rawline='%s'" % rawline
				for word in words[1:]:
					if not word.endswith(".dbd"):
						word += ".dbd"
					appendOnceOnly(dbdList, os.path.basename(word))
			# look for .dbd files used
			elif words[0].find("_DBD") != -1:
				#print "rawline='%s'" % rawline
				for word in words[1:]:
					appendOnceOnly(dbdUsedList, os.path.basename(word))
			# look for libs published
			elif words[0].find("LIBRARY") != -1:
				#print "rawline='%s'" % rawline
				appendOnceOnly(libList, os.path.basename(words[1]))
			# look for libs used
			elif words[0].find("_LIBS") != -1:
				#print "rawline='%s'" % rawline
				for word in words[1:]:
					if not word.startswith("$("):
						appendOnceOnly(libUsedList, os.path.basename(word))

def collect(destDict, dir, fileList):
	"""find files in fileList that end with certain extensions, add those files to
	certain lists, and examine the files for dependencies"""
	if (dir in ["db", "dbd", "lib"]):
		return
	for f in fileList:
		if f.endswith(".dbd"):
			appendOnceOnly(destDict["dbd"], f)
			examine_dbd(destDict["dbdUsed"], dir, f)
		elif f.endswith(".db") or f.endswith(".vdb") or f.endswith(".template"):
			appendOnceOnly(destDict["db"], f)
		elif f.endswith(".substitutions"):
			examine_db(destDict["dbUsed"], dir, f)
		elif f.endswith(".adl"):
			appendOnceOnly(destDict["adl"], f)
			examine_adl(destDict["adlUsed"], dir, f)
		elif f == "Makefile":
			examine_Makefile(destDict["dbd"], destDict["dbdUsed"], destDict["lib"], destDict["libUsed"], dir, f)

def inReleaseFile(releaseDirs, name):
	for s in releaseDirs:
		s = s.strip("\n")
		ix = s.find(name)
		if (ix != -1) and (len(s[ix:]) == len(name)):
			print name, "matches", s 
			return True
	return(False)

def main(supportDir, outfilename):
	if outfilename:
		outFile = open(outfilename, "w")

	releaseFilename = os.path.join(supportDir, "configure/RELEASE")
	releaseFile = open(releaseFilename, "r")
	releaseDirs = []
	for line in releaseFile:
		if (line[0] != '#') and (line.find('=') != -1):
			releaseDirs.append(line)

	# find all directories
	files = glob.glob(os.path.join(supportDir,"*"))
	for file in files:
		#if os.path.isdir(file) and not os.path.islink(file) and	os.path.exists(os.path.join(file,"configure")):

		if inReleaseFile(releaseDirs, os.path.basename(file)):
			print os.path.basename(file), "found"
			# Now we think this is an epics module includec in the build
			baseFileName = os.path.basename(file)
			moduleDict[baseFileName] = moduleInfo(file)
		#else:
		#	print os.path.basename(file), "NOT found"

	# find all resources published and used
	for module in moduleDict.keys():
		directory = moduleDict[module].filepath
		print "searching directory ", directory
		os.path.walk(directory, collect, moduleDict[module].resourceDict)


	# weed out resources used within a module
	for module in moduleDict.keys():
		resourceDict = moduleDict[module].resourceDict
		#print "weeding", module
		if len(resourceDict) > 0:
			l = copy.copy(resourceDict["dbdUsed"])
			for i in l:
				if resourceDict["dbd"].count(i):
					resourceDict["dbdUsed"].remove(i)

			l = copy.copy(resourceDict["dbUsed"])
			for i in l:
				if resourceDict["db"].count(i):
					resourceDict["dbUsed"].remove(i)

			l = copy.copy(resourceDict["adlUsed"])
			for i in l:
				if resourceDict["adl"].count(i):
					resourceDict["adlUsed"].remove(i)

			l = copy.copy(resourceDict["libUsed"])
			for i in l:
				if resourceDict["lib"].count(i):
					resourceDict["libUsed"].remove(i)

	# find module dependencies
	NeedKeys = ["dbdUsed", "dbUsed", "adlUsed", "libUsed"]
	SupplyKeys = ["dbd", "db", "adl", "lib"]
	for module in moduleDict.keys():
		for need in moduleDict[module].resourceDict["dbdUsed"]:
			for trymodule in moduleDict.keys():
				if need in moduleDict[trymodule].resourceDict["dbd"]:
					appendOnceOnly(moduleDict[module].dependsOn["dbd"], trymodule)
					break

		for need in moduleDict[module].resourceDict["dbUsed"]:
			for trymodule in moduleDict.keys():
				if need in moduleDict[trymodule].resourceDict["db"]:
					appendOnceOnly(moduleDict[module].dependsOn["db"], trymodule)
					break

		for need in moduleDict[module].resourceDict["adlUsed"]:
			for trymodule in moduleDict.keys():
				if need in moduleDict[trymodule].resourceDict["adl"]:
					appendOnceOnly(moduleDict[module].dependsOn["adl"], trymodule)
					break

		for need in moduleDict[module].resourceDict["libUsed"]:
			for trymodule in moduleDict.keys():
				if need in moduleDict[trymodule].resourceDict["lib"]:
					appendOnceOnly(moduleDict[module].dependsOn["lib"], trymodule)
					break

	# write
	moduleList = copy.copy(moduleDict.keys())
	moduleList.sort()
	for module in moduleList:
		if len(moduleDict[module].resourceDict) > 0:
			outFile.write("\n%s\n" % module)
			keys = ["dbd", "dbdUsed", "db", "dbUsed", "adl", "adlUsed", "lib", "libUsed"]
			#keys = ["dbdUsed", "dbUsed", "adlUsed", "libUsed"]
			for key in keys:
				outFile.write("\t %-7s %s\n" % (key, moduleDict[module].resourceDict[key]))
			outFile.write("\n\t %-12s %s\n" % ("dbd_depends", moduleDict[module].dependsOn["dbd"]))
			outFile.write("\t %-12s %s\n" % ("db_depends", moduleDict[module].dependsOn["db"]))
			outFile.write("\t %-12s %s\n" % ("adl_depends", moduleDict[module].dependsOn["adl"]))
			outFile.write("\t %-12s %s\n" % ("lib_depends", moduleDict[module].dependsOn["lib"]))

	outFile.close()

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "usage: dependencies.py supportDir outfile"
		sys.exit(1)
	main(sys.argv[1], sys.argv[2])
