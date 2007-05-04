#!/usr/bin/env python

# This software is intended to help convert an ioc directory from one version
# of synApps to another.  Invoked as a program, it takes two arguments, the
# old directory and the new directory, both of which are assumed to be ioc
# directories (i.e., they contain st.cmd, or other .cmd files).  The program
# parses .cmd files and .substitutions files in the source directory, and
# accumulates information.  Then it parses .cmd files and .substitutions in
# the new directory. For each .cmd file in the new directory, the program
# writes a .cmd.CVT file, which is the .cmd file modified to agree as closely
# as seems reasonable with information collected from the old directory.
# Substitutions files are also treated in this way
#
# The following legal commands are not recognized, because they don't have
# parentheses or commas.
#
# 'epicsEnvSet EPICS_CA_MAX_ARRAY_BYTES 64008'
# 'var motorUtil_debug,1'
# 'iocInit'

import sys
import os
import glob
import string
import curses.ascii
from convertCmdFiles import *
from convertSubFiles import *
from convertAutosaveFiles import *

def parseCmdFiles(d, filespec, verbose):
	cmdFiles = glob.glob(filespec)
	for fileName in cmdFiles:
		d = parseCmdFile(d, fileName, max(verbose,0))
	return (d)

def writeNewCmdFiles(d, filespec, verbose):
	cmdFiles = glob.glob(filespec)
	for fileName in cmdFiles:
		d = writeNewCmdFile(d, fileName, max(verbose,0))
	return(d)

def collectAllInfo(directory=".", verbose=0):
	cmdFileDicts = cmdFileDictionaries()
	subFileDict = {}
	asDicts = {}

	filespec = os.path.join(directory, "*.cmd")
	cmdFileDicts = parseCmdFiles(cmdFileDicts, filespec, verbose)
	if (verbose): writecmdFileDictionaries(cmdFileDictsd, sys.stdout, False)

	filespec = os.path.join(directory, "*.substitutions")
	subFileDict = parseSubFiles(subFileDict, filespec, verbose)
	if (verbose): writeSubFileDictionaries(subFileDict, sys.stdout, 120)

	filespec = os.path.join(directory, "auto*.req")
	asDicts = parseAutosaveFiles(asDicts, filespec, verbose)
	if (verbose): asDicts = writeAutosaveDictionaries(asDicts, sys.stdout, False)

	# parse cdCommands or envPaths file
	file = os.path.join(directory, "cdCommands")
	if os.path.isfile(file):
		cmdFileDicts = parse_cdCommands(cmdFileDicts, file, verbose)
	else:
		file = os.path.join(directory, "envPaths")
		if os.path.isfile(file):
			cmdFileDicts = parse_envPaths(cmdFileDicts, file, verbose)

	return (cmdFileDicts, subFileDict, asDicts)

usage = """
Usage:    convertIocFiles.py [options] old_dir [new_dir]
    options: -v[integer]   (verbose/debug level)

Examples: convertIocFiles.py <old_dir> <new_dir>
    convertIocFiles.py <old_dir>"
    convertIocFiles.py -v1 <old_dir> <new_dir>

Synopsis: convertIocFiles.py examines .cmd files and .substitution
	files, in old_dir, collecting dbLoadRecords/Template
	commands, function calls, variable assignments (though not
	'var' commands), SNL program invocations, script commands,
	and collections of macro-substitution strings.

    If new_dir is specified, new versions of all .cmd files in
    new_dir (named, e.g., st.cmd.CVT) are created or overwritten.
    The new files are patched with information extracted from
    old_dir.  The program notes whether commands in old_dir were
    commented out, and it uses that information in writing
    commands for new_dir.

    The program also creates or overwrites the file
    'convertIocFiles.out' in the current directory.  This file
    contains a list of the commands found in old_dir.  If new_dir
    was specified, only those commands from old_dir that did not
    find a place in new_dir are listed.
"""

def main():
	verbose = 0
	dirArg = 1
	d = cmdFileDictionaries()
	subFileDict = {}
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
			filespec = os.path.join(oldDir, "*.cmd")
			d = parseCmdFiles(d, filespec, verbose)
			if (verbose): writeCmdFileDictionaries(d, sys.stdout, False)

			filespec = os.path.join(oldDir, "*.substitutions")
			subFileDict = parseSubFiles(subFileDict, filespec, verbose)
			if (verbose): writeSubFileDictionaries(subFileDict, sys.stdout, 120)

			filespec = os.path.join(oldDir, "auto*.req")
			dd = parseAutosaveFiles(dd, filespec, verbose)
			if (verbose): dd = writeAutosaveDictionaries(dd, sys.stdout, False)

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
			filespec = os.path.join(newDir, "*.substitutions")
			subFileDict = writeNewSubFiles(subFileDict, filespec)
			wrote_new_files = 1

			# parse cdCommands or envPaths file
			file = os.path.join(newDir, "cdCommands")
			if os.path.isfile(file):
				d = parse_cdCommands(d, file, verbose)
			else:
				file = os.path.join(newDir, "envPaths")
				if os.path.isfile(file):
					d = parse_envPaths(d, file, verbose)

			filespec = os.path.join(newDir, "auto*.req")
			dd = writeNewAutosaveFiles(dd, filespec, verbose)
			writeStandardAutosaveFiles(d, subFileDict, newDir)

		reportFile = open("convertIocFiles.out", "w+")
		if (wrote_new_files):
			writeUnusedCmdFileEntries(d, reportFile)
			writeUnusedSubFileEntries(subFileDict, reportFile, 128)
			writeUnusedAutosaveEntries(dd, reportFile)
		else:
			writeCmdFileDictionaries(d, reportFile)
			writeSubFileDictionaries(subFileDict, reportFile, 128)
			writeAutosaveDictionaries(dd, reportFile)
		reportFile.close()

		
if __name__ == "__main__":
	main()
