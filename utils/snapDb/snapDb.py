#!/usr/bin/env python
"""
	snapDb 1.0 - an EPICS rapid application development tool
	Tim Mooney
	January 5, 2009 
"""
import sys
import dbd
import os

import wx
import wx.lib.mixins.listctrl as listmix
#import test_listctrl as listmix

HAVE_CA = True
try:
	from ca_util import *
	import ca
except:
	HAVE_CA = False

databasePath = os.getcwd()
medmPath = os.getcwd()

displayInfo = {
	'aSub':			('anyRecord.adl',		'P', 'R'),
	'acalcout':		('yyArrayCalc.adl',		'P', 'C'),
	'ai':			('anyRecord.adl',		'P', 'R'),
	'ao':			('anyRecord.adl',		'P', 'R'),
	'asyn':			('asynRecord.adl',		'P', 'R'),
	'bi':			('anyRecord.adl',		'P', 'R'),
	'bo':			('anyRecord.adl',		'P', 'R'),
	'busy':			('busyRecord.adl',		'P', 'B'),
	'calc':			('CalcRecord.adl',		'P', 'C'),
	'calcout':		('yyCalcoutRecord.adl',	'P', 'C'),
	'compress':		('anyRecord.adl',		'P', 'R'),
	'dfanout':		('anyRecord.adl',		'P', 'R'),
	'epid':			('pid_control.adl',		'P', 'PID'),
	'event':		('anyRecord.adl',		'P', 'R'),
	'fanout':		('anyRecord.adl',		'P', 'R'),
	'longin':		('anyRecord.adl',		'P', 'R'),
	'longout':		('anyRecord.adl',		'P', 'R'),
	'mbbi':			('anyRecord.adl',		'P', 'R'),
	'mbbiDirect':	('anyRecord.adl',		'P', 'R'),
	'mbbo':			('anyRecord.adl',		'P', 'R'),
	'mbboDirect':	('anyRecord.adl',		'P', 'R'),
	'mca':			('anyRecord.adl',		'P', 'R'),
	'motor':		('motorx.adl',			'P', 'M'),
	'permissive':	('anyRecord.adl',		'P', 'R'),
	'scalcout':		('yysCalcoutRecord.adl',	'P', 'C'),
	'scaler':		('anyRecord.adl',		'P', 'R'),
	'scanparm':		('anyRecord.adl',		'P', 'R'),
	'sel':			('anyRecord.adl',		'P', 'R'),
	'seq':			('yySeq.adl',			'P', 'S'),
	'sscan':		('scanAux.adl',			'P', 'S'),
	'sseq':			('yySseq.adl',			'P', 'S'),
	'state':		('anyRecord.adl',		'P', 'R'),
	'stringin':		('anyRecord.adl',		'P', 'R'),
	'stringout':	('anyRecord.adl',		'P', 'R'),
	'sub':			('anyRecord.adl',		'P', 'R'),
	'subArray':		('anyRecord.adl',		'P', 'R'),
	'swait':		('yyWaitRecord.adl',		'P', 'C'),
	'table':		('anyRecord.adl',		'P', 'R'),
	'timestamp':	('anyRecord.adl',		'P', 'R'),
	'transform':	('yyTransform.adl',		'P', 'T'),
	'vme':			('anyRecord.adl',		'P', 'R'),
	'waveform':		('anyRecord.adl',		'P', 'R')
}

def writePromptGroupFields(dbdFile, outFile=None):
	dbd_object = dbd.readDBD(dbdFile)
	if not dbd_object:
		return
	if (outFile):
		fp = open(outFile, "w")
	else:
		fp = sys.stdout
	for r in dbd_object.recordtypeDict.keys():
		fp.write("recordtype %s\n" % r)
		recordType = dbd_object.recordtypeDict[r]
		for fieldName in recordType.fieldList:
			fieldDict = recordType.fieldDict[fieldName]
			if 'promptgroup' in fieldDict.keys():
				fp.write("\t%s (%s)\n" % (fieldName, fieldDict['prompt']))
	fp.close


def makeReplaceDict(replaceTargets, replaceStrings):
	replaceDict = {}
	for i in range(len(replaceTargets)):
		replaceDict[replaceTargets[i]] = replaceStrings[i]
	return replaceDict

def readDisplayInfoFile(fileName):
	global displayInfo
	if (fileName):
		fp = open(fileName, "r")
	else:
		#print "readDisplayInfoFile: No filename specified; nothing done."
		return displayInfo

	di = displayInfo
	for line in fp.readlines():
		words = line.lstrip().split()
		if (len(words) < 3):
			continue
		if (words[0][0] == '#'):
			continue
		di[words[0]] = tuple(words[1:])	
	return di

# Read an existing database to populate or supplement the lists of record names and types
def openDatabase(fileName, recordNames=[], recordTypes=[], displayStrings=[], replaceDict={}):
	if (fileName):
		file = open(fileName, "r")
	else:
		#print "openDatabase: No filename specified; nothing done."
		return recordNames

	for rawLine in file :
		global displayInfo
		rawLine = rawLine.lstrip()
		rawLine = dbd.doReplace(rawLine, replaceDict, reverse=True)
		split1 = rawLine.split("(")
		#print "openDatabase: split1=%s" % split1
		if len(split1[0]) > 0 and split1[0][0] == '#':
			continue
		if split1[0] == "record":
			rType = rawLine.split('(')[1].split(',')[0]
			rName = rawLine.split('"') [1]
			#print "openDatabase: found record: '%s'" % rName
			if rName not in recordNames:
				recordNames.append(rName)
				recordTypes.append(rType)
				if rType in displayInfo.keys():
					(prefix, name) = rName.split(':', 1)
					prefix = dbd.doReplace(prefix+':', replaceDict)
					name = dbd.doReplace(name, replaceDict)
					dString = displayInfo[rType][0] + ';'
					dString += displayInfo[rType][1] + '=%s,' % prefix
					dString += displayInfo[rType][2] + '=%s' % name
					displayStrings.append(dString)
				else:
					#print "no displayInfo for record type '%s'" % rType
					displayStrings.append("")
	return (recordNames, recordTypes, displayStrings)

