#!/usr/bin/env python

from convertIocFiles import *


usage = """
Usage:    makeAutosaveFiles.py [dir]
    options: -<anything>   (print usage)

Synopsis: makeAutosaveFiles.py examines .cmd and .substitution
    files in an ioc directory ('dir', or the current directory,
    if 'dir' is not supplied), collecting dbLoadRecords/Template
    commands, function calls, variable assignments, etc.  It
    also uses the autosave request file path (defined by
    set_requestfile_path() calls, typically found in
    save_restore.cmd, and the environment variables found in
    either cdCommands or envPaths) to find autosave-include
    files whose names match the names of databases loaded, and
    it examines the macro arguments supplied in database-load
    commands to define the macro commands required for the
    autosave-include files. (It assumes autosave-include macros
    are a subset of dbLoad macros, and that macros take the same
    definitions in both uses.  This is not true for all
    autosave-include files.)
    
    Because makeAutosaveFiles.py uses cdCommands or envPaths,
    the ioc directory must be built before makeAutosaveFiles.py
    can be used on it.

Result: Files named auto_positions.req.STD and auto_settings.req.STD
    are created or overwritten.

See also: convertAutosaveFiles.py, convertIocFiles.py

"""

def main():
	dirName = "."

	if len(sys.argv) > 1:
		if (sys.argv[1][0] == '-'):
			print usage
			return
		dirName = sys.argv[1]

	(cmdFileDicts, subFileDict, autosaveDicts) = collectAllInfo(dirName)
	writeStandardAutosaveFiles(cmdFileDicts, subFileDict, dirName)
		
if __name__ == "__main__":
	main()
