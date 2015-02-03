#!/usr/bin/perl
# changePrefix for synApps 5.8

use Cwd;
use File::Copy 'move';

sub doSed
{
	if ( @_ < 2 )
	{
		print "usage: doSed <sed script> filename\n";
		print 'example: doSed "s/tmm:/1bma:/g" stdApp.adl\n';
		exit;
    }
	
	$sed_script = $_[0];
	$filename = $_[1];
	
	unlink "${filename}~";
	unlink "${filename}%";
	move $filename, "${filename}~";
	`sed ${sed_script} ${filename}~ >${filename}`;
	unlink "${filename}~";
}

$argc = @ARGV;

if ( $argc < 2 )
{
	print "usage: changePrefix old new\n";
	print "example: changePrefix xxx 1bma\n";
	exit 2;
}

$old = $ARGV[0];
$new = $ARGV[1];

if ( ! -d "${old}App" )
{
	print "changePrefix: ${old}App not found. Nothing done.\n";
	exit 2;
}

if ( ! -d "iocBoot" )
{
	print "changePrefix: iocBoot not found. Nothing done.\n";
	exit 2;
}

$top = cwd();

if ( -f "start_epics_${old}" )
{
	printf "\r%-50s", "start_epics_${new}";
	move "start_epics_${old}", "start_epics_${new}";
	doSed("s!/${old}!/${new}!g", "start_epics_${new}");
	doSed("s/${old}.adl/${new}.adl/g", "start_epics_${new}");
	doSed("s/=${old}:/=${new}:/g", "start_epics_${new}");
	doSed("s/ioc${old}/ioc${new}/g", "start_epics_${new}");
	doSed("s/${old}App/${new}App/g", "start_epics_${new}");
	
	#chmod a+x
	$permissions = ((stat("start_epics_${new}"))[2] | oct("111"));
	chmod $permissions, "start_epics_${new}";
}

if ( -f "start_epics_${old}.bash" )
{
	printf "\r%-50s", "start_epics_${new}.bash";
	move "start_epics_${old}.bash", "start_epics_${new}.bash";
	doSed("s!/${old}!/${new}!g", "start_epics_${new}.bash");
	doSed("s/${old}.adl/${new}.adl/g", "start_epics_${new}.bash");
	doSed("s/=${old}:/=${new}:/g", "start_epics_${new}.bash");
	doSed("s/ioc${old}/ioc${new}/g", "start_epics_${new}.bash");
	doSed("s/${old}App/${new}App/g", "start_epics_${new}.bash");
	
	#chmod a+x
	$permissions = ((stat("start_epics_${new}.bash"))[2] | oct("111"));
	chmod $permissions, "start_epics_${new}.bash";
}

if ( -f "setup_epics_common" )
{
	printf "\r%-50s", "setup_epics_common";
	doSed("s!/${old}!/${new}!g", "setup_epics_common");
	doSed("s/${old}App/${new}App/g", "setup_epics_common");
}

printf "\r%-50s", "${new}App/src";
move "${old}App", "${new}App";
chdir "${new}App/src";

if ( -f "${old}Main.c" )
{
	move "${old}Main.c", "${new}Main.c";
	doSed("s/${old}/${new}/g", "${new}Main.c");
}

if ( -f "${old}Main.cpp" )
{
	move "${old}Main.cpp", "${new}Main.cpp";
	doSed("s/${old}/${new}/g", "${new}Main.cpp");
}

if ( -f "${old}Support.dbd" )
{
	move "${old}Support.dbd", "${new}Support.dbd";
}

foreach $file (glob("*${old}*Include.dbd"))
{
	if ( -f $file )
	{
		doSed("/Include\.dbd/s/${old}/${new}/g", $file);
		$newfile=~s/$old/$new/g;
		move $file, $newfile;
	}
}

`perl -pi.bak -e "s/${old}(?!\.dbd)/${new}/g" Makefile`;

if (-f "Makefile.bak" )
{
	unlink("Makefile.bak");
}

printf "\r%-50s", "${new}App/Db";
chdir "${top}/${new}App/Db";
doSed("s/${old}.dbd/${new}.dbd/g", "Makefile");
doSed("s/${old}.template/${new}.template/g", "Makefile");
doSed("s/${old}Include/${new}Include/g", "Makefile");
doSed("s/${old}/${new}/g", "Makefile");

