#!/usr/bin/env python

"""
This software is part of a package intended to help convert an ioc directory
from one version of synApps to another.   This module finds, parses, and writes
autosave request files.
"""

import sys
import os
import glob
import string
import curses.ascii
from conversionUtils import *
from convertCmdFiles import *
from convertSubFiles import *


class autosaveDictionaries:
	"""
	asFileDict contains the content of an autosave-request file, which
	contains lines of the form:
	  file motor_settings.req P=$(P),M=m1
	which populate asFileDict; and lines of the form
	  $(P)hsc1:hID
	which populate asPvDict

	asFileDict['motor_settings.req"] = [dictEntry1,...]
	where dictEntry (included from conversionUtils) contains:
	  leadingComment	  comment from original line
	  trailing comment    comment from original line (not implemented yet)
	  value 			  entire macroString "P=$(P),M=m1"
	  used  			  dictEntry has been used to write a new file
	  origLine  		  original line from old ioc dir
	  macroDict 		  {P:$(P), M:m1}

	asPvDict['$(P)hsc1:hID'] = [dictEntry1,...]
	where dictEntry contains
	  leadingComment	  comment from original line
	  trailing comment    comment from original line (not implemented yet)
	  value 			  None
	  used  			  dictEntry has been used to write a new file
	  origLine  		  original line from old ioc dir
	  macroDict 		  None

	asKeyList is a list of the dictionary keys in asFileDict and asPvDict, in
	the order in which the keys were encountered in the request file.
	"""

	def __init__(self):
		self.asFileDict = {}
		self.asPvDict = {}
		self.asKeyList = []


class autosaveIncludeEntry:
	"""
	autosaveIncludeEntry contains information about an autosave-request file
	that is included in another autosave-request file.  We're not going to try
	to convert or reproduce this "include" file, but simply to use it.
	Therefore, all we need from it is its name, and a list of the macro names
	it contains.
	"""

	def __init__(self, name):
		self.name = name
		self.pattern = []



def getRequestFilePath(cmdFileDicts):
	"""Get request-file path from .cmd-file dictionary, and cdCommands or
	envPaths.
	
	Given all of the information collected from .cmd files, and from the
	file cdCommands or envPaths, compile a list of the directories
	autosave will search for request files.  '.cmd' files (especially
	save_restore.cmd) are expected to contain one or more calls to
	"set_requestfile_path()". Each call defines a single directory, in
	the form of one or two argument strings, which may contain macro
	names or shell variables.  For example: set_requestfile_path(calc,
	"calcApp/Db") contains the shell variable "calc", whose value was
	defined in the file cdCommands as 'calc =
	"/home/mooney/epics/synApps/support/calc"' From this information, the
	following path would be added to the list:
	"/home/mooney/epics/synApps/support/calc/calcApp/Db"
	"""

	if not "set_requestfile_path" in cmdFileDicts.funcDict.keys():
		print "Can't find request-file path"
		return []
	pathList = []
	value = ["", ""]
	for entry in cmdFileDicts.funcDict["set_requestfile_path"]:
		if (entry.value.find(",") != -1):
			words = entry.value.split(',')
		else:
			words = [entry.value, ""]
		for i in range(2):
			if (words[i].find('"') == -1):
				# shell variable
				value[i] = getVar(cmdFileDicts.varDict, words[i])
				if (value[i] == None):
					print "getRequestFilePath: var '%s' not found" % words[i]
			else:
				# string, which might contain a macro
				words[i] = words[i].strip().strip('"')
				if (words[i].find('$(') != -1):
					# macro
					words[i] = words[i][2:].strip(')')
					value[i] = getEnv(cmdFileDicts.envDict, words[i])
					if (value[i] == None):
						print "getRequestFilePath: var '%s' not found" % words[i]
				else:
					value[i] = words[i]

		if (value[0] and value[1]): path = os.path.join(value[0],value[1])
		elif value[0]: path = value [0]
		elif value[1]: path = value[1]
		else:
			print "getRequestFilePath: could not add '%s' to pathlist" % entry.value
			continue
		pathList.append(path)
	return pathList


