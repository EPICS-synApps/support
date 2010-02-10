#!/usr/bin/env python
"""
dbd.py - a collection of routines for reading the .dbd file loaded into an ioc,
extracting some of the information into a python object, and using that
information to do a couple of tricks.  I've not been very careful about
handling legal variations in the .dbd syntax.   Probably the most useful
routine here is writeNewDatabase().
"""
import sys

HAVE_CA = True
try:
	from ca_util import *
except:
	HAVE_CA = False


# menuDict is a dictionary whose keys are menu types, and whose entries are lists
# of menu choices.  For example, the following dbd-file fragment:
#
#	menu(vmeRDWT) {
#		choice(vmeRDWT_Read,"Read")
#		choice(vmeRDWT_Write,"Write")
#	}
#
# yields:
#	menuDict['vmeRDWT'] = ["Read", "Write"]

# fieldAttributeDict is a dictionary whose keys are field-attribute names, and whose
# entries are field-attribute values.  For example, the following dbd-file
# fragment:
#
#		prompt("Record Name")
#
# yields
#	fieldAttributeDict['prompt'] = "Record Name"

# fieldDict is a dictionary whose keys are field names, and whose entries are
# fieldAttributeDict dictionaries:
# For example, the following dbd-file fragment:
#
#	field(NAME,DBF_STRING) {
#		prompt("Record Name")
#		special(SPC_NOMOD)
#		size(61)
#	}
#
# yields:
#	fieldDict['NAME'] = {'prompt':'Record Name', 'special':'SPC_NOMOD', 'size':61}

class recordtypeClass:
	def __init__(self):
		self.fieldDict = {}	# e.g., {'prompt':'Record Name', 'special':'SPC_NOMOD', 'size':61, ...}
		self.fieldList = []	# e.g., ['NAME', 'EGU', ...]
		self.fieldType = {}	# e.g., {'NAME':'DBF_STRING', 'DESC':'DBF_STRING', ...}

# recordtypeDict is a dictionary whose keys are record-type names, and whose entries
# are instances of class recordtypeClass.  For example, the following dbd-file fragment:
#
#	recordtype(ai) {
#		field(NAME,DBF_STRING) {
#			prompt("Record Name")
#			special(SPC_NOMOD)
#			size(61)
#		}
#		field(DESC,DBF_STRING) {
#			prompt("Descriptor")
#			promptgroup(GUI_COMMON)
#			size(29)
#		}
#	}
#
# yields:
#	recordtypeDict['ai'] = {
#		<recordtypeClass instance>
#	}
#
# where <recordtypeClass instance> is :
#		fieldDict = {'NAME':{'prompt':'Record Name', 'special':'SPC_NOMOD', 'size':61},
#					'DESC':{'DBF_STRING', 'prompt':"Descriptor", 'promptgroup':'GUI_COMMON', 'size':29}}
#		fieldList = ['NAME', 'DESC']
#		fieldType = {'NAME':DBF_STRING, 'DESC':DBF_STRING}

class recordInstance:
	def __init__(self, recordName, recordType):
		self.recordName = recordName
		self.recordType = recordType
		self.fieldNames = []
		self.fieldValues = []

class dbdClass:
	def __init__(self):
		self.recordtypeDict = {}
		self.recordtypeList = []
		self.menuDict = {}


def readDBD(fileName):
	dbd = dbdClass()
	file = open(fileName, "r")
	inMenu = 0
	inRecordtype = 0
	inField = 0
	for rawLine in file :
		rawLine = rawLine.lstrip()
		#print("readDBD: line='%s'" % rawLine)
		
		if inMenu :
			# collect choices into menuDict
			ix = rawLine.find('choice(')
			if ix != -1 :
				(junk,choice) = rawLine[ix:].split(',',1)
				choice = choice.split(')')[0].lstrip()
				startix = choice.find('"')+1
				endix = choice[startix:].rfind('"')+1
				dbd.menuDict[menuName].append(choice)
			else:
				if rawLine.find('}') != -1:
					inMenu = 0
			continue
		
		if inRecordtype :
			if inField :
				if rawLine.find('}') != -1 :
					inField = 0
				else:
					# add entries to recordtypeDict[recordName].fieldDict[fieldName] (a fieldAttributeDict)
					(name, value) = rawLine.split('(', 1)
					value = value.split(')')[0]
					dbd.recordtypeDict[recordName].fieldDict[fieldName][name] = value
				continue
			elif rawLine[0:6] == 'field(' :
				inField = 1
				(fieldName, fieldType) = rawLine[6:].split(')')[0].split(',', 1)
				dbd.recordtypeDict[recordName].fieldList.append(fieldName)
				dbd.recordtypeDict[recordName].fieldType[fieldName] = fieldType
				dbd.recordtypeDict[recordName].fieldDict[fieldName] = {} # a fieldAttributeDict
				continue
			elif rawLine.find('}') != -1 :
				inRecordtype = 0
					
			
		if rawLine[0:5] == 'menu(' :
			inMenu = 1
			menuName = rawLine[5:].split(')')[0]
			dbd.menuDict[menuName] = []
		elif rawLine[0:11] == 'recordtype(' :
			inRecordtype = 1
			recordName = rawLine[11:].split(')')[0]
			dbd.recordtypeDict[recordName] = recordtypeClass()
			dbd.recordtypeList.append(recordName)
		elif rawLine[0:7] == 'device(' :
			continue
		elif rawLine[0:7] == 'driver(' :
			continue
		elif rawLine[0:10] == 'registrar(' :
			continue
		elif rawLine[0:9] == 'variable(' :
			continue
		else:
			continue
	#print("dbd=", dbd)
	return(dbd)

