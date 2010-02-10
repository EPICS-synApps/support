#!/usr/bin/env python

""" This module is intended to help convert an ioc directory from one version
of synApps to another.

Invoked as a program, it takes two arguments, the old directory and the new
directory, both of which are assumed to be ioc directories (i.e., they contain
st.cmd, or other .cmd files).  The program parses .cmd files in the source directory,
and accumulates information.  Then it parses .cmd files in the new directory.
For each .cmd file in the new directory, the program writes a .cmd.CVT file,
which is the .cmd file modified to agree as closely as seems reasonable with
information collected from the old directory.
"""

# Not recognized:
# 'epicsEnvSet EPICS_CA_MAX_ARRAY_BYTES 64008'
# 'var motorUtil_debug,1'
# 'iocInit'

import sys
import os
import glob
import string
import curses.ascii
from conversionUtils import *


def parse_cdCommands(d, fileName, verbose, ignoreComments=False):
	""" Parse the file 'cdCommands', collecting its information into the
	dictionary d.envDict, or d.varDict, as appropriate.
	"""

	file = open(fileName)
	for rawLine in file:
		line = rawLine.strip("\t\r\n")
		if (len(line) == 0): continue
		if (isDecoration(line)):continue
		if (verbose): print "\n'%s'" % line
		isCommentedOut = (line[0] == '#')
		if (isCommentedOut and ignoreComments): continue
		line = line.lstrip("#")
		words = line.split(' ')
		if words[0] == "putenv":
			words[1] = words[1].strip('"')
			(varName, varValue) = words[1].split('=')
			if verbose: print varName, ' = ', varValue
			if (varName not in d.envDict.keys()):
				d.envDict[varName] = []
			entry = dictEntry(varValue, rawLine)
			if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find("putenv")]
			d.envDict[varName].append(entry)
		else:
			(varName, varValue) = isVariableDefinition(line, max(verbose-1,0))
			if (varName):
				if (verbose): print " -- is a variable definition"
				if (varName not in d.varDict.keys()):
					d.varDict[varName] = []
				varValue = varValue.strip().strip('"')
				entry = dictEntry(varValue, rawLine)
				if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find(varName)]
				d.varDict[varName].append(entry)

	return (d)

def parse_envPaths(d, fileName, verbose, ignoreComments=False):
	""" Parse the file 'envPaths', collecting its information into the
	dictionary d.envDict.
	"""

	file = open(fileName)
	for rawLine in file:
		line = rawLine.strip("\t\r\n")
		if (len(line) == 0): continue
		if (isDecoration(line)):continue
		if (verbose): print "\n'%s'" % line
		isCommentedOut = (line[0] == '#')
		if (isCommentedOut and ignoreComments): continue
		line = line.lstrip("#")
		words = line.split('(')
		if words[0] == "epicsEnvSet":
			words[1] = words[1].strip(')').strip('"')
			(varName, varValue) = words[1].split(',')
			varName = varName.strip('"')
			varValue = varValue.strip('"')
			if verbose: print varName, ' = ', varValue
			if (varName not in d.envDict.keys()):
				d.envDict[varName] = []
			entry = dictEntry(varValue, rawLine)
			if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find("epicsEnvSet")]
			d.envDict[varName].append(entry)
	return (d)

