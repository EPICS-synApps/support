#!/usr/bin/env python

"""
This software is intended to help convert an ioc directory from one version of
synApps to another.  It parses .substitutions files, collects their content in
a dictionary, and writes that content in the correct format to new files.

In the anticipated use, parseSubFiles() will read all the .substitutions files
in the old directory, and collect the information into a dictionary.  Then
writeNewSubFiles() will read all the .substitutions files in the new directory,
and create copies of them (<name>.substitutions.CVT) that contain information
from the dictionary.  If no information in the dictionary seems suitable as
a replacement for what's found in the .substitutions file, the information in
the .substitutions file will be used, but it will be commented out with "#NEW:".
When all new files have been written, any unused information in the dictionary
will be written to a log file.
"""

import curses.ascii
from conversionUtils import *
import sys
import os


class subFileDictEntry:
	"""
	Each substitutions file will be represented by a subFileDictEntry, which
	consists mainly of the dictionary templateFileDict.  Each "word" in
	templateFileDict is the (base) name of a template file; the corresponding
	"definition" is a list of templateFileDictEntry's.  Each
	templateFileDictEntry contains all of the macro names and values associated
	with a single instance of that template file.  (Note that a template file
	may be mentioned more than once in a substitutions file, though it's not
	very common.)
	"""

	def __init__(self):
		self.leadingComment = ""
		self.trailingComment = ""
		self.used = False
		self.templateFileDict = {}	# word is a database name
									# definition is a list of templateFileDictEntry's

class templateFileDictEntry:
	"""Store the content of a single 'file' command in a .substitutions file."""

	def __init__(self):
		self.leadingComment = ""
		self.trailingComment = ""
		self.used = False
		self.usePattern = False
		self.pattern = None
		self.macroDictList = None
		self.valueListList = None


def parseMacroValue(lines, line, next):
	"""
	Expect something like "name1=val1, name2=val2, ... nameN=valN}".  Names are
	expected to begin with a letter, and not to be quoted, but values may look
	like "m$(N)", or "blah blah".  Parse a single name=value pair and return
	them.  After the first set of name=value pairs, it will be our job to
	recognize the "{" that introduces the next set of pairs.  Also, it's our job
	to recognize the "}" that ends a set of pairs, and the "}" that ends the
	list of sets.  Return one of the following:
	   "Fatal"  parsing problem
	   "Found"  a macro=value pair was found
	   "NextDb" no macro=value pair was found; found another list
	   "End"	the end of lists was found
	Also return the macro and value found, and the line and number of the first
	character not yet parsed.
	"""

	#print "parseMacroValue: line = '%s'" % (lines[line][next:])
	(found, line, char) = findLegalOrTerminator(lines, line, next, curses.ascii.isalpha, "}{")
	if (not found): return ("Fatal", line, char, 0, 0)
	if (found == "{"):
		#print "found '{' instead of macro"
		return ("NextDb", line, char+1, 0, 0)
	if (found == "}"):
		#print "found '}' instead of macro"
		return ("End", line, char+1, 0, 0)
	macroLine = line
	macroStartIx = char
	(found, line, char, next) = findTarget(lines, line, char, ["=","}"])
	if (found != "="): return ("Fatal", line, char, 0, 0)
	if line == macroLine:
		macro = lines[macroLine][macroStartIx:next-1]
	else:
		macro = lines[macroLine][macroStartIx:]
	macro = macro.strip().strip('"')
	valueLine = line
	valueStartIx = next
	(found, line, char, next) = findTarget(lines, line, next, [",", "}"])
	if not found: return ("Fatal", line, char, 0, 0)
	if line == valueLine:
		value = lines[valueLine][valueStartIx:next-1]
	else:
		value = lines[valueLine][valueStartIx:]
	value = value.strip().strip('"')
	#print "parseMacroValue: '%s=%s'" % (macro, value)
	return ("Found", line, next, macro, value)


