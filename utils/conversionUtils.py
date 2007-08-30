#!/usr/bin/env python
"""This software is intended to help convert an ioc directory from one version
of synApps to another.
"""

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

class cmdFileDictionaries:
	"""A collection of dictionaries in which information from .cmd files, and
	the cdCommands or envPaths file is accumulated.  All dictionaries contain,
	as 'definitions', a list of instances of the class 'dictEntry'.
	"""
	def __init__(self):
		self.dbLoadRecordsDict = {}		# dbLoadRecordsDict[dbFileName][i].dictEntry
		self.dbLoadTemplateDict = {}	# dbLoadTemplateDict[subFileName][i].dictEntry
		self.funcDict = {}				# funcDict[funcName][i].dictEntry
		self.varDict = {}				# varDict[varName][i].dictEntry
		self.seqDict = {}				# seqDict[seqName][i].dictEntry
		self.scriptDict = {}			# scriptDict[scriptName][i].dictEntry
		self.envDict = {}				# envDict[varName][i].dictEntry


class dictEntry:
	def __init__(self, value, origLine):
		self.leadingComment = ""		# comment from original line
		self.trailingComment = ""		# comment from original line
		self.value = value				# depends on dictionary
		self.used = False				# has been used to write a new file
		self.origLine = origLine		# original line from old ioc dir
		self.macroDict = None			# {name:value, ...}

	def __str__(self):
		if (self.value != None):
			s = self.value
		else:
			s = ""
		return s



def countUnquotedBrackets(s, openChar, closeChar, verbose):
	"""Count occurrences of 'openChar' and 'closeChar' (typically, '(' and ')')
	in the string s,  ignoring those within a quoted string.  Return the number
	of 'openChar' characters found, the number of 'openChar' characters minus
	the number of 'closeChar', found, and the index at which the last 'closeChar'
	was found.
	"""
	openBrackets = 0
	netBrackets = 0   # numOpened - numClosed
	closeIndex = 0
	inString1 = False
	inString2 = False
	#print "countBrackets: s='"+s+"'" 
	for i in range(len(s)):
		if (s[i] == '"'): inString1 = not inString1
		if (s[i] == "'"): inString2 = not inString2
		if (inString1 or inString2): continue
		if (s[i] == openChar):
			openBrackets = openBrackets + 1
			netBrackets = netBrackets + 1
		if (s[i] == closeChar):
			netBrackets = netBrackets - 1
			if (netBrackets == 0):
				closeIndex = i
	#print "countBrackets: openBrackets=", openBrackets, " netBrackets=", netBrackets 
	return (openBrackets, netBrackets, closeIndex)


def nextLine(lines, line):
	"""Increment line number.  If the new line is a comment, continue
	incrementing until a non-comment line is found, or the last line is
	reached.
	"""
	maxLines = len(lines)
	line = line + 1
	while (line < maxLines):
		newLine = lines[line].lstrip()
		if ((newLine != "") and (newLine[0] != "#")):
			return(line)
		line = line + 1
	return line



def findUnquotedLegalOrTerminator(lines, line, char, isLegal, terminatorChars):
	""" Find the first unquoted legal character or terminator in a list of strings.
	
	Search through a list of strings (lines[]), starting at lines[line][char],
	for a legal character (isLegal(c) == True), or a terminator (c in
	terminatorChars). Do not test characters within quotes, or the quote character
	that ends a quoted string, but do test the quote character that takes us from
	out-of-quotes to in-quotes. If a legal or terminating character is found,
	return it; otherwise return False.  Also return the line and character numbers
	at which the legal or terminating character is found.
	"""

	inSingleQuotes = False
	inDoubleQuotes = False
	while line < len(lines):
		while char < len(lines[line]):
			c = lines[line][char:char+1]
			if (not inSingleQuotes) and (not inDoubleQuotes):
				if c in terminatorChars:
					#print "findUnquotedLegalOrTerminator: found '%s' at line %d, char %d" % (c, line+1, char)
					return (c, line, char)
				if (isLegal(c)):
					return (c, line, char)
			if (not inDoubleQuotes) and (c == "'"): inSingleQuotes = not inSingleQuotes
			if (not inSingleQuotes) and (c == '"'): inDoubleQuotes = not inDoubleQuotes
			char = char + 1
		line = nextLine(lines, line)
		char = 0
	#print "letter not found."
	return (False, line, char)


