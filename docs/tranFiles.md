---
layout: default
title: tranFiles.py
nav_order: 6
---

tranFiles.py
============

tranFiles.py finds data files, translates them, and writes the translated files to disk. 
The program finds data files either in a caller-specified directory, or by reading EPICS PVs 
(using a caller-specified prefix string) and converting that information to a directory name. 
Files in the data-file directory whose names end with a caller-specified file extension 
(default: '.mda') are considered data files.

If any data files are found, tranFiles.py translates them all, by executing the caller-specified 
command \<tran\_command\>, and (in the simplest case) causes the translations to be written to 
files named \<dest\>.NNNN, where \<dest\> is supplied, and 'NNNN' is extracted from data-file 
names. For example, the data file 'abc\_1234.mda' will result in the translated file \<dest\>.1234. 
If the translated file corresponding to a data file already exists, and has a 'modified' time more 
recent than that of the data file, then the data file will be ignored.

\<dest\> may contain the directives '@\<element\>' or '@N' or both, as described in the usage message:

```
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

```
                    
If \<source\> begins with '@', the python executable that runs this
program should be capable of importing the ca\_util module, which uses
caPython to read EPICS PVs.  If ca\_util can't be imported, this
program will try to execute the command-line program, caget, instead.

\<dest\> tells this program how to name the text files it creates. If
\<dest\> contains any path information (e.g., 'ascii/base', as opposed
to simply 'base'), the path information will be used in one of two
ways:

* if <dest> begins with a '/', it completely specifies the
  directory in which text files will be written.
* otherwise, the path part of <dest> will be appended to the
  source directory.

\<dest\> may contain the directive '@N' in the filename, for example, as
'dirA/tran@N'.  If so, '@N' will be replaced by a scan-number string
extracted from the source-file name.

\<dest\> may contain the directive '@\<name\>', where \<name\> is a valid
directory name that contains no path separators.  If so, the source
path is searched for a directory matching \<name\>.  If a match is found,
the match plus the rest of the source directory is used in place of the
directive.  For example, if the source directory is '/a/b/c', and <dest>
is '/x/@b/y', then translated files will be written to '/x/b/c/y'. This
allows (repeated execution of) tranFiles.py to maintain a directory
tree for translated files that parallels the directory tree for data
files.

\<dest\> may contain the directive '\<name\>@', which has the same effect as
'@\<name\>', except that \<name\> is not included in the dest directory.

```
Examples:
    python tranFiles.py @4idc1: ascii/tran mda2ascii mda
        The source directory will be gotten from the EPICS PVs
        4idc1:saveData_fileSystem and 4idc1:saveData_subDir; translated
        files will be written to <source dir>/ascii/tran_0123.txt.

    python tranFiles.py @4idc1: /home/@vxDir/tran.@N mda2ascii mda
        Same as above, but translated files will be written to
        /home/<source path from vxDir on>/tran.0123

```