def findAllDbFiles(cmdFileDicts):
	" Find all the database files available for use in an ioc directory."

	dbFileList = []
	dbFileBaseNameList = []
	requestFilePathList = getRequestFilePath(cmdFileDicts)
	for path in requestFilePathList:
		filespec = os.path.join(path, "*.db")
		dbFiles = glob.glob(filespec)
		for dbfile in dbFiles:
			if os.path.isfile(dbfile):
				s = os.path.basename(dbfile)
				dbFileList.append(s)
				s = s[:s.find(".")]
				dbFileBaseNameList.append(s)
		filespec = os.path.join(path, "*.vdb")
		dbFiles = glob.glob(filespec)
		for dbfile in dbFiles:
			if os.path.isfile(dbfile):
				s = os.path.basename(dbfile)
				dbFileList.append(s)
				s = s[:s.find(".")]
				dbFileBaseNameList.append(s)
	return (dbFileList, dbFileBaseNameList)


def getPattern(reqFile):
	"""
	Search through an autosave-request file for macros (e.g., "$(P)").
	Return a list of the variable names found.
	"""

	pattern = []
	file = open(reqFile, "r")
	#print "getPattern: file='%s'" % reqFile
	for rawLine in file:
		startIx = 0
		while startIx < len(rawLine)-4:
			Ix = rawLine[startIx:].find("$(")
			if (Ix == -1): break
			macroIx = startIx + Ix + 2
			Ix = rawLine[macroIx:].find(")")
			if (Ix == -1): break
			macro = rawLine[macroIx:macroIx+Ix]
			startIx = macroIx+Ix+1
			if not macro in pattern: pattern.append(macro)
			#print "getPattern: rawLine='%s' macro='%s' startIx=%d" % (rawLine, macro, startIx)
	#print "getPattern: reqFile='%s', pattern=%s" % (reqFile, pattern)
	return pattern


def findAllReqFiles(cmdFileDicts):
	"""
	Search through all the directories in the autosave request-file path
	for autosave-request files.  The request-file path is found by calling
	getRequestFilePath().  Autosave-request files are marked by a file name
	of the form "*_settings.req" or *_positions.req".  For each file found,
	make a dictionary entry in settingsReqFileDict, or positionsReqFileDict.
	Return the compiled dictionaries as a tuple.
	"""

	settingsReqFileDict = {}
	positionsReqFileDict = {}
	requestFilePathList = getRequestFilePath(cmdFileDicts)
	for path in requestFilePathList:
		# _settings.req files
		filespec = os.path.join(path, "*_settings.req")
		reqFiles = glob.glob(filespec)
		for rfile in reqFiles:
			if os.path.isfile(rfile):
				s = os.path.basename(rfile)
				entry = autosaveIncludeEntry(s)
				rfileBaseName = s[:s.find("_settings")]
				entry.pattern = getPattern(rfile)
				settingsReqFileDict[rfileBaseName] = entry
		# _positions.req files
		filespec = os.path.join(path, "*_positions.req")
		reqFiles = glob.glob(filespec)
		for rfile in reqFiles:
			if os.path.isfile(rfile):
				s = os.path.basename(rfile)
				entry = autosaveIncludeEntry(s)
				rfileBaseName = s[:s.find("_positions")]
				entry.pattern = getPattern(rfile)
				positionsReqFileDict[rfileBaseName] = entry
	return (settingsReqFileDict, positionsReqFileDict)


def findMatchingAutosaveIncludeFiles(requestFilePath, databaseName):
	"""
	Given a database name, and the autosave request-file path (a list of
	directory names), find the request file(s) whose names match the
	database name.  For example, the database "motor.db" would be matched
	by "motor_positions.req" and "motor_settings.req".  If either or both
	such files exist, return their names.
	"""

	baseName = databaseName
	dotIx = baseName.find(".")
	if (dotIx != -1): baseName = baseName[:dotIx]
	trialSettingsName = baseName + "_settings.req"
	trialPositionsName = baseName + "_positions.req"
	settingsName = ""
	positionsName = ""
	for path in requestFilePath:
		trialName = os.path.join(path, trialSettingsName)
		if os.path.isfile(trialName): settingsName = trialSettingsName
		trialName = os.path.join(path, trialPositionsName)
		if os.path.isfile(trialName): positionsName = trialPositionsName
		if (settingsName and positionsName):
			return (settingsName, positionsName)
	return (settingsName, positionsName)