nowrite_fields = ['PROC', 'UDF']

# We're using the existence of a "promptgroup()" entry in the record definition to determine
# whether a field can be defined in a database, but really promptgroup only says whether the
# field is *intended* or expected to be defined in a database.  Some records do not have promptgroup
# entries for fields that we want to define in the database:
def kludgePromptGroup(recordType, fieldName):
	if recordType == "scalcout" and fieldName in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
		return True
	if recordType == "sub" and fieldName in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
		return True
	return False		

def defineNewDatabase(pvList, dbd_object, fixUserCalcs=True):
	"""
	Software to support the use of run-time programming to prototype an EPICS database.

	usage:
	   defineNewDatabase(pvList, dbd_object, fixUserCalcs=True)
	example:
	   dbd_object = dbd.readDBD("myDBDFile.dbd")
	   defineNewDatabase(['xxx:myCalc.SCAN','xxx:myTran.DESC'], dbd_object)

	Reads all current field values from the records mentioned in 'pvList', and
	collects values from live record instances.  Field definitions and default
	field values are looked up in the dbdClass object, dbd_object; only non-default
	values are included.
	
	If you are using actual userCalcs (userTransforms, etc.) to prototype,
	you'll probably not want the Enable/Disable support built into userCalcs
	to be reproduced in the new database.  By default (fixUserCalcs==True),
	records whose names begin with '*:user' are treated specially: live values
	of the SDIS, DISA, and DISV fields are replaced by default field values.

	"""
	if not HAVE_CA :
		print("Can't import ca_util")
		return None

	# From pvList, compile a list of unique record instances
	recordNameList = []	# just to avoid duplication
	recordInstanceList = []
	for pv in pvList:
		recordName = pv.split('.')[0]
		if recordName not in recordNameList:
			try:
				recordType = caget(recordName+".RTYP")
			except:
				continue
			recordNameList.append(recordName)
			recordInstanceList.append(dbd.recordInstance(recordName, recordType))
	del recordNameList

	for r in recordInstanceList:
		recordType = dbd_object.recordtypeDict[r.recordType]
		for fieldName in recordType.fieldList:
			if recordType.fieldType[fieldName] == 'DBF_NOACCESS':
				continue
			if fieldName in nowrite_fields:
				continue
			fieldDict = recordType.fieldDict[fieldName]
			if ('special' in fieldDict.keys()): 
				if (fieldDict['special'] in ['SPC_NOMOD', 'SPC_DBADDR']):
					continue
			if 'promptgroup' in fieldDict.keys() or kludgePromptGroup(r.recordType, fieldName):
				pv = r.recordName+'.'+fieldName
				#print("trying %s..." % pv)
				try:
					value = caget(pv)
				except:
					value = 0
				try:
					string_value = caget(pv,req_type=ca.DBR_STRING)
				except:
					string_value = "Caget failed"
				#print("%s='%s'" % (recordName+'.'+fieldName, value))
				if string_value != "Caget failed":
					if dbd.isDefaultValue(value, r.recordType, fieldName, dbd_object):
						continue
					if (fixUserCalcs and r.recordName.find(':user') and 
						fieldName in ['DISA', 'DISV', 'SDIS']):
						continue
				r.fieldNames.append(fieldName)
				r.fieldValues.append(string_value)
	return recordInstanceList

def writeNewDatabase(fileName, pvList, dbdFileName, replaceDict=None, fixUserCalcs=True):
	dbd_object = dbd.readDBD(dbdFileName)
	recordInstanceList = defineNewDatabase(pvList, dbd_object, fixUserCalcs)
	dbd.writeDatabase(fileName, recordInstanceList, replaceDict)

def writeColorTable(fp):
	fp.write('"color map" {\n\tncolors=65\n\tcolors {\n\t\tffffff,\n\t\tececec,\n\t\tdadada,\n\t\tc8c8c8,\n')
	fp.write('\t\tbbbbbb,\n\t\taeaeae,\n\t\t9e9e9e,\n\t\t919191,\n\t\t858585,\n\t\t787878,\n\t\t696969,\n')
	fp.write('\t\t5a5a5a,\n\t\t464646,\n\t\t2d2d2d,\n\t\t000000,\n\t\t00d800,\n\t\t1ebb00,\n\t\t339900,\n')
	fp.write('\t\t2d7f00,\n\t\t216c00,\n\t\tfd0000,\n\t\tde1309,\n\t\tbe190b,\n\t\ta01207,\n\t\t820400,\n')
	fp.write('\t\t5893ff,\n\t\t597ee1,\n\t\t4b6ec7,\n\t\t3a5eab,\n\t\t27548d,\n\t\tfbf34a,\n\t\tf9da3c,\n')
	fp.write('\t\teeb62b,\n\t\te19015,\n\t\tcd6100,\n\t\tffb0ff,\n\t\td67fe2,\n\t\tae4ebc,\n\t\t8b1a96,\n')
	fp.write('\t\t610a75,\n\t\ta4aaff,\n\t\t8793e2,\n\t\t6a73c1,\n\t\t4d52a4,\n\t\t343386,\n\t\tc7bb6d,\n')
	fp.write('\t\tb79d5c,\n\t\ta47e3c,\n\t\t7d5627,\n\t\t58340f,\n\t\t99ffff,\n\t\t73dfff,\n\t\t4ea5f9,\n')
	fp.write('\t\t2a63e4,\n\t\t0a00b8,\n\t\tebf1b5,\n\t\td4db9d,\n\t\tbbc187,\n\t\ta6a462,\n\t\t8b8239,\n')
	fp.write('\t\t73ff6b,\n\t\t52da3b,\n\t\t3cb420,\n\t\t289315,\n\t\t1a7309,\n\t}\n}\n')