def parseMacroValueLists(lines, line, next):
	"""
	Expect something like "name1=val1, name2=val2, ... nameN=valN}".  Names are
	expected to begin with a letter, and not to be quoted, but values may look
	like "m$(N)", or "blah blah".  Return a list of dictionaries, a list of
	macro names, and the line and number of the first character not yet parsed.
	"""

	#print "parseMacroValueLists: line = '%s'" % (lines[line][next:])
	dbNum = 0
	dictList = []
	dictList.append({})
	pattern = []
	(status, line, next, macro, value) = parseMacroValue(lines, line, next)
	while ((status != "Fatal") and (status != "End")):
		if status == "Found":
			dictList[dbNum][macro] = value
			if (dbNum == 0): pattern.append(macro)
			(status, line, next, macro, value) = parseMacroValue(lines, line, next)
		else: #NextDb
			#print "parseMacroValueLists: currDict = ", dictList[dbNum]
			#print "----parseMacroValueLists: next db"
			dbNum = dbNum + 1
			dictList.append({})
			(status, line, next, macro, value) = parseMacroValue(lines, line, next)
	return (dictList, pattern, line, next)

def notWhiteOrComma(c):
	if c==",": return False
	return curses.ascii.isgraph(c)

def parseValue(lines, line, next, verbose=0):
	"""
	Expect something like "val1, val2, ... valN}", where "valN" might look like
	"m$(N)", or "blah blah".  Parse a single value and return it.  After the
	first set of values, it will be our job to recognize the "{" that introduces
	the next set of values.  Also, it's our job to recognize the "}" that ends a
	set of values, and the "}" that ends the list of sets.  Return one of the
	following:
	   "Fatal"    if no value is found
	   "NextDb"   if no value is found, but the next list is found
	   "Found"    if a value is found
	   "FoundEnd" if a value is found, and the terminating character also
				  terminates the value list
	   "End"	  if the end of the value list is found
	Also return the value found, and the line and number of the first character
	not yet parsed.
	"""

	trailer = ""
	if (verbose): print "parseValue: line %d = '%s'" % (line+1, lines[line][next:])
	# isgraph: any printable character except whitespace OR COMMA
	(found, line, char) = findUnquotedLegalOrTerminator(lines, line, next, notWhiteOrComma, "}{")
	if (not found):
		print "parseValue: Fatal: didn't find either of }{ (FATAL)"
		return ("Fatal", line, char, None, trailer)
	if (found == "{"):
		if (verbose): print "found '{' instead of value (NEXTDB)"
		return ("NextDb", line, char+1, None, trailer)
	if (found == "}"):
		if (verbose): print "parseValue: found '}' (END) at line %d", line+1
		if (char < len(lines[line])): trailer = lines[line][char+1:].strip()
		return ("End", line, char+1, None, trailer)
	# Now we know we have a value to parse
	#print "parseValue: found value at line %d = '%s'" % (line+1, lines[line][char:])
	retVal = "Found"
	valueLine = line
	valueChar = char
	# find value terminator
	(found, line, char) = findUnquotedTargetChar(lines, line, char, ["}", ",", " ", "\t", "\n"])
	next = char + 1
	if found == "}":
		# this terminates value string and also database section
		retVal = "FoundEnd"
		if (char < len(lines[line])): trailer = lines[line][char+1:].strip()
	if not found: return ("Fatal", line, next, None, trailer)
	if (verbose): print "parseValue: value at '%s', terminated by '%s'" % (lines[valueLine][valueChar:], found)
	if (line == valueLine):
		if (verbose): print "parseValue: valueChar=%d, char=%d" % (valueChar, char)
		value = lines[valueLine][valueChar:char]
	else:
		value = lines[valueLine][valueChar:]
	return (retVal, line, next, value, trailer)


