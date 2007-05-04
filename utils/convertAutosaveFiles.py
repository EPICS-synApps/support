#!/usr/bin/env python

import sys
import os
import glob
import string
import curses.ascii
from conversionUtils import *
from convertCmdFiles import *
from convertSubFiles import *

class autosaveDictionaries:
	def __init__(self):
		self.asFileDict = {}
		self.asPvDict = {}
		self.asKeyList = []

class autosaveIncludeEntry:
	def __init__(self, name):
		self.name = name
		self.pattern = []


def getRequestFilePath(cmdFileDicts):
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
				if (value[i] == None): print "getRequestFilePath: '%s' not found in varDict" % words[i]
			else:
				# string, which might contain a macro
				words[i] = words[i].strip().strip('"')
				if (words[i].find('$(') != -1):
					# macro
					words[i] = words[i][2:].strip(')')
					value[i] = getEnv(cmdFileDicts.envDict, words[i])
					if (value[i] == None): print "getRequestFilePath: '%s' not found in envDict" % words[i]
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
	startIx = 0
	while startIx < len(s)-4:
		Ix = s[startIx:].find("$(")
		if (Ix == -1): return (s)
		macroIx = startIx + Ix + 2
		endIx = s[macroIx:].find(")")
		if (endIx == -1): return (s)
		macro = s[macroIx:macroIx+endIx]
		startIx = macroIx+endIx+1
		if macro in macroDict.keys():
			value = macroDict[macro]
			s = s[:macroIx-2] + value + s[macroIx+endIx+1:]
			startIx = s.find("$(")
		else:
			startIx = macroIx+endIx+1
	return s

def makeMacroString(pattern, macroDict):
	macroString = ""
	for macro in pattern:
		if macro in macroDict.keys():
			value = macroDict[macro]
			macroString = macroString + "%s=%s " % (macro, value)
		else:
			macroString = macroString + "%s=??? " % macro
	return replaceMacrosWithValues(macroString, macroDict)

def writeStandardAutosaveFiles(cmdFileDicts, subFileDict, dirName="."):
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
				macroString = makeMacroString(settingsEntry.pattern, entry.macroDict)
				settingsFile.write("file %s %s\n" % (settingsEntry.name, macroString))
		if dbBaseName in positionsReqFileDict.keys():
			positionsEntry =  positionsReqFileDict[dbBaseName]
			for entry in cmdFileDicts.dbLoadRecordsDict[db]:
				if entry.leadingComment: continue
				macroString = makeMacroString(positionsEntry.pattern, entry.macroDict)
				positionsFile.write("file %s %s\n" % (positionsEntry.name, macroString))
	for subFile in subFileDict.keys():
		for db in subFileDict[subFile].templateFileDict.keys():
			dbBaseName = db[:db.find(".")]
			for dictEntry in subFileDict[subFile].templateFileDict[db]:
				if dictEntry.leadingComment: continue
				if dbBaseName in settingsReqFileDict.keys():
					settingsEntry =  settingsReqFileDict[dbBaseName]
					for macroDict in dictEntry.macroDictList:
						macroString = makeMacroString(settingsEntry.pattern, macroDict)
						settingsFile.write("file %s %s\n" % (settingsEntry.name, macroString))
				if dbBaseName in positionsReqFileDict.keys():
					positionsEntry =  positionsReqFileDict[dbBaseName]
					for macroDict in dictEntry.macroDictList:
						macroString = makeMacroString(positionsEntry.pattern, macroDict)
						positionsFile.write("file %s %s\n" % (positionsEntry.name, macroString))


commaToSpaceTable = string.maketrans(',',' ')

def cannotBePvName(s):
	for c in s:
		if c.isspace(): return True
		if curses.ascii.ispunct(c) and (not c in [':', '.', '$', '(', ')']): return True
	return False

def parseAutosaveFile(d, asFileName, verbose):
	file = open(asFileName)
	for rawLine in file:
		line = rawLine.strip("\t\r\n ")
		if (len(line) == 0): continue
		if (isDecoration(line)):continue
		if (verbose): print "\n'%s'" % line

		isCommentedOut = (line[0] == '#')
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
			if not found: newFile.write("#NEW: " + rawLine)
		else:
			# just a pvName
			pvName = words[0]
			if isCommentedOut and len(words) > 1: continue
			found = False
			if pvName in d.asPvDict.keys():
				for entry in d.asPvDict[pvName]:
					if (not entry.used):
						found = True
						entry.used = True
						newFile.write(rawLine)
			else:
				newFile.write("#NEW: " + rawLine)
			continue

	file.close()
	newFile.close()
	return (d)


					
def parseAutosaveFiles(dd, filespec, verbose):
	autosaveFiles = glob.glob(filespec)
	for fileName in autosaveFiles:
		baseFileName = os.path.basename(fileName)
		dd[baseFileName] = autosaveDictionaries()
		dd[baseFileName] = parseAutosaveFile(dd[baseFileName], fileName, max(verbose,0))
	return (dd)


def writeNewAutosaveFiles(dd, filespec, verbose):
	autosaveFiles = glob.glob(filespec)
	for fileName in autosaveFiles:
		baseFileName = os.path.basename(fileName)
		if baseFileName in dd.keys():
			dd[baseFileName] = writeNewAutosaveFile(dd[baseFileName], fileName, max(verbose,0))
	return (dd)

def writeAutosaveDictionaries(dd, reportFile):
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
	writeHead(reportFile, "unused autosave-request-file lines:")
	for fileKey in dd.keys():
		reportFile.write("\n-------------------------------------------------\n")
		reportFile.write('%s\n' % fileKey)
		d = dd[fileKey]
		writeUnusedEntries(d.asFileDict, reportFile)
		writeUnusedEntries(d.asPvDict, reportFile)


usage = "no usage info yet"
def main():
	verbose = 0
	dirArg = 1
	dd = {}
	if len(sys.argv) < 2:
		print usage
	else:
		if (sys.argv[1][0] == '-'):
			for i in range(len(sys.argv[1])):
				print "char %d = '%c'" % (i, sys.argv[1][i])
				if (sys.argv[1][i] == 'v'):
					if len(sys.argv[1]) > i+1:
						i = i + 1
						verbose = int(sys.argv[1][i])
					else:
						verbose = 1
					break
			dirArg = 2

		if (len(sys.argv) > dirArg):
			oldDir = sys.argv[dirArg]
			# user specified an old directory
			if not os.path.isdir(oldDir):
				print "\n'"+oldDir+"' is not a directory"
				return
			filespec = os.path.join(oldDir, "auto*.req")
			dd = parseAutosaveFiles(dd, filespec, verbose)
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

		reportFile = open("cvtAutosaveFiles.out", "w+")
		if (wrote_new_files):
			writeUnusedAutosaveEntries(dd, reportFile)
		else:
			writeAutosaveDictionaries(dd, reportFile)
		reportFile.close()
		
if __name__ == "__main__":
	main()
