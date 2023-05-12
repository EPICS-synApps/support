utils Release Notes
===================

synApps release 6-2
-------------------

*   Python Wheel Install File created for mdaPythonUtils


synApps release 6-1
-------------------

*   copyScreens.pl:
    *   replaces copyAdl, copyUi, and copyOpi
    *   top level synapps makefile now has a set of targets to replicate those scripts
    *   use 'make all\_adl', 'make all\_ui', or 'make all\_opi', respectively

synApps release 6-0
-------------------

*   changePrefix:
    *   Rewritten in perl to allow cross-platform usage
    *   Updated for synApps 6-0 reorganization of xxx

synApps release 5-8
-------------------

*   copyUi.py - Copy all .ui and .qss to specified directory
*   addTag.py - For a module that already has a module tag, tag that same revision with another tag.
*   adlDir2uiDir - Rewritten to change only .ui files in ui directory
*   adl2uiAll - translate all .adl files in synApps to .ui
*   changePrefix:
    *   Better handle testing for existence of files
    *   Made changePrefix smarter about changing prefix in src/Makefile
    *   Modified changePrefix to handle xxx.sh, as well as new versions of run and in-screen.sh
*   snapDb.py - Maintain default paths for medm displays, databases, and displayinfo files; specify display files for aSub, compress, mbbo, mca, scaler, sub, and vme record types.

synApps release 5-7
-------------------

*   snapDb.py - converted to use pyepics
*   mdaExplorer:
    *   added distutils config to simplify installation
    *   merged mda.py and mda\_f.py into mda.py
    *   Made mda.py conditional on availability of wxmpl and axes3d
    *   check for unreasonable scan rank
*   mdaPythonUtils - make mda and f\_xdrlib support installable as a Python package
*   mdautils-src - new version
*   changePrefix - fix for devIocStats, treat op/ui/\*.ui files
*   dependencies.py - find selected dependencies in synApps modules
*   makeTar.py - automate generation of tar file from svn export

synApps release 5-6
-------------------

*   logModuleFromTag.py, releaseNotesFromTag.py: Don't rely on 'svn ls -v' output to write highest revision number first. Search all rev nums for highest.
*   burt.py: Ignore lines with fewer than two words. Don't even parse array lines
*   mdaAscii.py: check rank before trying to print out 2D data. Diagnostics and IndexError exception for 2D printout.
*   mdautils-src: updated to version 1.1
*   tranFiles.py: new program to automate data-file translation
*   copyOpi.py: new program to copy all .opi files from a source tree to a destination tree that is suitable for use with CSS-BOY. Currently, this means the dest tree has its .OPI files in subdirectories with synApps module names.

synApps release 5-5
-------------------

*   Added logModuleFromTag.py and releaseNotesFromTag.py, programs to get commit messages from subversion, given a module name and one or two tags.
*   Added cygwinScripts directory, containing scripts to configure the Cygwin bash shell for building for the cyginx-86 and win32-x86 architectures.
*   Added utils/documentation
    
*   Added burt.py, python support for writing the content of a burt snapshot file to a running IOC. burt.py cannot write a snapshot file.
    
*   mdaExplorer:
    *   Survey MDA files checks directory periodically for new files.
    *   Add file description to directory list.
    *   Can scale 2D plots for square image.
    *   Color bar was displayed on top of image.
*   snapDb
    *   Handle sub-record fields A-L, which have no promptgroup property, but are permitted to be written in .db files.
    *   Don't crash if caget fails to get a value.
    *   Get value as number, for comparison with default value, and as string, for writing to file.
*   mdautils-src
    *   Nov 2009 distribution from Dohn Arms
*   convertIocFiles
    *   New directory in which all convertIocFiles related support is collected.

Suggestions and Comments to:  
[Tim Mooney](mailto:mooney@aps.anl.gov) : (mooney@aps.anl.gov)