def parseValueLists(lines, line, next, verbose):
	"""
	Expect something like "{val1, val2, ... valN}", where "valN" might look like
	"m$(N)", or "blah blah".  We should find as many values as parseMacro()
	found macro names, but this routine doesn't check that.  Return a list of
	value lists, or None if something went wrong.  Also return the line and
	number of the first character not yet parsed.
	"""

	if (verbose): print "parseValueLists: line = '%s'" % (lines[line][next:])
	dbNum = 0
	valueListList = [[]]
	(found, line, char, next) = findTarget(lines, line, next, ["{"])
	if (verbose): print "parseValueLists: findTarget(...'{') returned ", (found, line, char, next)
	if not found:
		print "parseValueLists: Expected '{', but didn't find it."
		return (None, line, next)
	inDbLine = True
	(status, line, next, value, trailer) = parseValue(lines, line, next, max(0,verbose-1))
	if (verbose): print "parseValueLists: parseValue() returned ", (status, line, next, value)
	while ((status != "Fatal") and (status != "Done") and (line < len(lines))):
		if ((status == "Found") or (status == "FoundEnd")):
			if (verbose): print "parseValueLists: found value '%s'" % (value)
			valueListList[dbNum].append(value.strip().strip('"'))
			(status, line, next, value, trailer) = parseValue(lines, line, next, max(0,verbose-1))
			if (verbose): print "parseValueLists: parseValue() returned ", (status, line, next, value)
			if (status == "FoundEnd"): 	inDbLine = False
		elif (status == "NextDb"):
			if (verbose): print "parseValueLists: found list = %s" % valueListList[dbNum]
			valueListList.append([])
			dbNum = dbNum + 1
			inDbLine = True
			(status, line, next, value, trailer) = parseValue(lines, line, next, max(0,verbose-1))	
			if (verbose): print "parseValueLists: parseValue() returned ", (status, line, next, value)
		else: # (status == "End"):
			# found "}" which did not terminate a value, might be end of template file
			# see if there are more databases for this template file
			if (not inDbLine): break
			(found, line, char, next) = findTarget(lines, line, next, ["{", "}"])
			if (found == "{"):
				valueListList.append([])
				dbNum = dbNum + 1
				if (verbose): print "parseValueLists: dbNum = ", dbNum
				inDbLine = True
				(status, line, next, value, trailer) = parseValue(lines, line, next, max(0,verbose-1))
			else:
				break
	if (verbose): print "parseValueLists: found list = %s" % valueListList[dbNum]
	return (valueListList, line, next)


def parseMacro(lines, line, next):
	"""
	Expect something like "{name1, name2, ... nameN}".  Names are expected to
	begin with a letter, and not to be quoted.  If we see '}', we can assume it
	terminates the pattern, and needn't worry about whether it occurs within
	quotes.  Return one of the following:
	   "Fatal"    if no macro is found
	   "Found"    if a macro is found
	   "FoundEnd" if a macro is found, and the terminating character also
				  terminates the macro list
	   "End"	  if the end of the macro list was found
	Also return the macro found, and the line and number of the first character
	not yet parsed.
	"""

	#print "parseMacro: line = '%s'" % (lines[line][next:])
	(found, line, char) = findLegalOrTerminator(lines, line, next, curses.ascii.isalpha, "}")
	if (not found): return ("Fatal", line, char, None)
	if (found == "}"):
		#print "parseMacro: found '}'"
		next = char + 1
		if (next >= len(lines[line])):
			line = line + 1
			skipCommentLines(lines, line)
			next = 0
		return ("End", line, next, None)
	macroLine = line
	macroChar = char
	# find macro-name terminator
	(found, line, char) = findTargetChar(lines, line, char+1, ["}", ",", " ", "\t", "\n"])
	if not found: return ("Fatal", line, next, None)
	retVal = "Found"
	next = char + 1
	if (found == "}"): retVal = "FoundEnd"
	#print "parseMacro: macro at beginning of '%s'" % (lines[macroLine][macroChar:])
	if (line == macroLine):
		#print "parseMacro: macroChar=%d, char=%d" % (macroChar, char)
		macro = lines[macroLine][macroChar:char]
	else:
		macro = lines[macroLine][macroChar:]
	return (retVal, line, next, macro)


def parseMacroList(lines, line, next):
	"""
	Expect something like "{name1, name2, ... nameN}".  Names are expected to
	begin with a letter, and not to be quoted.  If we see '}', we can assume it
	terminates the pattern, and needn't worry about whether it occurs within
	quotes.  Return the macro list, if found, or None.  Also return the line and
	number of the first character not yet parsed.
	"""

	#print "parseMacroList: line = '%s'" % (lines[line][next:])
	macroList = []
	(found, line, char, next) = findTarget(lines, line, next, ["{"])
	if not found: return (None, line, next)
	(status, line, next, macro) = parseMacro(lines, line, next)
	while (status == "Found"):
		#print "parseMacroList: found macro '%s'" % (macro)
		macroList.append(macro)
		(status, line, next, macro) = parseMacro(lines, line, next)
	if (status == "FoundEnd"): macroList.append(macro)
	return (macroList, line, next)


