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

transtable = string.maketrans('_','a')

class dictEntry:
	def __init__(self, isCommentedOut, value, origLine):
		self.isCommentedOut = isCommentedOut
		self.value = value
		self.used = False
		self.origLine = origLine

	def __str__(self):
		if (self.value != None):
			s = self.value
		else:
			s = ""
		return s

def isdbLoadRecordsCall(line, verbose):
	if (line.find('dbLoadRecords(') == -1): return (0,0,0)
	# e.g., dbLoadRecords("stdApp/Db/IDctrl.db","P=4id:,xx=04", std)
	words = line.split('"',4)
	if (len(words) > 2):
		# e.g., "dbLoadRecords(", "stdApp/Db/IDctrl.db", ",", "P=4id:,xx=04"
		(path, dbFile) = os.path.split(words[1])
		macroString = words[3]
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

def printHead(s, unused):
	print "\n############################################################################"
	if unused: print "Unused",
	print s
	print "############################################################################"

dbDict = {}
substitutionsDict = {}
funcDict = {}
varDict = {}
seqDict = {}
scriptDict = {}
funcName = ""
argString = ""
varName = ""
varValue = ""

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
			dbDict[dbFile].append(dictEntry(isCommentedOut, macroString, rawLine))
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

def printDictionaries(printUnused=False):

	printHead("dbLoadRecords commands:", printUnused)
	if (len(dbDict.keys()) == 0):
		print "None"
	else:
		for key in dbDict.keys():
			printedKey = False
			for entry in dbDict[key]:
				if printUnused:
					if not entry.used: print entry.origLine,
				else:
					if not printedKey:
						print key
						printedKey = True
					print "\t",
					if (entry.isCommentedOut): print '#',
					print entry.value

	printHead("dbLoadTemplate commands:", printUnused)
	if (len(substitutionsDict.keys()) == 0):
		print "None"
	else:
		for key in substitutionsDict.keys():
			for entry in substitutionsDict[key]:
				if printUnused:
					if not entry.used: print entry.origLine,
				else:
					if (entry.isCommentedOut): print '#',
					print key

	printHead("function calls:", printUnused)
	if (len(funcDict.keys()) == 0):
		print "None"
	else:
		for key in funcDict.keys():
			printedKey = False
			for entry in funcDict[key]:
				if printUnused:
					if not entry.used: print entry.origLine,
				else:
					if not printedKey:
						print key
						printedKey = True
					print "\t",
					if (entry.isCommentedOut): print '#',
					print entry.value

	printHead("variable definitions:", printUnused)
	if (len(varDict.keys()) == 0):
		print "None"
	else:
		for key in varDict.keys():
			printedKey = False
			for entry in varDict[key]:
				if printUnused:
					if not entry.used: print entry.origLine,
				else:
					if not printedKey:
						print key
						printedKey = True
					print "\t",
					if (entry.isCommentedOut): print '#',
					print entry.value

	printHead("seq commands:", printUnused)
	if (len(seqDict.keys()) == 0):
		print "None"
	else:
		for key in seqDict.keys():
			printedKey = False
			for entry in seqDict[key]:
				if printUnused:
					if not entry.used: print entry.origLine,
				else:
					if not printedKey:
						print key
						printedKey = True
					print "\t",
					if (entry.isCommentedOut):'#',
					print entry.value

	printHead("script commands:", printUnused)
	if (len(scriptDict.keys()) == 0):
		print "None"
	else:
		for key in scriptDict.keys():
			for entry in scriptDict[key]:
				if printUnused:
					if not entry.used: print entry.origLine,
				else:
					if (entry.isCommentedOut): print '#',
					print key
					
def parseCmdFiles(filespec, verbose):
	cmdFiles = glob.glob(filespec)
	for fileName in cmdFiles:
		parseCmdFile(fileName, max(verbose,0))

def editCmdFiles(filespec, verbose):
	cmdFiles = glob.glob(filespec)
	for fileName in cmdFiles:
		editCmdFile(fileName, max(verbose,0))
	printDictionaries(True)
	
def main():
	verbose = 0
	dirArg = 1
	if len(sys.argv) < 2:
		print "Usage:   convertCmdFiles.py [options] old_dir [new_dir]"
		print "Example: convertCmdFiles.py -v1 <old_dir>  <new_dir> >cvt.out"
	else:
		if (sys.argv[1][0] == '-'):
			for i in range(len(sys.argv[1])):
				if (sys.argv[1][i] == 'v'):
					i = i + 1
					verbose = max(1,int(sys.argv[1][i]))
			dirArg = 2

		if (len(sys.argv) > dirArg):
			if not os.path.isdir(sys.argv[dirArg]):
				print "\n'"+sys.argv[dirArg]+"' is not a directory"
				return
			filespec = os.path.join(sys.argv[dirArg], "*.cmd")
			parseCmdFiles(filespec, verbose)
			if (verbose): printDictionaries()
			dirArg = dirArg + 1

		if (len(sys.argv) > dirArg):
			if not os.path.isdir(sys.argv[dirArg]):
				print "\n'"+sys.argv[dirArg]+"' is not a directory"
				return
			filespec = os.path.join(sys.argv[dirArg], "*.cmd")
			editCmdFiles(filespec, verbose)

		
if __name__ == "__main__":
	main()