# Write a .dbd file from information contained in the dbdClass instance, 'dbd'.
def writeDBD(dbd, fileName=None):
	if (fileName):
		file = open(fileName, "w")
	else:
		file = sys.stdout
	for k in dbd.menuDict.keys():
		file.write("menu(%s) {\n" % k)
		for c in dbd.menuDict[k]:
			file.write("\t%s\n" % c)
		file.write("}\n")
	for r in dbd.recordtypeList:
		file.write("recordtype(%s) {\n" % r)
		for f in dbd.recordtypeDict[r].fieldList:
			file.write("\tfield(%s,%s) {\n" % (f, dbd.recordtypeDict[r].fieldType[f]))
			for a in dbd.recordtypeDict[r].fieldDict[f].keys():
				file.write("\t\t%s(%s)\n" % (a, dbd.recordtypeDict[r].fieldDict[f][a]))
			file.write("\t}\n")
		file.write("}\n")

string_field_types = ['DBF_STRING', 'DBF_ENUM', 'DBF_INLINK', 'DBF_OUTLINK', 'DBF_FWDLINK']
numeric_fieldTypes = ['DBF_DOUBLE', 'DBF_FLOAT', 'DBF_LONG', 'DBF_INT', 'DBF_SHORT', 'DBF_CHAR']
nowrite_fields = ['PROC', 'UDF']

def setToSameType(val, example_of_type):
	if type(example_of_type) == type(""):
		return str(val)
	if type(example_of_type) == type(0):
		return int(val)
	if type(example_of_type) == type(0L):
		return long(val)
	if type(example_of_type) == type(0.0):
		return float(val)
	return(val)

# Given a dbdClass object, 'dbd', a record type, a field name, and a value, determine if the value
# is different from the default value for that PV.
def isDefaultValue(value, recordType, fieldName, dbd):
	if 'initial' in dbd.recordtypeDict[recordType].fieldDict[fieldName].keys():
		initial = dbd.recordtypeDict[recordType].fieldDict[fieldName]['initial'][1:-1]
		value = setToSameType(value, initial)
		if value == initial:
			return True
		else:
			#print "isDefaultValue: <%s>.%s value='%s'; initial='%s' NOT default" % (recordType, fieldName, value, initial)
			#print "type(value) = ", type(value), " type(initial) = ", type(initial)
			return False
	if (fieldName == 'FLNK') and (value == '0'):
		return True
	if dbd.recordtypeDict[recordType].fieldType[fieldName] in string_field_types:
		if value == '':
			return True
	if value == 0:
		return True
	return False

# Given an input string, and a dictionary whose keys are target strings and whose entries are
# replacement strings, replace all occurrences, in the input string, of all target strings, with
# the corresponding replacement string.  Thus, doReplace('abcxxdefyy', {'xx':'11', 'yy':'22'})
# would return 'abc11def22'.
def doReplace(string, replaceDict, reverse=False) :
	s = string
	if replaceDict:
		for old in replaceDict.keys():
			if reverse:
				s = s.replace(replaceDict[old], old, 10)
			else:
				s = s.replace(old, replaceDict[old], 10)
	return s

def findMacros(line):
	macros = set()
	words = line.split('$(')
	for word in words[1:]:
		j = word.find(')')
		if j == -1:
			continue
		macros.add(word[:j])
	return macros

