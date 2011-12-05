"""
tranFiles.py finds data files, translates them, and writes the
translated files to disk.  The program finds data files either in a
caller-specified directory, or by reading EPICS PVs (using a
caller-specified prefix string) and converting that information to a
directory name.  Files in the data-file directory whose names end with
a caller-specified file extension (default: '.mda') are considered
data files.

If any data files are found, tranFiles.py translates them all, by
executing the caller-specified command <tran_command>, and (in the
simplest case) causes the translations to be written to files named
<dest>.NNNN, where <dest> is supplied, and 'NNNN' is extracted from
data-file names.  For example, the data file 'abc_1234.mda' will result
in the translated file <dest>.1234.  If the translated file
corresponding to a data file already exists, and has a 'modified' time
more recent than that of the data file, then the data file will be
ignored.

<dest> may contain the directives '@<element>' or '@N' or both, as
described in the usage message.  (Run 'python tranFiles.py -h').

"""

import sys
import os
import commands

def tranPath(sourceDir):
	"""
	translate a saveData directory specification, which is of the form
	'//<server>/export/<dirA>/<dirB>/...', to a path that can be reached by us, running
	on a solaris workstation: '/net/<server>/export/<dirA>/<dirB>/...'.
	Not all servers are supported by paths like '/net/<server>/export'.
	For each XOR sector, a server named 'sec<n>' is supported by such a
	path.  For example, sector 4 can use the server 'sec4'.
	"""
	if sourceDir[:2] == '//':
		(server, rest) = sourceDir[2:].split(os.path.sep, 1)
		dir = '/net/' + server + '/' +  rest
	else:
		dir = sourceDir
	return dir

def makeDestNameOld(baseName, sourceName):
	"""
	Given a baseName, and a sourceName of the form 'abc_1234.mda' return
	the string '<baseName>.1234'.
	"""
	# assume only one underline character
	root, right = sourceName.split("_")
	# assume only one "." character
	index, ext = right.split(".")
	return("%s.%s" % (baseName, index))

def findScanNumberString(s):
	"""If s contains 'NNNN', where N stands for any digit, return the string
	beginning with 'NNNN' and extending to the end of s.  If 'NNNN' is not
	found, return ''."""
	n = 0
	for i in range(len(s)):
		if s[i].isdigit():
			n += 1
		else:
			n = 0
		if n == 4:
			return s[i-3:]
	return ''

def makeDestName(destExample, sourceFullPath):

	"""Construct a file name from <sourceFullPath> and <destExample>.

	<sourceFullPath> is used to determine a scan-number string, and maybe the
	base filename for dest files.  First, path and extension are stripped from
	sourceFullPath, leaving bareName.  If bareName contains a string of the form
	'NNNN', where N stands for any digit, then that string begins the
	scan-number string, which extends to the end of bareName.  For example,
	'xyz/abc1234def.mda' yields the scan-number string '1234def'.

	<destExample> is used as a template for the file name.  If '.' is found,
	<base>.<ext> is inferred.  Otherwise, <base>.<ext> = <destExample>.txt. If
	'@D' is found in <base>, it is replaced by the final directory of
	<sourceFullPath>. If '@N' is found, it is replaced by the scan-number
	string.  Otherwise, '_<scan-number string>' is appended to <base>. If <base>
	is blank, '@D' is used.  If <ext> is blank, 'txt' is used.  Examples:

	destExample --> resulting name
	------------------------------
	base        --> base_0123.txt
	@N          --> 0123.txt
	@D.@N       --> <last-dir-name>.0123
	base@N.def  --> base0123.def
	base.@N     --> base.0123
	"""
	
	baseName = os.path.basename(sourceFullPath)
	bareName = os.path.splitext(baseName)[0]
	scanNumberString = findScanNumberString(bareName)
	#print "scanNumberString=",scanNumberString

	lastDir = os.path.basename(os.path.dirname(sourceFullPath))

	if destExample.find('.') != -1:
		(name, ext) = destExample.rsplit('.',1)
	else:
		(name, ext) = (destExample, 'txt')

	if name == '': name = '@D'
	if name.find('@D') != -1:
		name = name.replace('@D', lastDir)

	if name.find('@N') != -1:
		name = name.replace('@N', scanNumberString)
	elif ext.find('@N') != -1:
		ext = ext.replace('@N', scanNumberString)
	else:
		name = name + '_' + scanNumberString
	if ext == '': ext = 'txt'
	return(name+'.'+ext)

def makeDestDir(destDir):
	#print "makeDestDir: destDir = '%s'" % destDir
	if destDir == "":
		return False
	if os.path.isfile(destDir):
		#print "Can't make directory '%s' because a file by that name exists"
		return False
	if os.path.isdir(destDir):
		return True
	if not os.path.isdir(os.path.dirname(destDir)):
		if not makeDestDir(os.path.dirname(destDir)):
			#print "Can't make %s" % os.path.dirname(destDir)
			return False
	try:
		os.mkdir(destDir)
		return True
	except:
		print "Can't make directory '%s'" % destDir
		return False

def doReplacement(sourceDir, destDir):
	at_loc = destDir.find('@')
	if at_loc != -1:
		destElements = destDir.split(os.path.sep)
		for el in destElements:
			if len(el) < 2:
				continue
			if el[0] == '@':
				# '.../@name/...'  (Include /name/...)
				replacement = sourceDir[sourceDir.find(el[1:]):]
				destDir = destDir.replace(el,replacement, 1)
				break
			elif el[-1] == '@':
				# '.../name@/...' (Include everything after /name/)
				(junk,replacement) = sourceDir[sourceDir.find(el[:-1]):].split(os.path.sep,1)
				destDir = destDir.replace(el,replacement, 1)
				break
			else:
				pass
	return destDir