def parseCmdFile(d, fileName, verbose, ignoreComments=False):
	""" Parse a .cmd file, collecting its information into an instance of
	class cmdFileDictionaries. 
	"""

	file = open(fileName)
	for rawLine in file:
		line = rawLine.strip("\t\r\n ")
		if (len(line) == 0): continue
		if (isDecoration(line)):continue
		if (verbose): print "\n'%s'" % line

		isCommentedOut = (line.strip()[0] == '#')
		if (isCommentedOut and ignoreComments): continue
		line = line.lstrip("#")

		if (len(line) == 0): continue

		(path, dbFile, macroString) = isdbLoadRecordsCall(line, max(verbose-1,0))
		if (dbFile):
			if (verbose): print " -- is a dbLoadRecords command"
			if (dbFile not in d.dbLoadRecordsDict.keys()):
				d.dbLoadRecordsDict[dbFile] = []
			entry = dictEntry(macroString, rawLine)
			if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find("dbLoad")]
			entry.macroDict = {}
			parms = macroString.split(',')
			for p in parms:
				if '=' in p:
					name, value = p.split('=')
					name = name.strip()
					entry.macroDict[name] = value.strip()
					if (verbose-1 > 0): print "macro: '%s' = '%s'" % (name, value)
			d.dbLoadRecordsDict[dbFile].append(entry)
			continue

		substitutionsFile = isdbLoadTemplateCall(line, max(verbose-1,0))
		if (substitutionsFile):
			if (verbose): print " -- is a dbLoadTemplate command"
			if (substitutionsFile not in d.dbLoadTemplateDict.keys()):
				d.dbLoadTemplateDict[substitutionsFile] = []
			entry = dictEntry(None, rawLine)
			if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find("dbLoad")]
			d.dbLoadTemplateDict[substitutionsFile].append(entry)
			continue

		(funcName, argString) = isFunctionCall(line, max(verbose-1,0))
		if (funcName):
			if (funcName == 'dbLoadDatabase') :
				if (verbose): print " -- is a dbLoadDatabase command (not recorded)"
				continue
			if (verbose): print " -- is a function call"
			if (funcName not in d.funcDict.keys()):
				d.funcDict[funcName] = []
			entry = dictEntry(argString, rawLine)
			if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find(funcName)]
			d.funcDict[funcName].append(entry)

			if (funcName == "putenv"):
				argString = argString.strip('"')
				(varName, varValue) = argString.split('=')
				if verbose: print varName, ' = ', varValue
				if (varName not in d.envDict.keys()):
					d.envDict[varName] = []
				entry = dictEntry(varValue, rawLine)
				if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find("putenv")]
				d.envDict[varName].append(entry)
			elif (funcName == "epicsEnvSet"):
				#print "parseCmdFile: found epicsEnvSet"
				argString = argString.strip('"')
				(varName, varValue) = argString.split(',')
				varName = varName.strip('"')
				value = varValue.strip('"')
				if verbose: print varName, ' = ', varValue
				if (varName not in d.envDict.keys()):
					d.envDict[varName] = []
				varValue = varValue.strip().strip('"')
				entry = dictEntry(varValue, rawLine)
				if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find("epicsEnvSet")]
				d.envDict[varName].append(entry)
			continue

		(varName, varValue) = isVariableDefinition(line, max(verbose-1,0))
		if (varName):
			if (verbose): print " -- is a variable definition"
			if (varName not in d.varDict.keys()):
				d.varDict[varName] = []
			entry = dictEntry(varValue, rawLine)
			if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find(varName)]
			d.varDict[varName].append(entry)
			continue

		(progName, argString) = isSeqCommand(line, max(verbose-1,0))
		if (progName):
			if (verbose): print " -- is a seq command"
			if (progName not in d.seqDict.keys()):
				d.seqDict[progName] = []
			entry = dictEntry(argString, rawLine)
			if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find("seq")]
			d.seqDict[progName].append(entry)
			continue

		scriptName = isScriptCommand(line, max(verbose-1,0))
		if (scriptName):
			if (verbose): print " -- is a script command"
			if (scriptName not in d.scriptDict.keys()):
				d.scriptDict[scriptName] = []
			entry = dictEntry(None, rawLine)
			if (isCommentedOut): entry.leadingComment = rawLine[0:rawLine.find("<")]
			d.scriptDict[scriptName].append(entry)
			continue

		if (verbose): print " -- is not recognized"

	file.close()
	return (d)

