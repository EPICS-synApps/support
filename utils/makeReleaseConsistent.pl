# FILENAME...	makeReleaseConsistent.pl
#
# SYNOPSIS...	makeReleaseConsistent(supporttop_dir, epics_base_dir,
#				master_config_dir, supporttop_dir)
#
# USAGE...      Take the version info. from <top>/config/*_RELEASE and
#	rewrite the <supporttop>/config/RELEASE file macros, giving them
#	absolute pathnames and the correct support module versions.
#
# NOTES...
#	- Master release files MUST have a "_RELEASE" suffix.
#
# LOGIC...
=for block comments

Initialize $supporttop and $epics_base from command line arguments.
Add $epics_base to the master macro list.

Assign remaining command line arguments to either the master or the release
    file list.

FOR each master file.
    Open the master file.
    WHILE master file lines left to process.
	Skip whitespace.
	Parse input line for macro assignment.
	IF SUPPORT macro found.
	    Prefix $supporttop to pathname.
	ENDIF
	Assign macro to master macro list.
    ENDWHILE
ENDFOR

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
# Version:	$Revision: 1.3 $
# Modified By:	$Author: sluiter $
# Last Modified:$Date: 2003-06-27 17:27:04 $

# NOTE with Perl 5.6, replace the following with File::Temp.
use POSIX;
use File::Copy;

$mitera = 0;
$ritera = 0;
$supporttop = shift;
$epics_base = shift;
$master_macro{"EPICS_BASE"} = $epics_base;


while (@ARGV)
{
    $_ = $ARGV[0];
    shift @ARGV;
    if (/_RELEASE$/)
    {
	$master_files[$mitera] = $_;
	$mitera++;
    }
    else
    {
	$release_files[$ritera] = $_;
	$ritera++;
    }
}


for ($itera = 0; $itera < $mitera; $itera++)
{
    open(IN, "$master_files[$itera]") or die "Cannot open $master_files[$itera]\n";
    while ($line = <IN>)
    {
	next if ($line =~ /^(#|\s*\n)/);
	chomp($line);
	$_ = $line;
	($prefix,$macro,$post) = /(.*)\s*=\s*\$\((.*)\)(.*)/;
	if ($macro ne "" && $macro eq "SUPPORT")
	{
	    $post = $supporttop . $post;
	}
	$master_macro{$prefix} = $post;
    }
    close(IN);
}

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
	copy($tempfile, $release_files[$itera]) or
	    die "copy failed for $release_files[$itera]: $!";
    }
    unlink $tempfile;
}