printf "\r%-50s", "iocBoot/";
chdir "${top}/iocBoot";

if (-d "ioc${old}" )
{
	move "ioc${old}", "ioc${new}";
}

foreach $dir (glob("ioc*"))
{
	chdir $dir;
	
	foreach $file (glob("*.cmd*"))
	{
		printf "\r%-50s", "$file";
		doSed("s!/${old}/!/${new}/!g", $file);
		doSed("s/${old}:/${new}:/g", $file);
		doSed("s/${old}\./${new}./g", $file);
		doSed("s/ioc${old}/ioc${new}/g", $file);
		doSed("s/${old}Lib/${new}Lib/g", $file);
		doSed("s/${old}App/${new}App/g", $file);
		doSed("s/=${old}/=${new}/g", $file);
		doSed("/dbLoadDatabase/s/${old}/${new}/g", $file);
		doSed("/registerRecordDeviceDriver/s/${old}/${new}/g", $file);
		doSed("/shellPromptSet/s/${old}/${new}/g", $file);
	}
	
	foreach $file (glob("*.iocsh"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}:/${new}:/g", $file);
			doSed("s/${old}\./${new}./g", $file);
			doSed("s/ioc${old}/ioc${new}/g", $file);
			doSed("s/${old}Lib/${new}Lib/g", $file);
			doSed("s/${old}App/${new}App/g", $file);
			doSed("s/=${old}/=${new}/g", $file);
			doSed("/dbLoadDatabase/s/${old}/${new}/g", $file);
			doSed("/registerRecordDeviceDriver/s/${old}/${new}/g", $file);
			doSed("/shellPromptSet/s/${old}/${new}/g", $file);
		}
	}
	
	foreach $file (glob("auto*.req"))
	{
		printf "\r%-50s", $file;
		doSed("s/${old}:/${new}:/g", $file);
	}
	
	foreach $file (glob("*.substitutions"))
	{
		printf "\r%-50s", $file;
		doSed("s/${old}/${new}/g", $file);
		doSed("s/${old}:/${new}:/g", $file);
		doSed("s/${old}App/${new}App/g", $file);
	}
	
	foreach $file (glob("*.template"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}:/${new}:/g", $file);
		}
	}
	
	if ( -f "interp.sav" )
	{
		doSed("s/${old}/${new}/g", "interp.sav");
	}
	
	if ( -f "bootParms" )
	{
		doSed("s!/${old}/!/${new}/!g", "bootParms");
		doSed("s/ioc${old}/ioc${new}/g", "bootParms");
	}
	
	if ( -f "run" )
	{
		doSed("s/${old}/${new}/g", "run");
	}
	
	if ( -f "in-screen.sh" )
	{
		doSed("s/${old}/${new}/g", "in-screen.sh");
	}
	
	if ( -f "${old}.sh" )
	{
		doSed("s/${old}/${new}/g", "${old}.sh");
		move "${old}.sh", "${new}.sh";
	}
	
	chdir ".."
}

printf "\r%-50s", "${new}App/op/adl";
chdir "${top}/${new}App/op/adl";
move "${old}.adl", "${new}.adl";

foreach $file (glob("*.adl"))
{
	printf "\r%-50s", $file;
	doSed("s/${old}:/${new}:/g", $file);
	doSed("s/=${old}/=${new}/g", $file);
	doSed("s/${old}App/${new}App/g", $file);
	doSed("s/${old}\.adl/${new}.adl/g", $file);
}

chdir "${top}/${new}App/op";
if ( -d "./opi" )
{
	printf "\r%-50s", "${new}App/op/opi";
	chdir "opi";
	foreach $file (glob("*.opi"))
	{
		printf "\r%-50s", $file;
		doSed("s/${old}/${new}/g", $file);
	}
}

chdir "${top}/${new}App/op";
if ( -d "./ui" )
{
	printf "\r%-50s", "${new}App/op/ui";
	chdir "ui";
	foreach $file (glob("*.ui"))
	{
		printf "\r%-50s", $file;
		doSed("s/${old}/${new}/g", $file);
	}
}

chdir "${top}/${new}App/op";
if ( -d "./burt" )
{
	printf "\r%-50s", "${new}App/op/burt";
	chdir "burt";
	foreach $file (glob("*"))
	{
		printf "\r%-50s", $file;
		doSed("s/${old}/${new}/g", $file);
	}
}

printf "\r%-50s\n", "Done.";
