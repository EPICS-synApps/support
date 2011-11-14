#!/bin/env python
usage = """
usage:
    logModuleFromTag.py module [tag1 [tag2]]
        If tag1 and tag2 are supplied:
            do 'svn log -v' for 'module' from 'tag1' to 'tag2',
        If tag2 is omitted:
            use 'trunk' for tag2
        If tag1 is omitted:
            Use most recent tag for tag1
"""

import sys
import commands
SVN="https://subversion.xor.aps.anl.gov/synApps"

def tags(module, verbose=False):
	"""
	Return tags for a module in the synApps repository.
	If verbose==False, return tags as a list; ['R1-0', 'R1-1']
	else, return tags as a dictionary of dictionaries:
	{'.': {'date': ('Mar', '30', '13:32'), 'rev': '10457', 'author': 'mooney'},
	 'R1-3': {'date': ('Mar', '30', '13:20'), 'rev': '10456', 'author': 'mooney'}}
	"""
	if verbose:
		tagListRaw = commands.getoutput("svn ls -v %s/%s/tags" % (SVN,module)).split('\n')
		tagDict = {}
		for tag in tagListRaw:
			(rev, author, month, day, year_time, tagName) = tag.split()
			tagDict[tagName.strip('/')] = {'rev':rev, 'author':author, 'date':(month, day, year_time)}
		return(tagDict)
	else:
		tagListRaw = commands.getoutput("svn ls %s/%s/tags" % (SVN,module)).split()
		tagList = []
		for tag in tagListRaw:
			tagList.append(tag.strip('/'))
		return(tagList)

def highestRevisionNum(module, dir):
	maxRev = -1
	maxTag = "None"
	revDate = "None"
	tagList = commands.getoutput("svn ls -v %s/%s/%s" % (SVN,module,dir)).split('\n')
	#print "tagList:", tagList
	for tag in tagList:
		words = tag.split()
		thisRev = int(words[0])
		thisTag = words[5]
		if (thisRev > maxRev) and (thisTag != "./"):
			maxTag = words[5][:-1] # strip trailing slash
			maxRev = thisRev
			revDate = " ".join(words[2:5])
	return (maxRev, maxTag, revDate)
		

def log(module, tag1=None, tag2=None):
	# Find the difference between tag1 and tag2, or between tag1 and trunk
	if tag2 == None:
		if tag1 == None:
			(tagRevNum, tag1, date1) = highestRevisionNum(module, 'tags')
			print "Most recent tag (revision) is %s (%d) on %s" % (tag1, tagRevNum, date1)
		else:
			reply = commands.getoutput("svn ls -v %s/%s/%s" % (SVN,module,'tags/'+tag1))
			tagList = reply.split('\n')
			words = tagList[0].split()
			try:
				(tagRevNum, date1) = (int(words[0]), " ".join(words[2:5]))
			except:
				print "* * * Error: '%s', using most recent tag instead\n" % reply
				(tagRevNum, tag1, date1) = highestRevisionNum(module, 'tags')
		(trunkRevNum, xx, date2) = highestRevisionNum(module, 'trunk')
		print "log from tag '%s' (%s on %s) to trunk (%s on %s)" % (tag1, tagRevNum, date1, trunkRevNum, date2)
		if (tagRevNum > trunkRevNum):
			l = "No changes"
		else:
			l = commands.getoutput("svn log -v -r %d:%d %s/%s" % (tagRevNum, trunkRevNum, SVN, module))
	else:
		(tag1RevNum, xx, date1) = highestRevisionNum(module, 'tags/'+tag1)
		(tag2RevNum, xx, date2) = highestRevisionNum(module, 'tags/'+tag2)
		print "log from tag '%s' (%s) to tag '%s' (%s)" % (tag1, date1, tag2, date2)
		l = commands.getoutput("svn log -v -r %d:%d %s/%s" % (tag1RevNum, tag2RevNum, SVN, module))
	l = l.split('\n')
	return(l)

typeName = {'A': 'Added',
      'C': 'Conflicted',
      'D': 'Deleted',
      'I': 'Ignored',
      'M': 'Modified',
      'R': 'Replaced',
      'X': 'unversioned external',
      '?': 'unknown',
      '!': 'missing'}

def parseLog(lines, debug=False):
	revisions = {}
	currRev = None
	section = None
	for l in lines:
		if debug>1: print("LINE='%s'" % l)
		if len(l) == 0:
			if debug>1: print('ignored')
			if section == 'files': section = 'message'
			continue
		if l[0] == '-' and l.strip('-') == '':
			if debug>1: print('separator')
			currRev = None
			section = None
			continue
		if currRev == None and l[0] == 'r':
			currRev = l.split()[0]
			if debug: print("revision:'%s'" % currRev)
			revisions[currRev] = {'files':[], 'message':[]}
			continue
		if currRev and l == 'Changed paths:':
			section = 'files'
			if debug>1: print('ignored')
			continue
		if currRev and (section == 'files') and l[0].isspace():
			(typeLetter,file) = l.lstrip(' ').split(' ', 1)
			type = typeName[typeLetter]
			if file.count(' '):
				file = file.split(' ',1)[0]
			if debug: print("    type ='%s', file = '%s'" % (type, file))
			revisions[currRev]['files'].append([type, file])
			continue
		if currRev and (section == 'message'):
			if debug: print("    commit message:'%s'" % l)
			revisions[currRev]['message'].append(l)
	return(revisions)

import os
def printRevisions(revs):
	for key in revs.keys():
		print(key)
		for f in revs[key]['files']:
			print("\t%s %s" % (f[0],os.path.basename(f[1])))
		for m in revs[key]['message']:
			print("\t%s" % m)

import sys
def printRevisionsHTML(revs,file=None):
	if file == None:
		fp = sys.stdout
	else:
		fp = open(file,'w')

	fp.write("<html>\n")
	fp.write("<body>\n")
	fp.write('<dl>\n')
	for key in revs.keys():
		if (len(revs[key]['message'])) > 0 and (
			revs[key]['message'][0][:39] == "This commit was manufactured by cvs2svn"):
			continue
		fp.write('\n<p><dt>')
		for f in revs[key]['files']:
			fp.write("%s %s<br>\n" % (f[0],os.path.basename(f[1])))
		fp.write('<dd>')
		for m in revs[key]['message']:
			fp.write("<br>%s\n" % m)
	fp.write('</dl>\n')
	fp.write("</body>\n")
	fp.write("</html>\n")
	fp.close()

def main():
	#print "sys.arvg:", sys.argv
	if len(sys.argv) == 4:
		s = log(sys.argv[1], sys.argv[2], sys.argv[3])
		for line in s: print(line)
	elif len(sys.argv) == 3:
		s=log(sys.argv[1], sys.argv[2])
		for line in s: print(line)
	elif len(sys.argv) == 2:
		s=log(sys.argv[1])
		for line in s: print(line)
#	elif len(sys.argv) == 2:
#		s=tags(sys.argv[1])
#		for line in s: print(line)
	else:
		print (usage)
		return

if __name__ == "__main__":
	main()