def find_file_command(lines, line, next):
	"""
	Look for a command of the form
		'file templateFileName <blah blah>'
	Note that the command may be commented out; we're still interested in it,
	but this complicates the business of parsing, and we might be fooled by a
	comment that just happens to comtain the word "file".  Minimize this by
	accepting only a line that contains "#___file", where underscore may be any
	number of non-alphabetic characters.
	"""

	while (line < len(lines)):
		leadingComment = ""
		(found, line, char, next) = findTarget(lines, line, next, "file")
		if (not found):
			#print "'file' keyword not found.  Done."
			break

		# examine line containing the word "file"
		fileNameLine = line
		fileNameStartIx = next
		if (char > 0):
			preamble = lines[fileNameLine][:char]
			if (preamble.find("#") != -1):
				leadingComment = preamble
				# Make sure this is a file command, not just a comment containing "file"
				for c in preamble:
					if c.isalpha():
						# This is not really a file command
						found = False
						break
		if (not found):
			# False alarm.  Keep looking.
			line = line + 1
			continue

		return (found, line, char, next, leadingComment)
	return (False, line, char, next, leadingComment)



def parseSubFile(fileName, verbose, ignoreComments=False):
	"""
	Parse a substitutions file.  Return a list of dictionary entries, one entry
	per template file, with the file content.  We probably should be collecting
	comments also, but we're not.  However, we are collecting information from
	commented out template-file commands (substitution blocks).
	"""

	file = open(fileName)
	lines = file.readlines()
	line = 0
	next = 0
	subFileEntry = subFileDictEntry()
	while (line < len(lines)):
		(found, line, char, next, leadingComment) = find_file_command(lines, line, next)
		if ((leadingComment != "") and ignoreComments):
			line += 1
			continue
		if (not found):
			if (verbose): print "'file' keyword not found.  Done."
			break
		fileNameLine = line
		fileNameString = lines[line]
		fileNameStartIx = next

		(found, line, char, next) = findTarget(lines, line, next, "{")
		if (not found):
			print "No {} section found for 'file' command: '%s'" % (lines[fileNameLine])
			break
		if (line == fileNameLine):
			fileNameEndIx = next - 1
			templateFile = fileNameString[fileNameStartIx:fileNameEndIx]
		else:
			templateFile = fileNameString[fileNameStartIx:]
		templateFile = templateFile.strip().strip('"')
		if (verbose): print "templateFile = '%s'" % templateFile
		entry = templateFileDictEntry()
		entry.leadingComment = leadingComment

		(found, line, char, next) = findTarget(lines, line, next, ["pattern", "{"])
		if (not found):
			print "No content found for template file '%s'" & (templateFile)
			break
		if (found == "{"):
			# look for {A=a1,B=b1}{A=a2,B=b2}...}
			if (verbose): print "parseSubFile: calling parseMacroValueLists for template '%s'" % (templateFile)
			(macroDictList, pattern, line, next) = parseMacroValueLists(lines, line, next)
			if (verbose): print "parseSubFile: found macro-value list:", macroDictList
			entry.macroDictList = macroDictList
			entry.pattern = pattern
		else:
			entry.usePattern = True
			# look for {A,B}{a1.b1}{a2,b2}...}
			if (verbose): print "parseSubFile: calling parseMacroList for template '%s'" % (templateFile)
			(entry.pattern, line, next) = parseMacroList(lines, line, next)
			if (verbose): print "parseSubFile: found pattern:", entry.pattern
			(valueListList, line, next) = parseValueLists(lines, line, next, max(0,verbose-1))
			if (verbose): print "parseSubFile: found value lists:", valueListList
			entry.valueListList = valueListList
			# create macroDictList from pattern and valueListList
			entry.macroDictList = []
			for valueList in entry.valueListList:
				macroDict = {}
				for i in range(len(entry.pattern)):
					macroDict[entry.pattern[i]] = valueList[i]
				entry.macroDictList.append(macroDict)
				

		baseTemplateName = os.path.basename(templateFile)
		if templateFile not in subFileEntry.templateFileDict.keys():
			subFileEntry.templateFileDict[baseTemplateName] = []
		subFileEntry.templateFileDict[baseTemplateName].append(entry)

	return subFileEntry


def parseSubFiles(subFileDict, filespec, verbose, ignoreComments=False):
	"""
	For each file in the file specification (which might be something like
	'*.substitutions') call parseSubFile() to collect the file's information
	into a list of dictionary entries.
	"""

	subFiles = glob.glob(filespec)
	for fileName in subFiles:
		fn = os.path.basename(fileName)
		subFileDict[fn] = parseSubFile(fileName, max(verbose,0), ignoreComments=ignoreComments)

	return (subFileDict)