def matchAllDbToReq(cmdFileDicts, subFileDict):
	""" For each database in a dictionary, find the matching autosave
	positions or settings files, if any exist.
	"""

	dbDict = {}
	reqFilePath = getRequestFilePath(cmdFileDicts)
	for db in cmdFileDicts.dbLoadRecordsDict.keys():
		dbDict[db] = findMatchingAutosaveIncludeFiles(reqFilePath, db)
	for subFile in subFileDict.keys():
		for db in subFileDict[subFile].templateFileDict.keys():
			if (db not in dbDict.keys()):
				dbDict[db] = findMatchingAutosaveIncludeFiles(reqFilePath, db)
	return dbDict


def replaceMacrosWithValues(s, macroDict):
	"""
	Given a string, s, which might contain one or more macros of the form
	"$(P)", and given a dictionary of macro name/value pairs (e.g.,
	macroDict["P"]=="xxx:") return s with macros replaced by their corresponding
	values.  Also return a string indicating whether any macros were not found.
	"""
	#print "replaceMacrosWithValues: s = '%s'" % (s)

	status = ""
	startIx = 0
	value = None
	while startIx <= len(s)-4:
		#print "replaceMacrosWithValues: looking for '$(' in '%s'" % (s[startIx:])
		Ix = s[startIx:].find("$(")
		if (Ix == -1): break
		macroIx = startIx + Ix + 2
		#print "replaceMacrosWithValues: looking for ')' in '%s'" % (s[macroIx:])
		endIx = s[macroIx:].find(")")
		if (endIx == -1): break
		macro = s[macroIx:macroIx+endIx]
		startIx = macroIx+endIx+1
		if macro in macroDict.keys():
			value = macroDict[macro]
			s = s[:macroIx-2] + value + s[macroIx+endIx+1:]
			startIx = s.find("$(")
		else:
			startIx = macroIx+endIx+1
			status = "notFound"
	return (s, status)


def makeMacroString(pattern, macroDict):
	"""
	Given a list of macro names, and a dictionary that associates macro names
	with values, construct and return a string of the form
	    'name1=value1,name2=value2,...'
	Also return a string indicating whether any macros were not found.
	"""

	#print "\nmakeMacroString:entry: pattern='%s' macroDict.keys()=%s" % (pattern, macroDict.keys())
	macroString = ""
	status = ""
	for macro in pattern:
		if macro in macroDict.keys():
			value = macroDict[macro]
			macroString = macroString + "%s=%s " % (macro, value)
		else:
			macroString = macroString + "%s=$(%s) " % (macro, macro)
			status = "notFound"
	#print "makeMacroString: calling replaceMacrosWithValues('%s')" % (macroString)
	(macroString, replaceStatus) = replaceMacrosWithValues(macroString, macroDict)
	if replaceStatus: status = replaceStatus
	#print "makeMacroString: returning '%s', status='%s'" % (macroString, status)
	return (macroString, status)


