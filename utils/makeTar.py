#!/bin/env python

import logModuleFromTag as log
import sys
import os
import commands
SVN="https://subversion.xray.aps.anl.gov/synApps"

usage = """
  makeTar [options] module [tag]
    If tag is supplied, make a tar file of that module/tag
    If tag is omitted, use most recent tag
"""

def main_old():
	#print "sys.arvg:", sys.argv
	if len(sys.argv) < 1:
		print (usage)
		return

	if len(sys.argv) > 1:
		module = sys.argv[1]
		reply = commands.getoutput("svn ls %s/%s/trunk" % (SVN,module)).split('\n')
		#print "reply='%s'" % reply
		if reply[0].find("non-existent") != -1:
			print "makeTar: module %s not found in repository" % module
			return
	if len(sys.argv) > 2:
		tag = sys.argv[2]
	else :
		(tagRevNum, tag, date) = log.highestRevisionNum(module, 'tags')

	allTags = log.tags(module, False)
	if not tag in allTags:
		print "makeTar: %s/%s not found in repository" % (module, tag)
		return
	ver = tag[1:]
	origDir = os.getcwd()
	tmpDir = commands.getoutput("mktemp -d work.XXX")
	os.chdir(tmpDir)
	commands.getoutput("svn export -q %s/%s/tags/%s %s-%s" % (SVN, module, tag, module, ver))
	commands.getoutput("tar cf ../%s_%s.tar %s-%s" % (module, tag, module, ver))
	os.chdir(origDir)
	commands.getoutput(" rm -rf %s" % tmpDir)

from optparse import OptionParser

def main():
	#print "sys.arvg:", sys.argv

	parser = OptionParser(usage=usage)
	parser.add_option("-d", "--directory", action="store_true", dest="keepDirectory",
		help="keep exported directory")
	parser.add_option("-z", "--zip", action="store_true", dest="zip",
		help="zip tar file")
	(options, args) = parser.parse_args()
	print "options=", options
	print "args=", args

	if len(args) < 1:
		parser.print_help()
		return
		
	if len(args) > 0:
		module = args[0]
		reply = commands.getoutput("svn ls %s/%s/trunk" % (SVN,module)).split('\n')
		#print "reply='%s'" % reply
		if reply[0].find("non-existent") != -1:
			print "makeTar: module %s not found in repository" % module
			return

	if len(args) > 1:
		tag = args[1]
	else :
		(tagRevNum, tag, date) = log.highestRevisionNum(module, 'tags')

	#print "makeTar: module='%s', tag='%s', keepDirectory=%s" % (module, tag, options.keepDirectory)

	allTags = log.tags(module, False)
	if not tag in allTags:
		print "makeTar: %s/%s not found in repository" % (module, tag)
		return
	ver = tag[1:]
	origDir = os.getcwd()
	if options.keepDirectory == None:
		tmpDir = commands.getoutput("mktemp -d work.XXX")
		os.chdir(tmpDir)
	commands.getoutput("svn export -q %s/%s/tags/%s %s-%s" % (SVN, module, tag, module, ver))
	commands.getoutput("tar cf %s_%s.tar %s-%s" % (module, tag, module, ver))
	if options.keepDirectory == None:
		commands.getoutput("mv %s_%s.tar .." % (module, tag))
		os.chdir(origDir)
		commands.getoutput("rm -rf %s" % tmpDir)
	if options.zip:
		commands.getoutput("gzip %s_%s.tar" % (module, tag))

if __name__ == "__main__":
	main()