def writeNewSubFile(subFileDict, fileName, maxLineLength=120):
	"""
	Read the substitutions file, fileName, and write a new copy of it, using
	information from the dictionary entry for that file name.  For each template
	file (substitutions block) in "fileName", look for an unused
	templateFileDict entry in the list,
	subFileDict[fileName].templateFileDict[template-file]. If no entry is found,
	copy from fileName to the new file, but comment the lines out with "#NEW:",
	and let some EPICS developer decide what to do with it. If an unused entry
	is found, use the dictionary information instead of what's in fileName. 
	Mark the dictionary entries we use, so they won't get written twice.
	"""

	#print "writeNewSubFile: ", fileName
	if not (os.path.basename(fileName) in subFileDict.keys()):
		return subFileDict
	thisSubFileDict = subFileDict[os.path.basename(fileName)]
	file = open(fileName)
	lines = file.readlines()
	line = 0
	next = 0
	newFile = open(fileName+".CVT", "w+")
	newFile.write("#NEW: <command> -- marks a command in %s that was not found in old_dir.\n" % os.path.basename(fileName))

	while (line < len(lines)):
		(found, line, char, next, leadingComment) = find_file_command(lines, line, next)
		if (not found):
			#print "'file' keyword not found.  Done."
			break

		fileNameLine = line
		fileNameStartIx = next

		(found, line, char, next) = findTarget(lines, line, next, "{")
		if (not found):
			print "No {} section found for 'file' command: '%s'" % (lines[fileNameLine])
			break
		if (line == fileNameLine):
			fileNameEndIx = next - 1
			templateFile = lines[fileNameLine][fileNameStartIx:fileNameEndIx]
		else:
			templateFile = lines[fileNameLine][fileNameStartIx:]
		templateFile = templateFile.strip().strip('"')

		found = False
		baseTemplateFile = os.path.basename(templateFile)
		if (baseTemplateFile in thisSubFileDict.templateFileDict.keys()):
			for entry in thisSubFileDict.templateFileDict[baseTemplateFile]:
				if (not entry.used):
					found = True
					entry.used = True
					writeSubstitutions(templateFile, entry, newFile, maxLineLength)
					break

		# skip to end of substitutions section.  If the template file was not found,
		# parrot the whole substitution, commented with #NEW:
		fLine = fileNameLine
		while (fLine < line):
			if not found: newFile.write("#NEW: " + lines[fLine])
			fLine = fLine + 1
		(o, netBrackets, c) = countUnquotedBrackets(lines[line], "{", "}", 0)
		if not found: newFile.write("#NEW: %s" % (lines[line]))
		line = line + 1
		while ((netBrackets > 0) and (line < len(lines))):
			(o, net, c) = countUnquotedBrackets(lines[line], "{", "}", 0)
			if not found: newFile.write("#NEW: %s" % (lines[line]))
			netBrackets = netBrackets + net
			line = line + 1

	return subFileDict


def writeNewSubFiles(subFileDict, filespec):
	"""
	For each substitutions file in the file specification, filespec, call
	writeNewSubFile() to write a new copy of the file.  writeNewSubFile() is
	expected to update the dictionary by marking all the entries it writes as
	'used'.
	"""

	subFiles = glob.glob(filespec)
	for fileName in subFiles:
		subFileDict = writeNewSubFile(subFileDict, fileName, 120)
	return (subFileDict)


