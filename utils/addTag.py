#!/bin/env python
usage = """
usage:
    addTag.py module tag1 tag2
		
	For a module that already has a module tag, tag that same
	revision with another tag, for example, a synApps tag.

example:
	addTag.py areaDetector R1-6 synApps_5_5
"""
import sys
import commands
SVN="https://subversion.xray.aps.anl.gov/synApps"
import logModuleFromTag

def tag(module, tag1, tag2):
	(tag1RevNum, xx, date1) = logModuleFromTag.highestRevisionNum(module, 'tags/'+tag1)
	print module, tag1, "is revision", tag1RevNum, "date", date1
	cmd = 'svn cp -m "tag %s as %s" %s/%s/trunk@%s %s/%s/tags/%s' % (tag1, tag2, SVN, module, tag1RevNum, SVN, module, tag2)
	print cmd
	s = commands.getoutput(cmd)
	print s
	return

def main():
	#print "sys.arvg:", sys.argv
	if len(sys.argv) == 4:
		tag(sys.argv[1], sys.argv[2], sys.argv[3])
	else:
		print (usage)
		return

if __name__ == "__main__":
	main()