def writeNewCmdFile(d, fileName, verbose):
	""" Write a new .cmd file, with information collected from
	an ioc directory.

	Given all of the information collected from an ioc directory (in the
	form of the instance ,d, of cmdFileDictionaries) and given the name of a
	existing .cmd file, make a new copy of the .cmd file (append ".CVT" to
	the name) by merging information from 'd' with it.
	"""

	if (verbose): print "writeNewCmdFile: ", fileName
	file = open(fileName)
	newFile = open(fileName+".CVT", "w+")
	newFile.write("#NEW: <command> -- marks a command in %s that was not found in old_dir.\n" % os.path.basename(fileName))
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

		if (isCommentedOut or (len(line) == 0)):
			newFile.write(rawLine);
			continue

		(path, dbFile, macroString) = isdbLoadRecordsCall(line, max(verbose-1,0))
		if (dbFile):
			if (verbose): print " -- is a dbLoadRecords command"
			found = False
			if (dbFile in d.dbLoadRecordsDict.keys()):
				for entry in d.dbLoadRecordsDict[dbFile]:
					if (not entry.used):
						found = True
						entry.used = True
						fullname = os.path.join(path, dbFile)
						newFile.write("%sdbLoadRecords(\"%s\", \"%s\")\n" % (entry.leadingComment,fullname, entry.value))
						break
			if not found:
				if (not isCommentedOut): newFile.write("#NEW: ")
				newFile.write(rawLine)
			continue

		substitutionsFile = isdbLoadTemplateCall(line, max(verbose-1,0))
		if (substitutionsFile):
			if (verbose): print " -- is a dbLoadTemplate command"
			found = False
			if (substitutionsFile in d.dbLoadTemplateDict.keys()):
				for entry in d.dbLoadTemplateDict[substitutionsFile]:
					if (not entry.used):
						found = True
						entry.used = True
						newFile.write("%sdbLoadTemplate(\"%s\")\n" % (entry.leadingComment, substitutionsFile))
						break
			#if not found: newFile.write("#NEW: " + rawLine)
			if not found:
				if (not isCommentedOut): newFile.write("#NEW: ")
				newFile.write(rawLine)
			continue

		(funcName, argString) = isFunctionCall(line, max(verbose-1,0))
		if (funcName):
			if (funcName == 'dbLoadDatabase') :
				if (verbose): print " -- is a dbLoadDatabase command (use new command)"
				newFile.write(rawLine)
				continue
			if (verbose): print " -- is a function call"
			found = False
			if (funcName in d.funcDict.keys()):
				for entry in d.funcDict[funcName]:
					if (not entry.used):
						found = True
						entry.used = True
						newFile.write("%s%s(%s)\n" % (entry.leadingComment, funcName, entry.value))
						break
			#if not found: newFile.write("#NEW: " + rawLine)
			if not found:
				if (not isCommentedOut): newFile.write("#NEW: ")
				newFile.write(rawLine)
			continue

		(varName, varValue) = isVariableDefinition(line, max(verbose-1,0))
		if (varName):
			if (verbose): print " -- is a variable definition"
			found = False
			if (varName in d.varDict.keys()):
				for entry in d.varDict[varName]:
					if (not entry.used):
						found = True
						entry.used = True
						newFile.write("%s%s = %s\n" % (entry.leadingComment, varName, entry.value))
						break
			#if not found: newFile.write("#NEW: " + rawLine)
			if not found:
				if (not isCommentedOut): newFile.write("#NEW: ")
				newFile.write(rawLine)
			continue

		(progName, argString) = isSeqCommand(line, max(verbose-1,0))
		if (progName):
			if (verbose): print " -- is a seq command"
			found = False
			if (progName in d.seqDict.keys()):
				for entry in d.seqDict[progName]:
					if (not entry.used):
						found = True
						entry.used = True
						newFile.write("%sseq %s, %s\n" % (entry.leadingComment, progName, entry.value))
						break
			#if not found: newFile.write("#NEW: " + rawLine)
			if not found:
				if (not isCommentedOut): newFile.write("#NEW: ")
				newFile.write(rawLine)
			continue

		scriptName = isScriptCommand(line, max(verbose-1,0))
		if (scriptName):
			if (verbose): print " -- is a script command"
			found = False
			if (scriptName in d.scriptDict.keys()):
				for entry in d.scriptDict[scriptName]:
					if (not entry.used):
						found = True
						entry.used = True
						newFile.write("%s< %s\n" % (entry.leadingComment, scriptName))
						break
			#if not found: newFile.write("#NEW: " + rawLine)
			if not found:
				if (not isCommentedOut): newFile.write("#NEW: ")
				newFile.write(rawLine)
			continue

		newFile.write(rawLine)

	file.close()
	newFile.close()
	return (d)


def writeCmdFileDictionaries(d, reportFile):
	print "writeCmdFileDictionaries() is not implemented yet"




