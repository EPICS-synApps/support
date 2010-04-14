#!/bin/env python
usage = """
usage:
    logModuleFromTag.py module tag1 [tag2]
        do 'svn log -v' for 'module' from 'tag1' to 'tag2',
        or to trunk if 'tag2' is omitted
"""

import sys
import commands
SVN="https://subversion.xor.aps.anl.gov/synApps"

def log(module, tag1, tag2=None):
	# Find the difference between tag1 and tag2, or between tag1 and trunk
	if tag2 == None:
		tagRevNum = int(commands.getoutput("svn ls -v %s/%s/tags/%s" % (SVN,module,tag1)).split()[0])
		trunkRevNum = int(commands.getoutput("svn ls -v %s/%s/trunk" % (SVN,module)).split()[0])
		log = commands.getoutput("svn log -v -r %d:%d %s/%s" % (tagRevNum, trunkRevNum, SVN, module))
	else:
		tag1RevNum = int(commands.getoutput("svn ls -v %s/%s/tags/%s" % (SVN,module,tag1)).split()[0])
		tag2RevNum = int(commands.getoutput("svn ls -v %s/%s/tags/%s" % (SVN,module,tag2)).split()[0])
		log = commands.getoutput("svn log -v -r %d:%d %s/%s" % (tag1RevNum, tag2RevNum, SVN, module))
	print(log)

def main():
	#print "sys.arvg:", sys.argv
	if len(sys.argv) == 4:
		log(sys.argv[1], sys.argv[2], sys.argv[3])
	elif len(sys.argv) == 3:
		log(sys.argv[1], sys.argv[2])
	else:
		print (usage)
		return

if __name__ == "__main__":
	main()