import math
def makeGrid(geom, border, maxWidth, maxHeight):
	numDisplays = len(geom)
	numX = max(1,int(round(math.sqrt(numDisplays), 0)))
	numY = max(1, int(numDisplays / numX))
	if numX*numY < numDisplays: numY += 1
	#print "numDisplays, numX, numY=", numDisplays, numX, numY
	if maxWidth > maxHeight*2:
		numX = max(1,int(round(numX/2, 0)))
		numY = max(1, int(numDisplays / numX))
		if numX*numY < numDisplays: numY += 1
	elif maxHeight > maxWidth*2:
		numY = max(1,int(round(numY/2, 0)))
		numX = max(1, int(numDisplays / numY))
		if numX*numY < numDisplays: numX += 1
	#print "numDisplays, numX, numY=", numDisplays, numX, numY

	ix = -1
	iy = 0
	newGeom = []
	maxWidth += border
	maxHeight += border
	for i in range(len(geom)):
		ix += 1
		if ix >= numX:
			ix = 0
			iy += 1
		newGeom.append((border+ix*maxWidth, border+iy*maxHeight, geom[i][2], geom[i][3]))
	totalWidth = numX * maxWidth + border
	totalHeight = numY * maxHeight + border
	return (newGeom, totalWidth, totalHeight)

def writeNewMEDM_Composites(fileName, recordNames, recordTypes, displayStrings=[], replaceDict={}, EPICS_DISPLAY_PATH=[]):

	geom=[]
	totalWidth = 0
	totalHeight = 10
	maxWidth = 0
	maxHeight = 0
	for i in range(len(recordNames)):
		rName = recordNames[i]
		rType = recordTypes[i]
		displayString = displayStrings[i]
		(display, macro) = displayString.split(';')
		displayFile = findFileInPath(display, EPICS_DISPLAY_PATH)
		if not displayFile:
			print "Can't find display file '%s' in EPICS_DISPLAY_PATH" % display
			return
		#print "writeNewMEDM_Composites: displayFile = ", displayFile
		dFile = open(displayFile, "r")
		lines = dFile.readlines()
		dFile.close()
		for i in range(len(lines)):
			line = lines[i].lstrip()
			if line.startswith('width'):
				width = int(line.split('=')[1])
				height = int(lines[i+1].lstrip().split('=')[1])
				geom.append((10, totalHeight, width, height))
				maxWidth = max(maxWidth, width)
				maxHeight = max(maxHeight, height)
				totalWidth = max(width, totalWidth)
				totalHeight += height+10
				break
		totalWidth += 20
		#print "writeNewMEDM_Composites: displayFile '%s'; w=%d,h=%d " % (displayFile, width, height)

	(geom, totalWidth, totalHeight) = makeGrid(geom, 10, maxWidth, maxHeight)

	if (fileName):
		fp = open(fileName, "w")
	else:
		fp = sys.stdout
	fp.write('\nfile {\n\tname="%s"\n\tversion=030102\n}\n' % fileName)
	fp.write('display {\n\tobject {\n\t\tx=%d\n\t\ty=%d\n\t\twidth=%d\n\t\theight=%d\n\t}\n' %
		(100, 100, totalWidth, totalHeight))
	fp.write('\tclr=14\n\tbclr=4\n\tcmap=""\n\tgridSpacing=5\n\tgridOn=0\n\tsnapToGrid=0\n}\n')
	writeColorTable(fp)
	for i in range(len(recordNames)):
		rName = recordNames[i]
		rType = recordTypes[i]
		displayString = displayStrings[i]
		(x,y,w,h) = geom[i]
		fp.write('composite {\n\tobject {\n\t\tx=%d\n\t\ty=%d\n\t\twidth=%d\n\t\theight=%d\n\t}\n' % (x,y, w, h))
		(display, macro) = displayString.split(';')
		newMacro = dbd.doReplace(macro, replaceDict)
		newName = dbd.doReplace(rName, replaceDict)
		fp.write('\t"composite name"=""\n')
		fp.write('\t"composite file"="%s;%s"\n}\n' % (display, newMacro))
	fp.close()

def writeNewMEDM_RDButtons(fileName, recordNames, recordTypes, displayStrings=[], replaceDict={}, EPICS_DISPLAY_PATH=[]):
	if (fileName):
		file = open(fileName, "w")
	else:
		file = sys.stdout
	file.write('\nfile {\n\tname="%s"\n\tversion=030102\n}\n' % fileName)

	file.write('display {\n\tobject {\n\t\tx=%d\n\t\ty=%d\n\t\twidth=%d\n\t\theight=%d\n\t}\n' % (100, 100, 200, 20+len(recordNames)*25))
	file.write('\tclr=14\n\tbclr=4\n\tcmap=""\n\tgridSpacing=5\n\tgridOn=0\n\tsnapToGrid=0\n}\n')
	writeColorTable(file)
	for i in range(len(recordNames)):
		rName = recordNames[i]
		rType = recordTypes[i]
		displayString = displayStrings[i]
		file.write('"related display" {\n\tobject {\n\t\tx=%d\n\t\ty=%d\n\t\twidth=150\n\t\theight=20\n\t}\n' % (10, 10+i*25))
		(display, macro) = displayString.split(';')
		newMacro = dbd.doReplace(macro, replaceDict)
		newName = dbd.doReplace(rName, replaceDict)
		file.write('\tdisplay[0] {\n\t\tlabel="%s"\n\t\tname="%s"\n\t\targs="%s"\n\t}\n' % (newName, display, newMacro))
		file.write('\tclr=14\n\tbclr=51\n\tlabel="%c%s"\n}\n' % ('-', newName))
	file.close()