def writeStandardAutosaveFiles(cmdFileDicts, subFileDict, dirName="."):
	""" Write standard autosave files.
	
	Standard autosave files are the files "auto_settings.req" and
	"auto_positions.req". Collect a list of the databases to be loaded into an
	ioc, and lists of the autosave-request files associated by name with those
	request files.  That is, for each database, "zzz.db", look for files named
	"zzz_positions.req" and "zzz_settings.req".  Write the standard autosave
	files, including lines of the form "file zzz_settings.req macro-string"
	where macro-string is a list of the form "name1=value1 name2=value2 ...".
	Macro names are extracted from the request files; values are extracted from
	the macro strings supplied in the dbLoadRecords command, or the
	substitutions file, in which a database is loaded.  We hope that all macro
	names in the request files will have values defined in a related
	dbLoadRecords command or substitutions file.  If not, punt, and let the
	EPICS developer figure out what to do.
	"""

	(settingsReqFileDict, positionsReqFileDict) = findAllReqFiles(cmdFileDicts)
	settingsFileName = os.path.join(dirName,"auto_settings.req.STD")
	settingsFile = open(settingsFileName,"w")
	positionsFileName = os.path.join(dirName,"auto_positions.req.STD")
	positionsFile = open(positionsFileName,"w")
	reqFilePath = getRequestFilePath(cmdFileDicts)
	for db in cmdFileDicts.dbLoadRecordsDict.keys():
		dbBaseName = db[:db.find(".")]
		if dbBaseName in settingsReqFileDict.keys():
			settingsEntry =  settingsReqFileDict[dbBaseName]
			for entry in cmdFileDicts.dbLoadRecordsDict[db]:
				if entry.leadingComment: continue
				(macroString, status) = makeMacroString(settingsEntry.pattern, entry.macroDict)
				trailer = ""
				if (status): trailer = " #dbLoad command: "+entry.origLine
				settingsFile.write("file %s %s%s\n" % (settingsEntry.name, macroString, trailer))
		if dbBaseName in positionsReqFileDict.keys():
			positionsEntry =  positionsReqFileDict[dbBaseName]
			for entry in cmdFileDicts.dbLoadRecordsDict[db]:
				if entry.leadingComment: continue
				(macroString, status) = makeMacroString(positionsEntry.pattern, entry.macroDict)
				trailer = ""
				if (status): trailer = " #dbLoad command:"+entry.origLine
				positionsFile.write("file %s %s%s\n" % (positionsEntry.name, macroString, trailer))
	for subFile in subFileDict.keys():
		subFileEntry = subFileDict[subFile]
		#print "writeStandardAutosaveFiles: subFile=%s, leadingComment='%s'" % (subFile, subFileEntry.leadingComment)
		if subFileEntry.leadingComment: continue
		for db in subFileEntry.templateFileDict.keys():
			dbBaseName = db[:db.find(".")]
			for dictEntry in subFileEntry.templateFileDict[db]:
				if dictEntry.leadingComment: continue
				if dbBaseName in settingsReqFileDict.keys():
					settingsEntry =  settingsReqFileDict[dbBaseName]
					for macroDict in dictEntry.macroDictList:
						(macroString, status) = makeMacroString(settingsEntry.pattern, macroDict)
						trailer = ""
						if (status): trailer = " #substitutions file: "+subFile
						settingsFile.write("file %s %s%s\n" % (settingsEntry.name, macroString, trailer))
				if dbBaseName in positionsReqFileDict.keys():
					positionsEntry =  positionsReqFileDict[dbBaseName]
					for macroDict in dictEntry.macroDictList:
						(macroString, status) = makeMacroString(positionsEntry.pattern, macroDict)
						trailer = ""
						if (status): trailer = " #substitutions file: "+subFile
						positionsFile.write("file %s %s%s\n" % (positionsEntry.name, macroString, trailer))


# We're going to see macro strings with name=value pairs separated by whitespace, a
# comma, or both. If we convert commas to spaces, the strings will be easier to
#  parse.
commaToSpaceTable = string.maketrans(',',' ')


def cannotBePvName(s):
	""" Test string to see if it could possible be a PV name.
	
	When we encounter a commented out line in an autosave-request file we're
	parsing, we'll need to know if it's just a comment, or if it's a commented
	out file command or PV name.  If the first word of the line is not "file,
	and it could be a PV name, we'll treat it as a PV name.  So we need a test
	to see if a word could possibly be a PV name.
	"""

	for c in s:
		if c.isspace(): return True
		if curses.ascii.ispunct(c) and (not c in [':', '.', '$', '(', ')']):
			return True
	return False


def parseAutosaveFile(d, asFileName, verbose, ignoreComments=False):
	""" Parse an autosave file, collecting its information into a dictionary.
	
	We're given a collection of dictionaries into which we can write, and the
	name of an autosave-request file to parse.  Read the file, and collect all
	the PV names and 'file' commands.  Add the PV names to a list.  Examine the
	'file' commands, collecting the file to be included, and the macro string to
	be used to satisfy macros in the file.
	"""

	file = open(asFileName)
	for rawLine in file:
		line = rawLine.strip("\t\r\n ")
		if (len(line) == 0): continue
		if (isDecoration(line)):continue
		if (verbose): print "\n'%s'" % line

		isCommentedOut = (line[0] == '#')
		if (isCommentedOut and ignoreComments): continue

		line = line.lstrip("#")

		if (len(line) == 0): continue

		words = line.split()
		if words[0] == "file":
			# e.g., 'file motor_settings.req P=$(P),M=m1'
			fileName = words[1].strip('"')
			macroString = words[2].strip('"')
			if fileName not in d.asFileDict.keys():
				d.asFileDict[fileName] = []
				d.asKeyList.append(fileName)
			entry = dictEntry(macroString, rawLine)
			if isCommentedOut: entry.leadingComment = rawLine[:rawLine.find("file")]

			entry.macroDict = {}
			parms = macroString.translate(commaToSpaceTable).split()
			for p in parms:
				if '=' in p:
					name, value = p.split('=', 1)
					name = name.strip()
					entry.macroDict[name] = value.strip()
					if (verbose-1 > 0): print "macro: '%s' = '%s'" % (name, value)
			d.asFileDict[fileName].append(entry)
		elif isCommentedOut and ((len(words)>1) or (cannotBePvName(words[0]))):
			# probably a real comment.  Ignore for now.
			continue
		else:
			pvName = words[0]
			if pvName not in d.asPvDict.keys():
				d.asPvDict[pvName] = []
				d.asKeyList.append(pvName)
			entry = dictEntry(None, rawLine)
			if isCommentedOut: entry.leadingComment = rawLine[:rawLine.find(pvName)]
			d.asPvDict[pvName].append(entry)
	file.close()
	return (d)