def findLegalOrTerminator(lines, line, char, isLegal, terminatorChars):
	""" Find the first legal character or terminator in a list of strings.
	
	Search through a list of strings (lines[]), starting at lines[line][char], for
	a legal character (isLegal(c) == True), or a terminator (c in
	terminatorChars). If a legal or terminating character is found, return it;
	otherwise return False.  Also return the line and character numbers at which
	the legal or terminating character is found.
	"""

	while line < len(lines):
		while char < len(lines[line]):
			c = lines[line][char:char+1]
			if c in terminatorChars:
				#print "findLegalOrTerminator: found '%s' at line %d, char %d" % (c, line+1, char)
				return (c, line, char)
			if (isLegal(c)):
				return (c, line, char)
			char = char + 1
		line = nextLine(lines, line)
		char = 0
	#print "letter not found."
	return (False, line, char)


def findUnquotedTargetChar(lines, line, char, targetCharList):
	""" Find the first unquoted target character in a list fo strings.
	
	Search through a list of strings (lines[]), starting at lines[line][char], for
	a character that is a member of targetCharList (c in targetCharList). 
	targetCharList is expected to be a list of one-element strings.  If
	targetCharList is not a list, make it the only element of a list.  Do not test
	characters within quotes, or the quote character that ends a quoted string,
	but do test the quote character that takes us from out-of-quotes to in-quotes.
	If a target character is found, return it; otherwise return False.  Also
	return the line and character numbers at which the legal or terminating
	character is found.
	"""

	if type(targetCharList) != type([]): targetCharList = [targetCharList]
	inSingleQuotes = False
	inDoubleQuotes = False
	while line < len(lines):
		while char < len(lines[line]):
			c = lines[line][char:char+1]
			if (not inDoubleQuotes) and (c == "'"): inSingleQuotes = not inSingleQuotes
			if (not inSingleQuotes) and (c == '"'): inDoubleQuotes = not inDoubleQuotes
			if (not inSingleQuotes) and (not inDoubleQuotes):
				if c in targetCharList:
					#print "findUnquotedTargetChar: found '%s' at line %d, char %d" % (c, line+1, char)
					return (c, line, char)
			char = char + 1
		line = nextLine(lines, line)
		char = 0
	#print "target(s) '%s' not found." % (targetCharList)
	return (False, line, char)


def findTargetChar(lines, line, char, targetCharList):
	""" Find the first target character in a list of strings.
	
	Search through a list of strings (lines[]), starting at lines[line][char], for
	a character that is a member of targetCharList (c in targetCharList). 
	targetCharList is expected to be a list of one-element strings.  If
	targetCharList is not a list, make it the only element of a list.  If a target
	character is found, return it; otherwise return False.  Also return the line
	and character numbers at which the legal or terminating character is found.
	"""

	if type(targetCharList) != type([]): targetCharList = [targetCharList]
	while line < len(lines):
		while char < len(lines[line]):
			c = lines[line][char:char+1]
			if c in targetCharList:
				#print "findTargetChar: found '%s' at line %d, char %d" % (c, line+1, char)
				return (c, line, char)
			char = char + 1
		line = nextLine(lines, line)
		char = 0
	#print "target(s) '%s' not found." % (targetCharList)
	return (False, line, char)



def findTarget(lines, line, char, targetList):
	""" Find the first target string in a list of strings.
	
	Search through a list of strings (lines[]), starting at lines[line][char], for
	a string that is a member of targetList (str in targetList).  targetList is
	expected to be a list of strings.  If targetList is not a list, make it the
	only element of a list.  If a target string is found, return it; otherwise
	return False.  Also return the line and character numbers at which the string
	is found, and the number of the first character not yet parsed.
	"""

	if type(targetList) != type([]): targetList = [targetList]
	if type(lines) != type([]): lines = [lines]
	if (char >= len(lines[line])):
		line = nextLine(lines, line)
		char = 0
	while line < len(lines):
		for target in targetList:
			index = lines[line].find(target, char)
			if (index != -1):
				next = index + len(target)
				#print "findTarget: found '%s' at line %d, char %d, next char at %d" % (target, line+1, index, next)
				return (target, line, index, next)
		line = nextLine(lines, line)
		char = 0
	#print "target(s) '%s' not found." % (targetList)
	return (False, line, char, char)