def doTranFiles(sourceDir, destName, translate_command, extension):
	# sourceDir may be a directory name, or an encoding of the EPICS prefix
	# by which a source directory name can be gotten.
	if sourceDir[0] == '@':
		prefix = sourceDir[1:]
		fileSystemPV = prefix + 'saveData_fileSystem'
		subDirPV = prefix + 'saveData_subDir'
		try:
			import ca_util
			saveDataMount = tranPath(ca_util.caget(fileSystemPV))
			saveDataSubDir = ca_util.caget(subDirPV)
		except:
			# Can't use ca_util.  Try running 'caget' from the command line.
			(status, output) = commands.getstatusoutput('caget ' + fileSystemPV)
			if status or output.find('Invalid') != -1:
				print "tranFiles: Can't read source directory\n"
				return
			else:
				saveDataMount = tranPath(output.split()[1])

			(status, output) = commands.getstatusoutput('caget ' + subDirPV)
			if status or output.find('Invalid') != -1:
				print "tranFiles: Can't read source directory\n"
				return
			else:
				saveDataSubDir = output.split()[1]
		sourceDir = os.path.join(saveDataMount, saveDataSubDir)

	# destName may include some path information as well as the text
	# from which ascii file names are to be made.
	destDir = os.path.dirname(destName)
	destBase = os.path.basename(destName)
	destDir = doReplacement(sourceDir, destDir)

	if not os.path.isabs(destDir):
		destDir = os.path.join(sourceDir, destDir)

	sourceFileList = [f for f in os.listdir(sourceDir) if f.endswith(extension)]

	for sourceFile in sourceFileList:
		sourceFullPath = os.path.join(sourceDir, sourceFile)
		destFileName = makeDestName(destBase, sourceFullPath)
		destFullPath = os.path.join(destDir, destFileName)
		if not os.path.exists(destDir) and not makeDestDir(destDir):
			return
		doTranslation = True
		if os.path.exists(destFullPath):
			if os.stat(destFullPath).st_mtime > os.stat(sourceFullPath).st_mtime:
				doTranslation = False
			if os.path.samefile(sourceFullPath, destFullPath):
				print "Source file is same as dest file.  No action."
				doTranslation = False
		if doTranslation:
			command = "%s -o %s %s" % (translate_command, destFullPath, sourceFullPath)
			#print "executing '%s'" % command 
			(status, output) = commands.getstatusoutput(command)
	return

usage_message = """
usage: python tranFiles.py source dest tran_command [extension]
where:
    source       the directory containing files to be translated.  If
                 <source> begins with '@', the rest of <source> is
                 used as the prefix of EPICS-PV names from which the
                 source directory is calculated.
    dest         the base name translated files will have.
    tran_command the full path of the file-translator program, which
                 must honor arguments specifying the output file to be
                 written as follows: 'program -o <outputFile>
                 inputFile'
    extension    the file extension by which data files will be
                 recognized.  If not specified, <extension> defaults
                 to '.mda'. If <extension> does not begin with '.',
                 '.' will be prepended to it.

If <source> begins with '@', the python executable that runs this
program should be capable of importing the ca_util module, which uses
caPython to read EPICS PVs.  If ca_util can't be imported, this
program will try to execute the command-line program, caget, instead.

<dest> tells this program how to name the text files it creates. If
<dest> contains any path information (e.g., 'ascii/base', as opposed
to simply 'base'), the path information will be used in one of two
ways:

    1) if <dest> begins with a '/', it completely specifies the
       directory in which text files will be written.
    2) otherwise, the path part of <dest> will be appended to the
       source directory.

<dest> may contain the directive '@N' in the filename, for example, as
'dirA/tran@N'.  If so, '@N' will be replaced by a scan-number string
extracted from the source-file name.

<dest> may contain the directive '@<name>', where <name> is a valid
directory name that contains no path separators.  If so, the source
path is searched for a directory matching <name>.  If a match is found,
the match plus the rest of the source directory is used in place of the
directive.  For example, if the source directory is '/a/b/c', and <dest>
is '/x/@b/y', then translated files will be written to '/x/b/c/y'. This
allows (repeated execution of) tranFiles.py to maintain a directory
tree for translated files that parallels the directory tree for data
files.

<dest> may contain the directive '<name>@', which has the same effect as
'@<name>', except that <name> is not included in the dest directory.


Examples:
    python tranFiles.py @4idc1: ascii/tran mda2ascii mda
        The source directory will be gotten from the EPICS PVs
        4idc1:saveData_fileSystem and 4idc1:saveData_subDir; translated
        files will be written to <source dir>/ascii/tran_0123.txt.

    python tranFiles.py @4idc1: /home/@vxDir/tran.@N mda2ascii mda
        Same as above, but translated files will be written to
        /home/<source path from vxDir on>/tran.0123

"""

if __name__ == '__main__':
	if (len(sys.argv) > 1) and (sys.argv[1] == '-h'):
		print __doc__
		print usage_message
		sys.exit()
	if len(sys.argv) < 4:
		print usage_message
		sys.exit()
	sourceDir = sys.argv[1]
	destName = sys.argv[2]
	translate_command = sys.argv[3]
	if len(sys.argv) > 4:
		extension = sys.argv[4]
		if extension[0] != '.': extension = '.' + extension
	else:
		extension = '.mda'
	doTranFiles(sourceDir, destName, translate_command, extension)