def writeNewAutosaveFile(d, asFileName, verbose):
	""" Write a new autosave-request file, with information collected from
	an ioc directory.

	Given all of the information collected from an ioc directory (in the form
	of the instance ,d, of cmdFileDictionaries) and given the name of an
	autosave-request file, make a new copy of the file (append ".CVT" to the
	name) by merging information from 'd' with it.
	"""

	if (verbose): print "writeNewAutosaveFile: ", asFileName
	file = open(asFileName)
	newFile = open(asFileName+".CVT", "w+")
	newFile.write("#NEW: <command> -- marks a command in %s that was not found in old_dir.\n" % os.path.basename(asFileName))
	for rawLine in file:
		strippedLine = rawLine.strip("\t\r\n ")
		if (len(strippedLine) == 0):
			newFile.write(rawLine)
			continue
		if (isDecoration(strippedLine)):
			newFile.write(rawLine)
			continue
		if (verbose): print "\n'%s'" % strippedLine

		isCommentedOut = (rawLine[0] == '#')
		line = strippedLine.lstrip("#")

		if (len(line) == 0):
			newFile.write(rawLine);
			continue

		words = line.split()
		if words[0] == "file":
			# e.g., 'file motor_settings.req P=$(P),M=m1'
			fileName = words[1].strip('"')
			macroString = words[2].strip('"')

			found = False
			if (fileName in d.asFileDict.keys()):
				for entry in d.asFileDict[fileName]:
					if (not entry.used):
						found = True
						entry.used = True
						newFile.write("%sfile %s %s\n" % (entry.leadingComment, fileName, entry.value))
						break
			#if not found: newFile.write("#NEW: " + rawLine)
			if not found:
				if (not isCommentedOut): newFile.write("#NEW: ")
				newFile.write(rawLine)
		else:
			# just a pvName
			pvName = words[0]
			#if isCommentedOut and len(words) > 1: continue
			found = False
			if pvName in d.asPvDict.keys():
				for entry in d.asPvDict[pvName]:
					if (not entry.used):
						found = True
						entry.used = True
						newFile.write(rawLine)
			if not found:
				#newFile.write("#NEW: " + rawLine)
				if (not isCommentedOut): newFile.write("#NEW: ")
				newFile.write(rawLine)
			continue

	file.close()
	newFile.close()
	return (d)

	
def parseAutosaveFiles(dd, filespec, verbose, ignoreComments=False):
	"""	Call parseAutosaveFile() for all files in filespec, collecting their
	information into 'dd', a list of autosaveDictionary instances.
	"""
	
	autosaveFiles = glob.glob(filespec)
	for fileName in autosaveFiles:
		baseFileName = os.path.basename(fileName)
		dd[baseFileName] = autosaveDictionaries()
		dd[baseFileName] = parseAutosaveFile(dd[baseFileName], fileName, max(verbose,0),
			ignoreComments=ignoreComments)
	return (dd)

def writeNewAutosaveFiles(dd, filespec, verbose):
	""" Call writeNewAutosaveFile() for all files in filespec, using information
	from a list of autosaveDictionary instances, 'dd', to write the files, and
	marking each  entry in 'dd' as 'used', so its information will be included
	only once.
	"""

	autosaveFiles = glob.glob(filespec)
	for fileName in autosaveFiles:
		baseFileName = os.path.basename(fileName)
		if baseFileName in dd.keys():
			dd[baseFileName] = writeNewAutosaveFile(dd[baseFileName], fileName, max(verbose,0))
	return (dd)


