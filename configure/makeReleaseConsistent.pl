# FILENAME...	makeReleaseConsistent.pl
#
# SYNOPSIS...	makeReleaseConsistent(supporttop_dir, epics_base_dir,
#				master_release, supporttop_dir)
#
# USAGE...      Take the version info. from the "master_release" file and
#	rewrite the <supporttop>/configure/RELEASE file macros, giving them
#	absolute pathnames and the correct support module versions.
#
# NOTES...
#	- Master release files MUST have a "_RELEASE" suffix.
#
# MODIFICATION LOG..
#  01/26/04 - Bug fix; no support for master files w/o macros.
#  04/09/04 - Support GATEWAY environment variable.
#  05/12/06 - Change permissions on updated RELEASE files to include group write
#             write access.
#  08/19/08 - master_config_dir argument changed to one "master_release" file.
#
# LOGIC...
=for block comments

Initialize $supporttop, $epics_base and $master_file from command line arguments.
Add $epics_base to the master macro list.
Add $GATEWAY to the master macro list.

Read the rest of the release files from the command line arguments.

Process $master_file for the master macro list.

FOR each release file.
    Open the release file.
    Set "rewrite release file" indicator to NO.
    Create temp file.
    WHILE master file lines left to process.
    	IF whitespace.
    	    Copy $line to temp file.
	ELSE
	    Parse input line for macro assignment.
	    IF macro found in master macro list.
    		Set "rewrite release file" indicator to YES.
		Copy macro to temp file using macro value from master list.
	    ELSE
		Copy $line to temp file.    
	    ENDIF
	ENDIF
    ENDWHILE

    Close temp and release files.
    IF "rewrite release file" indicator is YES.
	Copy temp file to release file.
    ENDIF
    Delete temp file.
ENDFOR
=cut
#
# Version:	$Revision: 1.1 $
# Modified By:	$Author: sluiter $
# Last Modified:$Date: 2008-08-26 18:09:18 $

# NOTE with Perl 5.6, replace the following with File::Temp.
use POSIX;
use File::Copy;
use Env;

$ritera = 0;
$supporttop = shift;
$epics_base = shift;
$master_file = shift;
$master_macro{"EPICS_BASE"} = $epics_base;

if ($ENV{GATEWAY} ne "")
{
    # Add GATEWAY to macro list.
    $master_macro{GATEWAY} = $ENV{GATEWAY};
}

while (@ARGV)
{
    $_ = $ARGV[0];
    shift @ARGV;
    $release_files[$ritera] = $_;
    $ritera++;
}

open(IN, "$master_file") or die "Cannot open $master_file\n";
while ($line = <IN>)
{
    next if ($line =~ /^(#|\s*\n)/);
    chomp($line);
    $_ = $line;
    $macro = /(.*)\s*=\s*\$\((.*)\)/;
    if ($macro eq "")
    {
	($prefix,$post) = /(.*)\s*=\s*(.*)/;
    }
    else
    {
	($prefix,$macro,$post) = /(.*)\s*=\s*\$\((.*)\)(.*)/;
    }
    if ($macro ne "" && $macro eq "SUPPORT")
    {
	$post = "\$(SUPPORT)" . $post;
    }
    if ($macro ne "" && $macro eq "GATEWAY")
    {
	$post = $master_macro{GATEWAY} . $post;
    }
    $master_macro{$prefix} = $post;
}
close(IN);

for ($itera = 0; $itera < $ritera; $itera++)
{
    open(IN, "$release_files[$itera]") or die "Cannot open $release_files[$itera]\n";
    $rewrite = 'NO';
    do
    {
	$tempfile = tmpnam();
    } until sysopen(TEMP, $tempfile, O_RDWR | O_CREAT | O_EXCL, 0600);

    while ($line = <IN>)
    {
	if ($line =~ /^(#|\s*\n)/)
	{
	    print TEMP $line;
	}
	else
	{
	    chomp($line);
	    $_ = $line;
	    ($prefix,$fullmacro,$macro,$post) = /(.*)\s*=\s*(\$\((.*)\))?(.*)?/;
	    $prefix =~ s/^\s+|\s+$//g; # strip leading and trailing whitespace.
	    if ($master_macro{$prefix} ne '' && $master_macro{$prefix} ne $post)
	    {
		$rewrite = 'YES';
		print TEMP "$prefix=$master_macro{$prefix}\n";
	    }
	    else
	    {
		print TEMP "$line\n";
	    }
	}
    }
    
    close(TEMP);
    close(IN);
    if ($rewrite eq 'YES')
    {
	chmod 0664, $release_files[$itera];
	copy($tempfile, $release_files[$itera]) or
	    die "copy failed for $release_files[$itera]: $!";
    }
    unlink $tempfile;
}