# For now, the following function can write an medm file for only a single record
def writeNewMEDM_Objects(fileName, recordNames, recordTypes, displayStrings=[], replaceDict={}, EPICS_DISPLAY_PATH=[]):

	geom=[]
	totalWidth = 0
	totalHeight = 10
	maxWidth = 0
	maxHeight = 0
	for i in range(len(recordNames)):
		rName = recordNames[i]
		rType = recordTypes[i]
		displayString = displayStrings[i]
		(display, macro) = displayString.split(';')
		displayFile = findFileInPath(display, EPICS_DISPLAY_PATH)
		if not displayFile:
			print "Can't find display file '%s' in EPICS_DISPLAY_PATH" % display
			return
		#print "writeNewMEDM_Composites: displayFile = ", displayFile
		dFile = open(displayFile, "r")
		lines = dFile.readlines()
		dFile.close()
		for i in range(len(lines)):
			line = lines[i].lstrip()
			if line.startswith('width'):
				width = int(line.split('=')[1])
				height = int(lines[i+1].lstrip().split('=')[1])
				geom.append((10, totalHeight, width, height))
				maxWidth = max(maxWidth, width)
				maxHeight = max(maxHeight, height)
				totalWidth = max(width, totalWidth)
				totalHeight += height+10
				break
		totalWidth += 20
		#print "writeNewMEDM_Composites: displayFile '%s'; w=%d,h=%d " % (displayFile, width, height)

	# Get only the lines we'll use from the medm file
	startLine = 0
	for i in range(len(lines)):
		if (lines[i].startswith('"color map')):
			numColors = int(lines[i+1].split("=")[1])
			startLine = i+numColors+5
			#print "start line:", lines[startLine]

	(geom, totalWidth, totalHeight) = makeGrid(geom, 10, maxWidth, maxHeight)

	if (fileName):
		fp = open(fileName, "w")
	else:
		fp = sys.stdout
	fp.write('\nfile {\n\tname="%s"\n\tversion=030102\n}\n' % fileName)
	fp.write('display {\n\tobject {\n\t\tx=%d\n\t\ty=%d\n\t\twidth=%d\n\t\theight=%d\n\t}\n' %
		(100, 100, totalWidth, totalHeight))
	fp.write('\tclr=14\n\tbclr=4\n\tcmap=""\n\tgridSpacing=5\n\tgridOn=0\n\tsnapToGrid=0\n}\n')
	writeColorTable(fp)

	for i in range(len(recordNames)):
		rName = recordNames[i]
		rType = recordTypes[i]
		displayString = displayStrings[i]
		(display, macro) = displayString.split(';')
		macros = macro.split(",")
		rDict = {}
		for m in macros:
			(target, replacement) = m.split("=")
			target = '$(%s)' % target
			rDict[target] = replacement
		
		(x,y,w,h) = geom[i]
		for line in lines[startLine:]:
			l = dbd.doReplace(line, rDict)
			fp.write(dbd.doReplace(l, replaceDict))
	fp.close()

###################################################################
# GUI STUFF
###################################################################

# From Python Cookbook
import re
re_digits = re.compile(r'(\d+)')
def embedded_numbers(s):
	pieces = re_digits.split(s)             # split into digits/nondigits
	pieces[1::2] = map(int, pieces[1::2])   # turn digits into numbers
	return pieces
def sort_strings_with_embedded_numbers(alist):
	aux = [ (embedded_numbers(s), s) for s in alist ]
	aux.sort()
	return [ s for __, s in aux ]           # convention: __ means "ignore"

def cmpStringsWithEmbeddedNumbers(s1, s2):
	if s1 == s2: return 0
	ss = sort_strings_with_embedded_numbers([s1,s2])
	if ss[0] == s1: return 1
	return -1

def parseReplacementsFromEnvString(s):
	replacements = s.split(',')
	replaceDict = {}
	for rep in replacements:
		target, string = rep.split('=')
		replaceDict[target]=string
	return replaceDict

def findFileInPath(file, pathList):
	for path in pathList:
		fullPath = os.path.join(path, file)
		if os.path.isfile(fullPath):
			return(fullPath)
	return("")