def writeAutosaveDictionaries(dd, reportFile):
	" Write the content of all autosave dictionaries."

	writeHead(reportFile, "autosave-request-file lines:")
	for fileKey in dd.keys():
		reportFile.write("\n-------------------------------------------------\n")
		reportFile.write('%s\n' % fileKey)
		reportFile.write("-------------------------------------------------\n")
		d = dd[fileKey]
		for key in d.asKeyList:
			if key in d.asFileDict.keys():
				for entry in d.asFileDict[key]:
					reportFile.write("%sfile %s %s\n" % (entry.leadingComment, key, entry.value))
			elif key in d.asPvDict.keys():
				for entry in d.asPvDict[key]:
					reportFile.write("%s%s\n" % (entry.leadingComment, key))


def writeUnusedAutosaveEntries(dd, reportFile):
	" Write the unused content (the original text) of all autosave dictionaries."

	writeHead(reportFile, "unused autosave-request-file lines:")
	for fileKey in dd.keys():
		reportFile.write("\n-------------------------------------------------\n")
		reportFile.write('%s\n' % fileKey)
		d = dd[fileKey]
		writeUnusedEntries(d.asFileDict, reportFile)
		writeUnusedEntries(d.asPvDict, reportFile)


usage = """
Usage:    convertAutosaveFiles.py [options] old_dir [new_dir]
    option: -v[integer]   (verbose/debug level)
    option: -c            (ignore comments)

Synopsis: convertAutosaveFiles.py examines autosave-request files in the
    directory, 'old_dir', collecting PV names and 'file' commands into a set
    of dictionaries. If the directory, 'new_dir', is specified, it writes
    new autosave-request files, in 'new_dir', named <existing-file>.CVT, by
    merging information collected from 'old_dir' with the autosave-request
    files in 'new_dir'.
    
    If 'new_dir' is not specified, information collected from old_dir is
    written to 'convertAutosaveFiles.out'.  If 'new_dir' is specified, only
    the information not used to make new autosave-reqiest files is written to
    'convertAutosaveFiles.out', and that information is written with its
    original formatting.

Result: Files named auto*.req.CVT are created or overwritten.  The file
    'convertAutosaveFiles.out' is created or overwritten.  No other files are
    modified.
	
See also: makeAutosaveFiles.py, convertIocFiles.py
"""

def main():
	verbose = 0
	dirArg = 1
	ignoreComments = 0
	dd = {}
	if len(sys.argv) < 2:
		print usage
	else:
		for i in range(1,3):
			if (sys.argv[i][0] != '-'): break
			for (j, arg) in enumerate(sys.argv[i]):
				if (arg == 'v'):
					if len(arg) > j+1:
						j += 1
						verbose = int(arg)
					else:
						verbose = 1
					break # out of 'for (j, arg)...'
				elif (arg == 'c'):
					ignoreComments = 1
					break # out of 'for (j, arg)...'
		dirArg = i
		if (len(sys.argv) > dirArg):
			oldDir = sys.argv[dirArg]
			# user specified an old directory
			if not os.path.isdir(oldDir):
				print "\n'"+oldDir+"' is not a directory"
				return
			filespec = os.path.join(oldDir, "auto*.req")
			dd = parseAutosaveFiles(dd, filespec, verbose, ignoreComments=ignoreComments)
			if (verbose):
				dd = writeAutosaveDictionaries(dd, sys.stdout, False)

			dirArg = dirArg + 1

		wrote_new_files = 0
		if (len(sys.argv) > dirArg):
			newDir = sys.argv[dirArg]
			# user specified a new directory
			if not os.path.isdir(newDir):
				print "\n'"+newDir+"' is not a directory"
				return
			filespec = os.path.join(newDir, "auto*.req")
			dd = writeNewAutosaveFiles(dd, filespec, verbose)
			wrote_new_files = 1

		reportFile = open("convertAutosaveFiles.out", "w+")
		if (wrote_new_files):
			writeUnusedAutosaveEntries(dd, reportFile)
		else:
			writeAutosaveDictionaries(dd, reportFile)
		reportFile.close()
		
if __name__ == "__main__":
	main()