def writeUnusedCmdFileEntries(d, outFile):
	""" Write the unused information contained in an instance of 'class
	cmdFileDictionaries', in most cases with its original formatting.
	"""


	writeHead(outFile, "unused dbLoadRecords commands:")
	writeUnusedEntries(d.dbLoadRecordsDict, outFile)

	writeHead(outFile, "unused dbLoadTemplate commands:")
	writeUnusedEntries(d.dbLoadTemplateDict, outFile)

	writeHead(outFile, "unused function calls:")
	writeUnusedEntries(d.funcDict, outFile)

	writeHead(outFile, "unused variable definitions:")
	writeUnusedEntries(d.varDict, outFile)

	writeHead(outFile, "unused seq commands:")
	writeUnusedEntries(d.seqDict, outFile)

	writeHead(outFile, "unused script commands:")
	writeUnusedEntries(d.scriptDict, outFile)

	writeHead(outFile, "unused environment-variable commands:")
	writeUnusedEntries(d.envDict, outFile)

def parseCmdFiles(d, filespec, verbose, ignoreComments=False):
	"""	Call parseCmdFile() for all files in filespec, collecting their
	information into 'dd', an instance of class 'cmdFileDictionaries'.
	"""

	cmdFiles = glob.glob(filespec)
	for fileName in cmdFiles:
		d = parseCmdFile(d, fileName, max(verbose,0), ignoreComments=ignoreComments)
	return (d)

def writeNewCmdFiles(d, filespec, verbose):
	""" Call writeNewCmdFile() for all files in filespec, using information
	from a list of autosaveDictionary instances, 'd', to write the files, and
	marking each  entry in 'd' as 'used', so its information will be included
	only once.
	"""

	cmdFiles = glob.glob(filespec)
	for fileName in cmdFiles:
		d = writeNewCmdFile(d, fileName, max(verbose,0))
	return(d)

usage = """
Usage:    convertCmdFiles.py [options] old_dir [new_dir]
    option: -v[integer]   (verbose/debug level)
    option: -c            (ignore comments)

Examples: convertCmdFiles.py <old_dir> <new_dir>
    convertCmdFiles.py <old_dir>
    convertCmdFiles.py -v1 <old_dir> <new_dir>

Synopsis: convertCmdfiles.py examines .cmd files in old_dir, collecting
    dbLoadRecords/Template commands, function calls, variable
    assignments (though not 'var' commands), SNL program invocations,
    and script commands.

    If new_dir is specified, new versions of all .cmd files in
    new_dir (named, e.g., st.cmd.CVT) are created or overwritten.
    The new files are patched with information extracted from
    old_dir.  The program notes whether commands in old_dir were
    commented out, and it uses that information in writing
    commands for new_dir.

    The program also creates or overwrites the file
    'convertCmdFiles.out' in the current directory.  This file contains
    a list of the commands found in old_dir.  If new_dir was specified,
    only those commands from old_dir that did not find a place in
    new_dir are listed.

Result: Files named *.CVT are created or overwritten.  The file
    'convertCmdFiles.out' is created or overwritten.  No other files are
    modified.
	
See also: makeAutosaveFiles.py, convertIocFiles.py
"""

def main():
	verbose = 0
	dirArg = 1
	ignoreComments = 0
	d = cmdFileDictionaries()
	subFileDict = {}

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
			filespec = os.path.join(oldDir, "*.cmd")
			d = parseCmdFiles(d, filespec, verbose, ignoreComments=ignoreComments)
			if (verbose): writeCmdFileDictionaries(d, sys.stdout)

			dirArg = dirArg + 1

		wrote_new_files = 0
		if (len(sys.argv) > dirArg):
			newDir = sys.argv[dirArg]
			# user specified a new directory
			if not os.path.isdir(newDir):
				print "\n'"+newDir+"' is not a directory"
				return
			filespec = os.path.join(newDir, "*.cmd")
			d = writeNewCmdFiles(d, filespec, verbose)
			wrote_new_files = 1

			# parse cdCommands or envPaths file
			file = os.path.join(newDir, "cdCommands")
			if os.path.isfile(file):
				d = parse_cdCommands(d, file, verbose, ignoreComments=ignoreComments)
			else:
				file = os.path.join(newDir, "envPaths")
				if os.path.isfile(file):
					d = parse_envPaths(d, file, verbose)


		reportFile = open("convertCmdFiles.out", "w+")
		if (wrote_new_files):
			writeUnusedCmdFileEntries(d, reportFile)
		else:
			writeCmdFileDictionaries(d, reportFile)
		reportFile.close()

		
if __name__ == "__main__":
	main()