class myList(wx.ListCtrl, listmix.ColumnSorterMixin, listmix.ListCtrlAutoWidthMixin, listmix.TextEditMixin):
	def __init__(self, parent, frame, purpose):
		wx.ListCtrl.__init__(
			self, parent, -1, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

		self.parent = parent
		self.frame = frame
		self.purpose = purpose
		self.itemDataMap = {}

		if purpose == "recordNames":
			numColumns = 3
			self.InsertColumn(0, "Record name")
			self.InsertColumn(1, "Record type")
			self.InsertColumn(2, "Display string")
		else:
			numColumns = 2
			self.InsertColumn(0, "Live string")
			self.InsertColumn(1, "In-File string")

		# fill list
		if self.purpose == "recordNames":
			i = 0
			if len(self.frame.recordNames) > 0:
				for i in range(len(self.frame.recordNames)):
					self.itemDataMap[i] = (self.frame.recordNames[i], self.frame.recordTypes[i], self.frame.displayStrings[i])
				i += 1
			self.itemDataMap[i] = (
				"Record name",
				"Record type",
				"abc.adl;P=$(P),R=yy"
			)
		else:
			i = 0
			if len(self.frame.replaceTargets) > 0:
				for i in range(len(self.frame.replaceTargets)):
					self.itemDataMap[i] = (self.frame.replaceTargets[i], self.frame.replaceStrings[i])
				i += 1
			self.itemDataMap[i] = (
				"Live string",
				"In-File string",
			)

		self.lastKey = i

		items = self.itemDataMap.items()
		for (i, data) in items:
			self.InsertStringItem(i, data[0])
			self.SetItemData(i, i)
			self.SetStringItem(i, 1, data[1])
			if numColumns > 2:
				self.SetStringItem(i, 2, data[2])
		self.SetItemTextColour(self.lastKey, "red")

		listmix.ColumnSorterMixin.__init__(self, numColumns)
		listmix.TextEditMixin.__init__(self)

		for i in range(numColumns):
			self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

		# Bind events to code
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self)
		self.selectedItems = set()

		# for wxMSW
		self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

		# for wxGTK
		self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

		# for edit veto
		#self.Bind(wx.EVT_COMMAND_LIST_BEGIN_LABEL_EDIT, self.OnEditRequest)

	def SetStringItem(self, index, col, data):
		#if self.purpose == "recordNames":
		#	print "SetStringItem: index=", index, " col=", col, " data='%s'" % data
		#	print "SetStringItem: GetItemData(%d)=%d" % (index, self.GetItemData(index))
		if index < len(self.frame.displayStrings) and col == 2: #only for this column do we permit edits (only medm display string)
			wx.ListCtrl.SetStringItem(self, index, col, data)
			self.frame.displayStrings[self.GetItemData(index)] = str(data)
		#	if self.purpose == "recordNames":
		#		print "displayStrings='%s'\n" % self.frame.displayStrings
		else:
			wx.ListCtrl.SetStringItem(self, index, col, self.itemDataMap[index][col])

	def GetListCtrl(self):
		return self

	def GetColumnSorter(self):
		"""Returns a callable object to be used for comparing column values when sorting."""
		return self.__ColumnSorter

	def __ColumnSorter(self, key1, key2):
		col = self._col
		ascending = self._colSortFlag[col]
		if key1 == self.lastKey:
			return 1
		if key2 == self.lastKey:
			return -1

		item1 = self.itemDataMap[key1][col]
		item2 = self.itemDataMap[key2][col]

		cmpVal = cmpStringsWithEmbeddedNumbers(item1, item2)
		if cmpVal == 0:
			item1 = self.itemDataMap[key1][0]
			item2 = self.itemDataMap[key2][0]
			#cmpVal = locale.strcoll(str(item1), str(item2))
			cmpVal = cmpStringsWithEmbeddedNumbers(item1, item2)

			if cmpVal == 0:
				cmpVal = key1 < key2

		if ascending:
			return cmpVal
		else:
			return -cmpVal

	# evidently there is a way to veto a list-edit event, and I'd like to
	# do this, but don't know how.  Here's some test code motivated by the OpenEditor
	# function from wx.lib.mixins.listctrl.py's TextEditMixin class.
	def OnEditRequest(self, event):
		pass
		#print "OnEditRequest: event=", event, " row=", event.m_itemIndex, " col=", event.m_col

	def OnItemSelected(self, event):
		self.selectedItems.add(event.m_itemIndex)
		#print "OnItemSelected: GetIndex=%d" % event.GetIndex()
		listmix.TextEditMixin.OnItemSelected(self, event)
		event.Skip()

	def OnItemDeselected(self, event):
		if event.m_itemIndex in self.selectedItems:
			self.selectedItems.remove(event.m_itemIndex)
		event.Skip()

	def OnRightClick(self, event):
		# only do this part the first time so the events are only bound once
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
			if self.purpose == "recordNames":
				self.popupID2 = wx.NewId()
				self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)

		if (len(self.itemDataMap) <= 1):
			return

		# make a menu
		menu = wx.Menu()
		# add some items
		menu.Append(self.popupID1, "Delete from list")
		if self.purpose == "recordNames":
			menu.Append(self.popupID2, "Write MEDM display for this record")

		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(menu)
		menu.Destroy()

	def OnPopupOne(self, event):
		#print "OnPopupOne"
		#print "selected items:", self.selectedItems
		items = list(self.selectedItems)
		item = items[0]
		if self.purpose == "recordNames":
			if item < len(self.frame.recordNames):
				self.DeleteItem(item)
				del self.frame.recordNames[item]
				del self.frame.recordTypes[item]
				del self.frame.displayStrings[item]
			#print "records:", self.frame.recordNames
		else:
			if item < len(self.frame.replaceTargets):
				self.DeleteItem(item)
				del self.frame.replaceTargets[item]
				del self.frame.replaceStrings[item]
			#print "replaceTargets:", self.frame.replaceTargets

	# Although self.selectedItems may contain several items, we're only going to
	# write a file for the first one.
	def OnPopupTwo(self, event):
		#print "OnPopupTwo"
		#print "selected items:", self.selectedItems
		if (len(self.itemDataMap) <= 1):
			return
		global medmPath
		if len(self.frame.recordNames) <= 0:
			return
		wildcard = "(*.adl)|*.adl|All files (*.*)|*.*"
		if medmPath == "":
			medmPath = os.getcwd()
		items = list(self.selectedItems)
		item = items[0]
		if item >= len(self.frame.recordNames):
			return
		recordNameList = [self.frame.recordNames[item]]
		fileName = recordNameList[0]
		if fileName.find(":"):
			fileName = fileName.split(":")[1]
		fileName += ".adl"
		dlg = wx.FileDialog(self, message="Save as ...",
			defaultDir=medmPath, defaultFile=fileName, wildcard=wildcard,
			style=wx.SAVE | wx.CHANGE_DIR)
		ans = dlg.ShowModal()
		if ans == wx.ID_OK:
			medmPath = dlg.GetPath()
		dlg.Destroy()
		if ans == wx.ID_OK and medmPath:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			recordNameList = [self.frame.recordNames[item]]
			recordTypeList = [self.frame.recordTypes[item]]
			displayStringList = [self.frame.displayStrings[item]]
			replaceDict = makeReplaceDict(self.frame.replaceTargets, self.frame.replaceStrings)
			writeNewMEDM_Objects(medmPath, recordNameList, recordTypeList, displayStringList, replaceDict, self.frame.EPICS_DISPLAY_PATH)
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

