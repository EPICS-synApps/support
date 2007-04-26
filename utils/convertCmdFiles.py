#!/usr/bin/env python
# This program is intended to help convert an ioc directory from one version
# of synApps to another.  It takes two arguments, the old directory and the new
# directory, both of which are assumed to be ioc directories (i.e., they contain
# st.cmd, or other .cmd files).  The program parses .cmd files in the source directory,
# and accumulates information.  Then it parses .cmd files in the new directory.
# For each .cmd file in the new directory, the program writes a .cmd.new file,
# which is the .cmd file modified to agree as closely as seems reasonable with
# information collected from the old directory.

# Not recognized:
# 'epicsEnvSet EPICS_CA_MAX_ARRAY_BYTES 64008'
# 'var motorUtil_debug,1'
# 'iocInit'

import sys
import os
import glob
import string
import curses.ascii

# We're going to need a quick way to tell if a word might be legal as a
# shell variable (consists of alphanumeric characters or underscores)
# isalnum() almost works, and it would make a good preliminary check,
# if we changed underscore to a letter.  The following translation table
# does that when supplied to string.translate().
transtable = string.maketrans('_','a')

dbDict = {}
substitutionsDict = {}
funcDict = {}
varDict = {}
seqDict = {}
scriptDict = {}
envDict = {}

class dictEntry:
	def __init__(self, isCommentedOut, value, origLine):
		self.isCommentedOut = isCommentedOut
		self.value = value
		self.used = False
		self.origLine = origLine
		self.macroDict = None

	def __str__(self):
		if (self.value != None):
			s = self.value
		else:
			s = ""
		return s

def parse_cdCommands(fileName, verbose):
	file = open(fileName)
	for rawLine in file:
		line = rawLine.strip("\t\r\n")
		if (len(line) == 0): continue
		if (isDecoration(line)):continue
		if (verbose): print "\n'%s'" % line
		isCommentedOut = (line[0] == '#')
		line = line.lstrip("#")
		words = line.split(' ')
		if words[0] == "putenv":
			words[1] = words[1].strip('"')
			(var, value) = words[1].split('=')
			if verbose: print var, ' = ', value
			envDict[var] = value

def parse_envPaths(fileName, verbose):
	file = open(fileName)
	for rawLine in file:
		line = rawLine.strip("\t\r\n")
		if (len(line) == 0): continue
		if (isDecoration(line)):continue
		if (verbose): print "\n'%s'" % line
		isCommentedOut = (line[0] == '#')
		line = line.lstrip("#")
		words = line.split('(')
		if words[0] == "epicsEnvSet":
			words[1] = words[1].strip('"')
			(var, value) = words[1].split(',')
			if verbose: print var, ' = ', value
			envDict[var] = value

def isdbLoadRecordsCall(line, verbose):
	if (line.find('dbLoadRecords(') == -1): return (0,0,0)
	# e.g., dbLoadRecords("stdApp/Db/IDctrl.db","P=4id:,xx=04", std)
	words = line.split('(',1)
	words = words[1].rstrip(')').split(',',1)
	words[0] = words[0].strip('"')
	if (len(words) >= 2):
		(path, dbFile) = os.path.split(words[0])
		macroString = words[1].strip().strip('"')
		return (path, dbFile, macroString)
	return (0,0,0)

def isdbLoadTemplateCall(line, verbose):
	if (line.find('dbLoadTemplate(') == -1): return (0)
	# e.g., dbLoadTemplate("myTemplate.substitutions")
	words = line.split('"',2)
	if (len(words) > 2):
		# e.g., 'dbLoadTemplate(', 'myTemplate.substitutions', ')'
		return (words[1])
	return(0)

def countParen(s, verbose):
	openParen = 0
	netParen = 0
	closeIndex = 0
	inString1 = False
	inString2 = False
	#print "countParen: s='"+s+"'" 
	for i in range(len(s)):
		if (s[i] == '"'): inString1 = not inString1
		if (s[i] == "'"): inString2 = not inString2
		if (inString1 or inString2): continue
		if (s[i] == '('):
			openParen = openParen + 1
			netParen = netParen + 1
		if (s[i] == ')'):
			netParen = netParen - 1
			if (netParen == 0):
				closeIndex = i
	#print "countParen: openParen=", openParen, " netParen=", netParen 
	return (openParen,netParen, closeIndex)