def writeDatabase(fileName, recordInstanceList, replaceDict=None):

	if (fileName):
		file = open(fileName, "w")
	else:
		file = sys.stdout

	macros = set()
	lines = []
	for r in recordInstanceList:
		line = 'record(%s,"%s") {\n' % (r.recordType, doReplace(r.recordName, replaceDict))
		newMacros = list(findMacros(line))
		for m in newMacros:
			macros.add(m)
		lines.append(line)
		for (fieldName, value) in zip(r.fieldNames, r.fieldValues):
			if type(value) == type(""):
				value = doReplace(value, replaceDict)
			line = '\tfield(%s,"%s")\n' % (fieldName, value)
			newMacros = list(findMacros(line))
			for m in newMacros:
				macros.add(m)
			lines.append(line)
		lines.append("}\n\n")

	comment = '#dbLoadRecords("%s", "' % fileName
	for m in list(macros):
		comment += "%s=," % m
	comment = comment[:-1] + '")\n'
	file.write(comment)
	file.writelines(lines)
	file.close()

# Write a new .db file from the following information:
#	- the dbdClass instance, made by calling readDBD(dbdFileName)
#	- a list of live EPICS records, specified as a list of PV's (just strip the field name)
#	- an ioc, which can be interrogated via channel access, from which field values are gotten
#	- a list of text replacements, so that, for example, a record named xxx:userCalc1 can appear
#	  in the .db file as '$(P)userCalc1'.
def writeNewDatabase(fileName, pvList, dbdFileName, replaceDict=None, fixUserCalcs=True):
	"""
	Software to support the use of run-time programming to prototype a database.

	usage:
	   dbd.writeNewDatabase(fileName, pvList, dbdFileName, replaceDict=None,
	      fixUserCalcs=True)
	example:
	   dbd.writeNewDatabase('test.db', ['xxx:userStringCalc1.SCAN',
	      'xxx:userCalcOut1.DESC'], 'iocxxxVX.dbd', {'xxx:user':'$(P)$(Q)'})

	Reads all current field values from the records mentioned in 'pvList', and
	writes them to a database named 'fileName'.  Field definitions and default
	field values are read from the .dbd file 'dbdFileName'; only non-default
	values are included in the database.  You can systmatically replace text in
	record names and PV values by supplying a dictionary of text replacements. 
	For example, if the live records have names like 'xxx:userCalc...', you
	can have the database write them as '$(P)$(Q)Calc...'.
	
	If you are using actual userCalcs (userTransforms, etc.) to prototype,
	you'll probably not want the Enable/Disable support built into userCalcs
	to be reproduced in the new database.  By default (fixUserCalcs==True),
	records whose names begin with '*:user' are treated specially: live values
	of the SDIS, DISA, and DISV fields are replaced by default field values.

	"""
	if not HAVE_CA :
		print("Can't import ca_util")
		return

	if (fileName):
		file = open(fileName, "w")
	else:
		file = sys.stdout

	recordList = []
	for pv in pvList:
		recordName = pv.split('.')[0]
		if recordName not in recordList:
			recordList.append(recordName)

	dbd = readDBD(dbdFileName)
	for recordName in recordList:
		recordType = caget(recordName+".RTYP")
		file.write('record(%s,"%s") {\n' % (recordType, doReplace(recordName, replaceDict)))
		for fieldName in dbd.recordtypeDict[recordType].fieldList:
			if dbd.recordtypeDict[recordType].fieldType[fieldName] == 'DBF_NOACCESS':
				continue
			if ('special' in dbd.recordtypeDict[recordType].fieldDict[fieldName].keys()) and (dbd.recordtypeDict[recordType].fieldDict[fieldName]['special'] == 'SPC_NOMOD'):
				continue
			if fieldName in nowrite_fields:
				continue
			if 'prompt' in dbd.recordtypeDict[recordType].fieldDict[fieldName].keys():
				pv = recordName+'.'+fieldName
				#print("trying %s..." % pv)
				value = caget(pv)
				#print("%s='%s'" % (recordName+'.'+fieldName, value))
				if isDefaultValue(value, recordType, fieldName, dbd):
					continue
				if type(value) == type(""):
					value = doReplace(value, replaceDict)
				if fixUserCalcs and recordName.find(':user') and fieldName in ['DISA', 'DISV', 'SDIS']:
					continue
				file.write('\tfield(%s,"%s")\n' % (fieldName, value))
		file.write("}\n\n")


def main():
	#print "sys.arvg:", sys.argv
	if len(sys.argv) < 2:
		print "usage: dbd.py <dbdFile>"
		return
	dbd = readDBD(sys.argv[1])
	writeDBD(dbd, sys.stdout)


if __name__ == "__main__":
	main()