def maybeAddQuotes(value):
	""" Return the supplied string enclosed in quotes, if they are needed.
	
	If the string 'value' needs to be quoted, because it contains whitespace, or a
	macro, or because it is empty, then return the string in double quotes.
	"""

	if ((len(value.split()) > 1) or (value.find('$(') != -1) or (value == "")):
		value = '"' + value + '"'
	return value


def isdbLoadRecordsCall(line, verbose):
	""" See if a string is a dbLoadRecords command."""

	if (line.find('dbLoadRecords(') == -1): return (0,0,0)
	# e.g., dbLoadRecords("stdApp/Db/IDctrl.db","P=4id:,xx=04", std)
	words = line.split('(',1)
	words = words[1].rstrip(')').split(',',1)
	words[0] = words[0].strip('"')
	if (len(words) >= 2):
		(path, dbFile) = os.path.split(words[0])
		if words[1].strip()[0] != '"':
			print "isdbLoadRecordsCall: can't parse macros in '%s'" % line
			return (path, dbFile, "")
		macroString = words[1].split('"')[1]
		return (path, dbFile, macroString)
	return (0,0,0)

def isdbLoadTemplateCall(line, verbose):
	""" See if a string is a dbLoadTemplate command."""

	if (line.find('dbLoadTemplate(') == -1): return (0)
	# e.g., dbLoadTemplate("myTemplate.substitutions")
	words = line.split('"',2)
	if (len(words) > 2):
		# e.g., 'dbLoadTemplate(', 'myTemplate.substitutions', ')'
		return (words[1])
	return(0)

# Not recognized, because no parentheses:
# 'epicsEnvSet EPICS_CA_MAX_ARRAY_BYTES 64008'
# 'iocInit'

def isFunctionCall(line, verbose):
	""" See if a string is a function call."""

	(openParen, netParen, closeIndex) = countUnquotedBrackets(line, '(', ')', max(verbose-1,0))
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
	""" See if a string is a legal variable name."""

	# get string with legal characters converted to something alphanumeric
	s = ss.translate(transtable)
	if s[0].isdigit(): return (False)
	if (verbose): print "isLegalName('%s') = %s" % (ss, s.isalnum())
	return s.isalnum()

# Not recognized, because no parentheses:
# 'var motorUtil_debug,1'

def isVariableDefinition(s, verbose):
	""" See if a string is a variable definition."""

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
	""" See if a string is a sequence-program invocation."""

	s = s.lstrip('#\t ')
	if (len(s) == 0): return (0,0)
	s = s.split(None,1)
	if (s[0] != 'seq'): return (0,0)
	split = s[1].split(',', 1)
	if (len(split) == 1): return (0,0)
	return split

def isScriptCommand(s, verbose):
	""" See if a string is a script command."""

	s = s.lstrip('#\t ')
	if (len(s) < 2): return (0)
	if (s[0] != '<'): return (0)
	return s[1:].lstrip()

def isDecoration(s):
	""" See if a string is a comment without useful content."""

	for c in s:
		if curses.ascii.ispunct(c): continue
		if curses.ascii.isspace(c): continue
		if curses.ascii.iscntrl(c): continue
		return(0)
	return(1)

def getEnv(envDict, word):
	""" Return the value of a variable defined in envDict."""

	if not word in envDict.keys(): return None
	return envDict[word][0].value
	
def getVar(varDict, word):
	""" Return the value of a variable defined in varDict."""

	if not word in varDict.keys(): return None
	return varDict[word][0].value

def writeHead(file, s):
	file.write("\n############################################################################\n")
	file.write(s + "\n")
	file.write("############################################################################\n")

def writeUnusedEntries(dictionary, outFile):
	""" Write all entries in a dictionary that are not marked 'used'."""

	if (len(dictionary.keys()) == 0): return
	for key in dictionary.keys():
		for entry in dictionary[key]:
			if not entry.used:
				outFile.write(entry.origLine)