def isFunctionCall(line, verbose):
	(openParen, netParen, closeIndex) = countParen(line, max(verbose-1,0))
	if (closeIndex != 0): line = line[0:closeIndex+1]
	if (openParen == 0): return (0,0)
	if (netParen != 0): return (0,0)
	line = line.lstrip('#\t ')
	if (len(line) == 0): return (0,0)
	if (line[0] == '('): return (0,0)
	if (line.find(')') < line.find('(')): return(0,0)

	# reject 'abc def()'
	words = line.split(None,1)
	if (words[0].find('(') == -1) and (words[1][0] != '('): return (0,0)

	words = line.split('(',1)
	words[1] = words[1][0:len(words[1])-1] # strip closing paren
	funcName = words[0]
	argString = words[1]
	if (verbose): print "FUNCTION: ", funcName, " ARG: '%s'" % argString
	return (funcName, argString)

def isLegalName(ss, verbose):
	# get string with legal characters converted to something alphanumeric
	s = ss.translate(transtable)
	if s[0].isdigit(): return (False)
	if (verbose): print "isLegalName('%s') = %s" % (ss, s.isalnum())
	return s.isalnum()

def isVariableDefinition(s, verbose):
	s = s.lstrip('#\t ')
	if (s.find('=') == -1): return (0,0)
	words = s.split('=',1)
	if (verbose): print words
	if (len(words) < 2): return (0,0)
	if (len(words[0]) == 0): return (0,0)
	words[0] = words[0].strip()
	if not (isLegalName(words[0], max(verbose-1,0))): return (0,0)
	varName = words[0]
	varValue = words[1]
	return (varName, varValue)
	
def isSeqCommand(s, verbose):
	s = s.lstrip('#\t ')
	if (len(s) == 0): return (0,0)
	s = s.split(None,1)
	if (s[0] != 'seq'): return (0,0)
	split = s[1].split(',', 1)
	if (len(split) == 1): return (0,0)
	return split

def isScriptCommand(s, verbose):
	s = s.lstrip('#\t ')
	if (len(s) < 2): return (0)
	if (s[0] != '<'): return (0)
	if (s[0] != '<'): return (0)	
	return s[1:].lstrip()

def isDecoration(s):
	for c in s:
		if curses.ascii.ispunct(c): continue
		if curses.ascii.isspace(c): continue
		if curses.ascii.iscntrl(c): continue
		return(0)
	return(1)


def parseCmdFile(fileName, verbose):
	file = open(fileName)
	for rawLine in file:
		line = rawLine.strip("\t\r\n ")
		if (len(line) == 0): continue
		if (isDecoration(line)):continue
		if (verbose): print "\n'%s'" % line

		isCommentedOut = (line[0] == '#')
		line = line.lstrip("#")

		if (len(line) == 0): continue

		(path, dbFile, macroString) = isdbLoadRecordsCall(line, max(verbose-1,0))
		if (dbFile):
			if (verbose): print " -- is a dbLoadRecords command"
			if (dbFile not in dbDict.keys()):
				dbDict[dbFile] = []
			entry = dictEntry(isCommentedOut, macroString, rawLine)
			entry.macroDict = {}
			parms = macroString.split(',')
			for p in parms:
				if '=' in p:
					name, value = p.split('=')
					name = name.strip()
					entry.macroDict[name] = value.strip()
					if (verbose-1 > 0): print "macro: '%s' = '%s'" % (name, value)
			dbDict[dbFile].append(entry)
			continue

		substitutionsFile = isdbLoadTemplateCall(line, max(verbose-1,0))
		if (substitutionsFile):
			if (verbose): print " -- is a dbLoadTemplate command"
			if (substitutionsFile not in substitutionsDict.keys()):
				substitutionsDict[substitutionsFile] = []
			substitutionsDict[substitutionsFile].append(dictEntry(isCommentedOut, None, rawLine))
			continue

		(funcName, argString) = isFunctionCall(line, max(verbose-1,0))
		if (funcName):
			if (funcName == 'dbLoadDatabase') :
				if (verbose): print " -- is a dbLoadDatabase command (not recorded)"
				continue
			if (verbose): print " -- is a function call"
			if (funcName not in funcDict.keys()):
				funcDict[funcName] = []
			funcDict[funcName].append(dictEntry(isCommentedOut, argString, rawLine))
			continue

		(varName, varValue) = isVariableDefinition(line, max(verbose-1,0))
		if (varName):
			if (verbose): print " -- is a variable definition"
			if (varName not in varDict.keys()):
				varDict[varName] = []
			varDict[varName].append(dictEntry(isCommentedOut, varValue, rawLine))
			continue

		(progName, argString) = isSeqCommand(line, max(verbose-1,0))
		if (progName):
			if (verbose): print " -- is a seq command"
			if (progName not in seqDict.keys()):
				seqDict[progName] = []
			seqDict[progName].append(dictEntry(isCommentedOut, argString, rawLine))
			continue

		scriptName = isScriptCommand(line, max(verbose-1,0))
		if (scriptName):
			if (verbose): print " -- is a script command"
			if (scriptName not in scriptDict.keys()):
				scriptDict[scriptName] = []
			scriptDict[scriptName].append(dictEntry(isCommentedOut, None, rawLine))
			continue

		if (verbose): print " -- is not recognized"

	file.close()