def writeSubstitutions(templateFileName, dictEntry, outFile, maxLineLength):
	"""
	Write, to outFile, the substitutions block for a given template file from a
	given template dictionary entry.  Format the lines so they don't exceed
	maxLineLength characters.  Also format the output macro names and values in
	columns.
	"""

	s = '%sfile "%s"\n{\n' % (dictEntry.leadingComment, templateFileName)
	outFile.write(s)
	pattern = dictEntry.pattern
	if dictEntry.usePattern:
		# determine word sizes
		sizes = []
		for macro in pattern: sizes.append(len(macro))
		list = dictEntry.valueListList
		for db in range(len(list)):
			for j in range(len(list[db])):
				value = maybeAddQuotes(list[db][j])
				size = len(value)
				if size > sizes[j]: sizes[j] = size
		# make format strings
		format = []
		format.append("{%%-%ds" % sizes[0])
		for j in range(1, len(pattern)):
			format.append(", %%-%ds" % sizes[j])

		# write
		s = "pattern\n"
		for j in range(len(pattern)):
			s = s + format[j] % (pattern[j])
		s = s + "}\n"
		outFile.write(s)
		for db in range(len(list)):
			s = ""
			for j in range(len(list[db])):
				value = maybeAddQuotes(list[db][j])
				s = s + format[j] % value
			s = s + "}\n"
			outFile.write(s)
	else:
		macroDictList = dictEntry.macroDictList

		# determine word sizes
		macroSizes = []
		valueSizes = []
		for p in pattern:
			macroSizes.append(0)
			valueSizes.append(0)
		for db in macroDictList:
			for j in range(len(pattern)):
				macro = pattern[j]
				size = len(macro)
				if size > macroSizes[j]: macroSizes[j] = size
				size = len(maybeAddQuotes(db[macro]))
				if size > valueSizes[j]: valueSizes[j] = size

		# make format strings
		format = []
		for j in range(len(pattern)):
			format.append("%%-%ds=%%-%ds" % (macroSizes[j], valueSizes[j]))

		# write
		for db in macroDictList:
			for j in range(len(pattern)):
				macro = pattern[j]
				value = maybeAddQuotes(db[macro])
				if (j == 0):
					s = "{" + (format[j] % (macro, db[macro]))
				elif ((len(s) + macroSizes[j] + valueSizes[j] + 3) > maxLineLength):
					outFile.write(s + ",\n ")
					s = format[j] % (macro, value)
				else:
					s = s + ", " + (format[j] % (macro, value))
			s = s + "}\n"
			outFile.write(s)
	outFile.write("}\n")



def writeSubFileDictionaries(subFileDict, outFile, maxLineLength):
	"""Write the content of all the substitution files we've parsed."""

	writeHead(outFile, "substitution files")
	for subFile in subFileDict.keys():
		wrotePreamble = False

		for templateFile in subFileDict[subFile].templateFileDict.keys():
			for entry in subFileDict[subFile].templateFileDict[templateFile]:
				if not wrotePreamble:
					outFile.write("\n----------------------------------------------------------------------------\n")
					s = '# "%s"\n' % os.path.basename(subFile)
					outFile.write(s)
					wrotePreamble = True
				writeSubstitutions(templateFile, entry, outFile, maxLineLength)


def writeUnusedSubFileEntries(subFileDict, outFile, maxLineLength):
	"""Write the unused information collected from substitutions files"""

	writeHead(outFile, "unused substitution files")

	for subFile in subFileDict.keys():
		wrotePreamble = False

		for templateFile in subFileDict[subFile].templateFileDict.keys():
			for entry in subFileDict[subFile].templateFileDict[templateFile]:
				if (not entry.used):
					if not wrotePreamble:
						outFile.write("\n----------------------------------------------------------------------------\n")
						s = '# "%s"\n' % os.path.basename(subFile)
						outFile.write(s)
						wrotePreamble = True
					writeSubstitutions(templateFile, entry, outFile, maxLineLength)


# Mostly for testing.

usage = "usage info not yet written"

def main():
	verbose = 4
	fileArg = 1
	ignoreComments = 0
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
		fileArg = i
		if (len(sys.argv) > fileArg):
			oldFileName = sys.argv[fileArg]
			if not os.path.isfile(oldFileName):
				print "\n'" + oldFileName + "' is not a file"
				return
			subFileDict = {}
			subFileDict[os.path.basename(oldFileName)] = parseSubFile(oldFileName, verbose)

			fileArg = fileArg + 1

		wrote_new_files = 0
		if (len(sys.argv) > fileArg):
			newFileName = sys.argv[fileArg]
			if not os.path.isfile(newFileName):
				print "\n'" + newFileName + "' is not a file"
				return
			writeNewSubFile(subFileDict, oldFileName, 80)


		reportFile = open("convertSubFiles.out", "w+")
		if (wrote_new_files):
			writeUnusedSubFileEntries(subFileDict, reportFile)
		else:
			writeSubFileDictionaries(subFileDict, reportFile)
		reportFile.close()

if __name__ == "__main__":
	main()