class myListPanel(wx.Panel):
   def __init__(self, parent, frame, purpose):
		wx.Panel.__init__(self, parent, -1, style=wx.BORDER_SUNKEN)
		#wx.Panel.__init__(self, parent, -1)
		self.parent = parent
		self.frame = frame
		self.purpose = purpose
		sizer = wx.BoxSizer(wx.VERTICAL)
		if purpose == "recordNames":
			title = wx.StaticText(self, -1, "Record list: Click column head to sort.\nRight click on entry to delete, or write MEDM file.\nLeft click in display string to edit. (Note that entire item must be visible to edit it.)")
		else:
			title = wx.StaticText(self, -1, "Replacement list: Click column head to sort.\nRight click on entry to delete.")
		sizer.Add(title, 0, wx.ALL, 5)
		self.list = myList(self, self.frame, self.purpose)
		sizer.Add(self.list, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
		self.SetSizer(sizer)

class MainPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.parent = parent

		self.bottomWin = wx.SashLayoutWindow(self, -1, (-1,-1), (200, 30), wx.SW_3D)
		self.bottomWin.SetDefaultSize((-1, 25))
		self.bottomWin.SetOrientation(wx.LAYOUT_HORIZONTAL)
		self.bottomWin.SetAlignment(wx.LAYOUT_BOTTOM)
		# Doesn't work; have to do it by hand in self.OnSashDrag()
		#self.bottomWin.SetMinimumSizeY(30)

		self.topWin = wx.SashLayoutWindow(self, -1, (-1,-1), (-1, -1), wx.SW_3D)
		(x,y) = self.parent.GetClientSize()
		self.topWin.SetDefaultSize((-1, y-30))
		self.topWin.SetOrientation(wx.LAYOUT_HORIZONTAL)
		self.topWin.SetAlignment(wx.LAYOUT_TOP)
		self.topWin.SetSashVisible(wx.SASH_BOTTOM, True)
		self.topWin.SetMinimumSizeY(30)

		self.Bind(wx.EVT_SASH_DRAGGED, self.OnSashDrag, id=self.topWin.GetId())
		self.Bind(wx.EVT_SIZE, self.OnSize)

	def OnSashDrag(self, event):
		#print "OnSashDrag: height=", event.GetDragRect().height
		(pW, pH) =  self.parent.GetClientSize()
		#print "OnSashDrag: clientHeight=", pH

		eobj = event.GetEventObject()
		height = event.GetDragRect().height
		topWinHeight = max(30, min(pH-30, height))
		# Because bottomWin was created first, LayoutWindow doesn't care
		# about topWin's default size
		#self.topWin.SetDefaultSize((-1, topWinHeight))
		self.bottomWin.SetDefaultSize((-1, pH-topWinHeight))
		wx.LayoutAlgorithm().LayoutWindow(self, None)

	def OnSize(self, event):
		#print "OnSize: height=", self.parent.GetClientSize()[1]
		wx.LayoutAlgorithm().LayoutWindow(self, None)

class TopFrame(wx.Frame):
	global displayInfo
	def __init__(self, parent, id, title, **kwds):
		wx.Frame.__init__(self, parent, id, title, **kwds)

		self.width = None
		self.height = None

		# init data structures
		self.dbd = None
		if os.environ.has_key('SNAPDB_DBDFILE'):
			self.dbdFileName = os.environ['SNAPDB_DBDFILE']
			self.dbd = dbd.readDBD(self.dbdFileName)
		else:
			self.dbdFileName = "<NOT YET SPECIFIED> (Use 'File' menu to open DBD file.)"
		self.displayInfoFileName = "<using internal displayInfo>"
		self.recordNames = []
		self.recordTypes = []
		self.displayStrings = []

		self.replaceTargets = []
		self.replaceStrings = []
		if os.environ.has_key('SNAPDB_REPLACEMENTS'):
			replaceDict = parseReplacementsFromEnvString(os.environ['SNAPDB_REPLACEMENTS'])
			for k in replaceDict.keys():
				self.replaceTargets.append(k)
				self.replaceStrings.append(replaceDict[k])

		if os.environ.has_key('SNAPDB_DISPLAYINFOFILE'):
			global displayInfo
			self.displayInfoFileName = os.environ['SNAPDB_DISPLAYINFOFILE']
			displayInfo = readDisplayInfoFile(self.displayInfoFileName)

		self.EPICS_DISPLAY_PATH = ['.']
		if os.environ.has_key('EPICS_DISPLAY_PATH'):
			self.EPICS_DISPLAY_PATH = os.environ['EPICS_DISPLAY_PATH'].split(':')

		self.fixUserCalcs = True

		# make menuBar
		menu1 = wx.Menu()
		menu1.Append(101, "Open DBD file", "Open .dbd file")
		menu1.Append(102, "Open database file", "Open database file")
		menu1.Append(103, "Write database file", "Write database file")
		menu1.Append(104, "Write MEDM-display file (buttons)", "Write MEDM-display file  (buttons)")
		menu1.Append(105, "Write MEDM-display file (composites)", "Write MEDM-display file (composites)")
		menu1.Append(106, "Read displayInfo file", "Read displayInfo file")
		menu1.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this application")
		self.Bind(wx.EVT_MENU, self.on_openDBD_MenuSelection, id=101)
		self.Bind(wx.EVT_MENU, self.on_openDB_MenuSelection, id=102)
		self.Bind(wx.EVT_MENU, self.on_writeDB_MenuSelection, id=103)
		self.Bind(wx.EVT_MENU_RANGE, self.on_writeMEDM_MenuSelection, id=104, id2=105)
		self.Bind(wx.EVT_MENU, self.on_readDI_MenuSelection, id=106)
		self.Bind(wx.EVT_MENU, self.on_Exit_Event, id=wx.ID_EXIT)
		menuBar = wx.MenuBar()
		menuBar.Append(menu1, "&File")
		self.SetMenuBar(menuBar)

		# make statusBar
		statusBar = self.CreateStatusBar()
		statusBar.SetFieldsCount(1)

		self.mainPanel = MainPanel(self)
		self.fillMainPanel()

	def on_Exit_Event(self, event):
		self.Close()

	def fillMainPanel(self):
		topPanel = wx.Panel(self.mainPanel.topWin, style=wx.BORDER_SUNKEN)
		topPanelSizer = wx.BoxSizer(wx.VERTICAL)
		topPanel.SetSizer(topPanelSizer)
		text1 = wx.StaticText(topPanel, -1, ".dbd File: %s" % self.dbdFileName)
		text2 = wx.StaticText(topPanel, -1, "displayInfo File: %s" % self.displayInfoFileName)
		topPanelSizer.Add(text1, 0, wx.LEFT|wx.TOP, 5)
		topPanelSizer.Add(text2, 0, wx.LEFT|wx.BOTTOM, 5)

		workPanel = wx.Panel(topPanel, style=wx.BORDER_SUNKEN)
		workPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
		workPanel.SetSizer(workPanelSizer)

		# records panel
		recordsPanel = wx.Panel(workPanel)
		recordsPanelSizer = wx.BoxSizer(wx.VERTICAL)
		recordsPanel.SetSizer(recordsPanelSizer)
		rap = wx.Panel(recordsPanel)
		rapSizer = wx.BoxSizer(wx.HORIZONTAL)
		lt = wx.StaticText(rap, -1, "add new record:")
		rt = wx.TextCtrl(rap, -1, "", size=(200,-1), style=wx.TE_PROCESS_ENTER)
		rapSizer.Add(lt, 0, 0)
		rapSizer.Add(rt, 1, 0)
		rap.SetSizer(rapSizer)
		self.Bind(wx.EVT_TEXT_ENTER, self.addRecordName, rt)
		recordsPanelSizer.Add(rap, 0, wx.ALL, 5)
		rlp = myListPanel(recordsPanel, self, "recordNames")
		recordsPanelSizer.Add(rlp, 1, wx.EXPAND|wx.ALL, 5)

		# replacements panel
		replacementsPanel = wx.Panel(workPanel)
		replacementsPanelSizer = wx.BoxSizer(wx.VERTICAL)
		replacementsPanel.SetSizer(replacementsPanelSizer)
		rap = wx.Panel(replacementsPanel)
		rapSizer = wx.BoxSizer(wx.HORIZONTAL)
		lt = wx.StaticText(rap, -1, "add new replacement\n(e.g., 'xxx=abc')")
		rt = wx.TextCtrl(rap, -1, "", size=(200,-1), style=wx.TE_PROCESS_ENTER)
		rapSizer.Add(lt, 0, 0)
		rapSizer.Add(rt, 1, 0)
		rap.SetSizer(rapSizer)
		self.Bind(wx.EVT_TEXT_ENTER, self.addReplacement, rt)
		replacementsPanelSizer.Add(rap, 0, wx.ALL, 5)
		rlp = myListPanel(replacementsPanel, self, "replacements")
		replacementsPanelSizer.Add(rlp, 1, wx.EXPAND|wx.ALL, 5)

		workPanelSizer.Add(recordsPanel, 5, wx.EXPAND|wx.ALL, 5)
		workPanelSizer.Add(replacementsPanel, 2, wx.EXPAND|wx.ALL, 5)

		topPanelSizer.Add(workPanel, 1, wx.EXPAND|wx.ALL, 5)
		self.mainPanel.Fit()

	def addRecordName(self, event):
		rName = str(event.GetString().split(".")[0])
		if rName == "":
			self.SetStatusText("empty record name")
			return
		if HAVE_CA:
			pvName = rName+".RTYP"
			try:
				rType = caget(pvName)
			except:
				rType = "unknown"
		else:
			#print "rName=", rName
			print "Pretending to do caget('%s')" % (rName+".RTYP")
			rType = "unknown"
		if rName in self.recordNames:
			self.SetStatusText("'%s' is already in the list of records" % rName)
		else:
			self.recordNames.append(rName)
			self.recordTypes.append(rType)
			if rType in displayInfo.keys():
				(prefix, name) = rName.split(':', 1)
				replaceDict = makeReplaceDict(self.replaceTargets, self.replaceStrings)
				prefix = dbd.doReplace(prefix+':', replaceDict)
				name = dbd.doReplace(name, replaceDict)
				del replaceDict
				dString = displayInfo[rType][0] + ';'
				dString += displayInfo[rType][1] + '=%s,' % prefix
				dString += displayInfo[rType][2] + '=%s' % name
				self.displayStrings.append(dString)
			else:
				#print "no displayInfo for record type '%s'" % rType
				self.SetStatusText("no displayInfo for record type '%s'" % rType)
				self.displayStrings.append("")
			#print "add new record: ", rName
			self.mainPanel.Destroy()
			self.mainPanel = MainPanel(self)
			self.fillMainPanel()
			self.SendSizeEvent()

	def addReplacement(self, event):
		target, replacement = event.GetString().split("=")
		#print "target, replacement =", target, replacement
		self.replaceTargets.append(target)
		self.replaceStrings.append(replacement)
		#print "add new replacement: ", target, replacement
		self.mainPanel.Destroy()
		self.mainPanel = MainPanel(self)
		self.fillMainPanel()
		self.SendSizeEvent()

	def openFile(self):
		wildcard = "(*.dbd)|*.dbd|All files (*.*)|*.*"
		dlg = wx.FileDialog(self, message="Choose a file",
			defaultDir=os.getcwd(), defaultFile="", wildcard=wildcard,
			style=wx.OPEN | wx.CHANGE_DIR)
		path = None
		ans = dlg.ShowModal()
		if ans == wx.ID_OK:
			path = dlg.GetPath()
		dlg.Destroy()
		return path

	def on_openDBD_MenuSelection(self, event):
		self.dbdFileName = self.openFile()
		if self.dbdFileName:
			self.mainPanel.Destroy()
			self.dbd = dbd.readDBD(self.dbdFileName)
			self.mainPanel = MainPanel(self)
			self.fillMainPanel()
			self.SendSizeEvent()

	def on_openDB_MenuSelection(self, event):
		global databasePath
		wildcard = "(*.db)|*.db|All files (*.*)|*.*"
		if databasePath == "":
			databasePath = os.getcwd()
		dlg = wx.FileDialog(self, message="Open ...",
			defaultDir=databasePath, defaultFile="test.db", wildcard=wildcard,
			style=wx.OPEN | wx.CHANGE_DIR)
		ans = dlg.ShowModal()
		if ans == wx.ID_OK:
			databasePath = dlg.GetPath()
		dlg.Destroy()
		if ans == wx.ID_OK and databasePath:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			replaceDict = makeReplaceDict(self.replaceTargets, self.replaceStrings)
			(self.recordNames, self.recordTypes, self.displayStrings) = openDatabase(databasePath,
				self.recordNames, self.recordTypes, self.displayStrings, replaceDict)
			del replaceDict
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
			#print "on_openDB_MenuSelection: recordNames = ", self.recordNames
			self.mainPanel.Destroy()
			self.mainPanel = MainPanel(self)
			self.fillMainPanel()
			self.SendSizeEvent()


	def on_writeDB_MenuSelection(self, event):
		global databasePath
		if self.dbdFileName.find("<NOT") != -1:
			self.SetStatusText("You have to open a .dbd file first")
			return
		if len(self.recordNames) <= 0:
			self.SetStatusText("No records")
			return
		wildcard = "(*.db)|*.db|All files (*.*)|*.*"
		if databasePath == "":
			databasePath = os.getcwd()
		dlg = wx.FileDialog(self, message="Save as ...",
			defaultDir=databasePath, defaultFile="test.db", wildcard=wildcard,
			style=wx.SAVE | wx.CHANGE_DIR)
		ans = dlg.ShowModal()
		if ans == wx.ID_OK:
			databasePath = dlg.GetPath()
		dlg.Destroy()
		if ans == wx.ID_OK and databasePath:
			replaceDict = makeReplaceDict(self.replaceTargets, self.replaceStrings)
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			writeNewDatabase(databasePath, self.recordNames, self.dbdFileName, replaceDict, self.fixUserCalcs)
			del replaceDict
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def on_writeMEDM_MenuSelection(self, event):
		id = event.GetId()
		global medmPath
		if len(self.recordNames) <= 0:
			self.SetStatusText("No records")
			return
		wildcard = "(*.adl)|*.adl|All files (*.*)|*.*"
		if medmPath == "":
			medmPath = os.getcwd()
		dlg = wx.FileDialog(self, message="Save as ...",
			defaultDir=medmPath, defaultFile="test.adl", wildcard=wildcard,
			style=wx.SAVE | wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			medmPath = dlg.GetPath()
		dlg.Destroy()
		if medmPath:
			self.SetCursor(wx.StockCursor(wx.CURSOR_WATCH))
			replaceDict = makeReplaceDict(self.replaceTargets, self.replaceStrings)
			if id == 104:
				writeNewMEDM_RDButtons(medmPath, self.recordNames, self.recordTypes, self.displayStrings, replaceDict, self.EPICS_DISPLAY_PATH)
			else:
				writeNewMEDM_Composites(medmPath, self.recordNames, self.recordTypes, self.displayStrings, replaceDict, self.EPICS_DISPLAY_PATH)
			del replaceDict
			self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))

	def on_readDI_MenuSelection(self, event):
		global displayInfo

		wildcard = "(*.txt)|*.txt|All files (*.*)|*.*"
		diPath = os.getcwd()
		dlg = wx.FileDialog(self, message="Open ...",
			defaultDir=diPath, defaultFile="displayInfo.txt", wildcard=wildcard, style=wx.OPEN)
		ans = dlg.ShowModal()
		if ans == wx.ID_OK:
			diPath = dlg.GetPath()
		dlg.Destroy()

		if ans == wx.ID_OK and diPath:
			self.mainPanel.Destroy()
			self.displayInfoFileName = diPath
			displayInfo = readDisplayInfoFile(diPath)
			self.mainPanel = MainPanel(self)
			self.fillMainPanel()
			self.SendSizeEvent()

def main():
	app = wx.PySimpleApp()
	frame = TopFrame(None, -1, 'dbd', size=(800,400))
	#frame = TopFrame(None, -1, 'dbd')
	frame.Center()
	(hS, vS) = frame.GetSize()
	(hP, vP) = frame.GetPosition()
	frame.width = (hP + hS/2)*2
	frame.height = (vP + vS/2)*2
	frame.SetMaxSize((frame.width, frame.height))
	frame.Show(True)
	app.MainLoop()

if __name__ == "__main__":
	main()
