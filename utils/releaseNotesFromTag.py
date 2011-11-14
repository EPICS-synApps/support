#!/bin/env python
usage = """
usage:
    releaseNotesFromTag.py module [tag1 [tag2]]
        If tag1 and tag2 are supplied:
            do 'svn log -v' for 'module' from 'tag1' to 'tag2',
        If tag2 is omitted:
            use 'trunk' for tag2
        If tag1 is omitted:
            Use most recent tag for tag1
        Then convert log to html.
"""

import sys
import commands
import logModuleFromTag
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

#def highestTag(module, dir):
#	maxTag = -1
#	tagList = commands.getoutput("svn ls -v %s/%s/%s" % (SVN,module,dir)).split('\n')
#	for tag in tagList:
#		maxTag = max(maxTag, int(tag.split()[0]))
#	return maxTag

#def log(module, tag1, tag2=None):
#	# Find the difference between tag1 and tag2, or between tag1 and trunk
#	tagList = tags(module)
#	if not tag1 in tagList:
#		print("tag '%s' not found for module '%s'" % (tag1, module))
#		return
#	if tag2 == None:
#		tagRevNum = highestTag(module, 'tags/'+tag1)
#		trunkRevNum = highestTag(module, 'trunk')
#		l = commands.getoutput("svn log -v -r %d:%d %s/%s" % (tagRevNum, trunkRevNum, SVN, module))
#	else:
#		if not tag2 in tagList:
#			print("tag '%s' not found for module '%s'" % (tag2, module))
#			return
#		tag1RevNum = highestTag(module, 'tags/'+tag1)
#		tag2RevNum = highestTag(module, 'tags/'+tag2)
#		l = commands.getoutput("svn log -v -r %d:%d %s/%s" % (tag1RevNum, tag2RevNum, SVN, module))
#	l = l.split('\n')
#	return(l)

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
def printRevisionsHTML(revs, file=None, endTag=None, module=None):
	if file == None:
		fp = sys.stdout
	else:
		fp = open(file,'w')

	fp.write("<html>\n")
	fp.write("<body>\n")

	if module:
		fp.write("<h1 align=\"center\">%s Release Notes</h1>\n" % module)
	if endTag:
		if endTag[0] == 'R': endTag = endTag[1:]
		fp.write("<h2 align=\"center\">Release %s</h2>\n" % endTag)

	fp.write('<dl>\n')
	revList = []
	for key in revs.keys():
		revList.append(key)
	revList.sort()
	for key in revList:
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
		s = logModuleFromTag.log(sys.argv[1], sys.argv[2], sys.argv[3])
		revs = parseLog(s)
		printRevisionsHTML(revs,None,sys.argv[3])
	elif len(sys.argv) == 3:
		s=logModuleFromTag.log(sys.argv[1], sys.argv[2])
		revs = parseLog(s)
		printRevisionsHTML(revs)
	elif len(sys.argv) == 2:
		s=tags(sys.argv[1])
		for line in s: print(line)
	else:
		print (usage)
		return

if __name__ == "__main__":
	main()