def editCmdFile(fileName, verbose):
	if (verbose): print "editCmdFile: ", fileName
	file = open(fileName)
	newFile = open(fileName+".new", "w+")
	newFile.write("#??? <command> -- marks a command in %s that was not found in old_dir." % os.path.basename(fileName))
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

		(path, dbFile, macroString) = isdbLoadRecordsCall(line, max(verbose-1,0))
		if (dbFile):
			if (verbose): print " -- is a dbLoadRecords command"
			found = False
			if (dbFile in dbDict.keys()):
				for entry in dbDict[dbFile]:
					if (entry.used): continue
					else:
						found = True
						entry.used = True
						if entry.isCommentedOut: newFile.write("#")
						fullname = os.path.join(path, dbFile)
						newFile.write("dbLoadRecords(\"%s\", \"%s\")\n" % (fullname, entry.value))
						break
			if not found: newFile.write("#??? " + rawLine)
			continue

		substitutionsFile = isdbLoadTemplateCall(line, max(verbose-1,0))
		if (substitutionsFile):
			if (verbose): print " -- is a dbLoadTemplate command"
			found = False
			if (substitutionsFile in substitutionsDict.keys()):
				for entry in substitutionsDict[substitutionsFile]:
					if (entry.used): continue
					else:
						found = True
						entry.used = True
						if entry.isCommentedOut: newFile.write("#")
						newFile.write("dbLoadTemplate(\"%s\")\n" % substitutionsFile)
						break
			if not found: newFile.write("#??? " + rawLine)
			continue

		(funcName, argString) = isFunctionCall(line, max(verbose-1,0))
		if (funcName):
			if (funcName == 'dbLoadDatabase') :
				if (verbose): print " -- is a dbLoadDatabase command (use new command)"
				newFile.write(rawLine)
				continue
			if (verbose): print " -- is a function call"
			found = False
			if (funcName in funcDict.keys()):
				for entry in funcDict[funcName]:
					if (entry.used): continue
					else:
						found = True
						entry.used = True
						if entry.isCommentedOut: newFile.write("#")
						newFile.write("%s(%s)\n" % (funcName, entry.value))
						break
			if not found: newFile.write("#??? " + rawLine)
			continue

		(varName, varValue) = isVariableDefinition(line, max(verbose-1,0))
		if (varName):
			if (verbose): print " -- is a variable definition"
			found = False
			if (varName in varDict.keys()):
				for entry in varDict[varName]:
					if (entry.used): continue
					else:
						found = True
						entry.used = True
						if entry.isCommentedOut: newFile.write("#")
						newFile.write("%s = %s\n" % (varName, entry.value))
						break
			if not found: newFile.write("#??? " + rawLine)
			continue

		(progName, argString) = isSeqCommand(line, max(verbose-1,0))
		if (progName):
			if (verbose): print " -- is a seq command"
			found = False
			if (progName in seqDict.keys()):
				for entry in seqDict[progName]:
					if (entry.used): continue
					else:
						found = True
						entry.used = True
						if entry.isCommentedOut: newFile.write("#")
						newFile.write("seq %s, %s\n" % (progName, entry.value))
						break
			if not found: newFile.write("#??? " + rawLine)
			continue

		scriptName = isScriptCommand(line, max(verbose-1,0))
		if (scriptName):
			if (verbose): print " -- is a script command"
			found = False
			if (scriptName in scriptDict.keys()):
				for entry in scriptDict[scriptName]:
					if (entry.used): continue
					else:
						found = True
						entry.used = True
						if (entry.isCommentedOut): newFile.write("#")
						newFile.write("< %s\n" % scriptName)
						break
			if not found: newFile.write("#??? " + rawLine)
			continue

		newFile.write(rawLine)

	file.close()
	newFile.close()


def writeHead(file, s, unused):
	file.write("\n############################################################################\n")
	if unused: file.write("Unused ")
	file.write(s + "\n")
	file.write("############################################################################\n")

