<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>utilsReleaseNotes</title>
  <meta content="text/html; charset=ISO-8859-1" http-equiv="Content-Type" />
</head>
<body>

<P>tranFiles.py finds data files, translates them, and writes the
translated files to disk.  The program finds data files either in a
caller-specified directory, or by reading EPICS PVs (using a
caller-specified prefix string) and converting that information to a
directory name.  Files in the data-file directory whose names end with
a caller-specified file extension (default: '.mda') are considered
data files.

<P>If any data files are found, tranFiles.py translates them all, by
executing the caller-specified command &lt;tran_command&gt;, and (in the
simplest case) causes the translations to be written to files named
&lt;dest&gt;.NNNN, where &lt;dest&gt; is supplied, and 'NNNN' is extracted from
data-file names.  For example, the data file 'abc_1234.mda' will result
in the translated file &lt;dest&gt;.1234.  If the translated file
corresponding to a data file already exists, and has a 'modified' time
more recent than that of the data file, then the data file will be
ignored.

<P>&lt;dest&gt; may contain the directives '@&lt;element&gt;' or '@N' or both, as
described in the usage message:

<pre>
usage: python tranFiles.py source dest tran_command [extension]
where:
    source       the directory containing files to be translated.  If
                 &lt;source&gt; begins with '@', the rest of &lt;source&gt; is
                 used as the prefix of EPICS-PV names from which the
                 source directory is calculated.
    dest         the base name translated files will have.
    tran_command the full path of the file-translator program, which
                 must honor arguments specifying the output file to be
                 written as follows: 'program -o &lt;outputFile&gt;
                 inputFile'
    extension    the file extension by which data files will be
                 recognized.  If not specified, &lt;extension&gt; defaults
                 to '.mda'. If &lt;extension&gt; does not begin with '.',
                 '.' will be prepended to it.

If &lt;source&gt; begins with '@', the python executable that runs this
program should be capable of importing the ca_util module, which uses
caPython to read EPICS PVs.  If ca_util can't be imported, this
program will try to execute the command-line program, caget, instead.

&lt;dest&gt; tells this program how to name the text files it creates. If
&lt;dest&gt; contains any path information (e.g., 'ascii/base', as opposed
to simply 'base'), the path information will be used in one of two
ways:

    1) if &lt;dest&gt; begins with a '/', it completely specifies the
       directory in which text files will be written.
    2) otherwise, the path part of &lt;dest&gt; will be appended to the
       source directory.

&lt;dest&gt; may contain the directive '@N' in the filename, for example, as
'dirA/tran@N'.  If so, '@N' will be replaced by a scan-number string
extracted from the source-file name.

&lt;dest&gt; may contain the directive '@&lt;name&gt;', where &lt;name&gt; is a valid
directory name that contains no path separators.  If so, the source
path is searched for a directory matching &lt;name&gt;.  If a match is found,
the match plus the rest of the source directory is used in place of the
directive.  For example, if the source directory is '/a/b/c', and &lt;dest&gt;
is '/x/@b/y', then translated files will be written to '/x/b/c/y'. This
allows (repeated execution of) tranFiles.py to maintain a directory
tree for translated files that parallels the directory tree for data
files.

&lt;dest&gt; may contain the directive '&lt;name&gt;@', which has the same effect as
'@&lt;name&gt;', except that &lt;name&gt; is not included in the dest directory.


Examples:
    python tranFiles.py @4idc1: ascii/tran mda2ascii mda
        The source directory will be gotten from the EPICS PVs
        4idc1:saveData_fileSystem and 4idc1:saveData_subDir; translated
        files will be written to &lt;source dir&gt;/ascii/tran_0123.txt.

    python tranFiles.py @4idc1: /home/@vxDir/tran.@N mda2ascii mda
        Same as above, but translated files will be written to
        /home/&lt;source path from vxDir on&gt;/tran.0123

</pre>

</body>
</html>