# Write the information collected from .cmd files, in most cases with its
# original formatting.  If (printUnused), then only write information that
# is not marked "used".
def writeDictionaries(outFile, printUnused=False):

	writeHead(outFile, "dbLoadRecords commands:", printUnused)
	if (len(dbDict.keys()) == 0):
		outFile.write("None\n")
	else:
		for key in dbDict.keys():
			printedKey = False
			for entry in dbDict[key]:
				if not entry.used or not printUnused: 
					outFile.write(entry.origLine)

	writeHead(outFile, "dbLoadTemplate commands:", printUnused)
	if (len(substitutionsDict.keys()) == 0):
		outFile.write("None\n")
	else:
		for key in substitutionsDict.keys():
			for entry in substitutionsDict[key]:
				if not entry.used or not printUnused: 
					outFile.write(entry.origLine)

	writeHead(outFile, "function calls:", printUnused)
	if (len(funcDict.keys()) == 0):
		outFile.write("None\n")
	else:
		for key in funcDict.keys():
			printedKey = False
			for entry in funcDict[key]:
				if not entry.used or not printUnused: 
					outFile.write(entry.origLine)

	writeHead(outFile, "variable definitions:", printUnused)
	if (len(varDict.keys()) == 0):
		outFile.write("None\n")
	else:
		for key in varDict.keys():
			printedKey = False
			for entry in varDict[key]:
				if not entry.used or not printUnused: 
					outFile.write(entry.origLine)

	writeHead(outFile, "seq commands:", printUnused)
	if (len(seqDict.keys()) == 0):
		outFile.write("None\n")
	else:
		for key in seqDict.keys():
			printedKey = False
			for entry in seqDict[key]:
				if not entry.used or not printUnused: 
					outFile.write(entry.origLine)

	writeHead(outFile, "script commands:", printUnused)
	if (len(scriptDict.keys()) == 0):
		outFile.write("None\n")
	else:
		for key in scriptDict.keys():
			for entry in scriptDict[key]:
				if not entry.used or not printUnused: 
					outFile.write(entry.origLine)

	writeHead(outFile, "environment variables:", False)
	if (len(envDict.keys()) == 0):
		outFile.write("None\n")
	else:
		for key in envDict.keys():
			outFile.write(key + "='" + envDict[key] + "'\n")

def parseCmdFiles(filespec, verbose):
	cmdFiles = glob.glob(filespec)
	for fileName in cmdFiles:
		parseCmdFile(fileName, max(verbose,0))

def editCmdFiles(filespec, verbose):
	cmdFiles = glob.glob(filespec)
	for fileName in cmdFiles:
		editCmdFile(fileName, max(verbose,0))
	
def main():
	verbose = 0
	dirArg = 1
	if len(sys.argv) < 2:
		print "Usage:\tconvertCmdFiles.py [options] old_dir [new_dir]"
		print "\toptions: -v (verbose/debug level)"
		print "\nExamples: convertCmdFiles.py <old_dir> <new_dir>"
		print "\tconvertCmdFiles.py <old_dir>"
		print "\tconvertCmdFiles.py -v1 <old_dir> <new_dir>"
		print "\nSynopsis: convertCmdfiles.py examines .cmd files in old_dir, collecting"
		print "\tdbLoadRecords/Template commands, function calls, variable"
		print "\tassignments (though not 'var' commands), SNL program invocations,"
		print "\tand script commands."
		print "\n\tIf new_dir is specified, new versions of all .cmd files in"
		print "\tnew_dir (named, e.g., st.cmd.new) are created or overwritten."
		print "\tThe new files are patched with information extracted from"
		print "\told_dir.  The program notes whether commands in old_dir were"
		print "\tcommented out, and it uses that information in writing"
		print "\tcommands for new_dir."
		print "\n\tThe program also creates or overwrites the file 'convert.out'"
		print "\tin the current directory.  This file contains a list of the"
		print "\tcommands found in old_dir.  If new_dir was specified, only"
		print "\tthose commands from old_dir that did not find a place in"
		print "\tnew_dir are listed."
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
			# user specified an old directory
			if not os.path.isdir(sys.argv[dirArg]):
				print "\n'"+sys.argv[dirArg]+"' is not a directory"
				return
			filespec = os.path.join(sys.argv[dirArg], "*.cmd")
			parseCmdFiles(filespec, verbose)
			if (verbose): writeDictionaries(sys.stdout, False)
			dirArg = dirArg + 1

		wrote_new_files = 0
		if (len(sys.argv) > dirArg):
			# user specified a new directory
			if not os.path.isdir(sys.argv[dirArg]):
				print "\n'"+sys.argv[dirArg]+"' is not a directory"
				return
			filespec = os.path.join(sys.argv[dirArg], "*.cmd")
			editCmdFiles(filespec, verbose)
			wrote_new_files = 1

			# parse cdCommands or envPaths file
			file = os.path.join(sys.argv[dirArg], "cdCommands")
			if os.path.isfile(file):
				parse_cdCommands(file, verbose)
			else:
				file = os.path.join(sys.argv[dirArg], "envPaths")
				if os.path.isfile(file):
					parse_envPaths(file, verbose)

		reportFile = open("convert.out", "w+")
		printUnusedInformation = wrote_new_files
		writeDictionaries(reportFile, printUnusedInformation)
		reportFile.close()

		
if __name__ == "__main__":
	main()
