#!/usr/bin/perl
# changePrefix for synApps 6.0

use Cwd;
use File::Copy;

sub doSed
{
	if ( @_ < 2 )
	{
		print "usage: doSed <sed script> filename\n";
		print 'example: doSed "s/tmm:/1bma:/g" stdApp.adl\n';
		exit;
    }
	
	my $sed_script = $_[0];
	my $filename = $_[1];
		
	`perl -pi -e '${sed_script}' ${filename}`
}

my $argc = @ARGV;

if ( $argc < 2 )
{
	print "usage: changePrefix old new\n";
	print "example: changePrefix xxx 1bma\n";
	exit 2;
}

my $old = $ARGV[0];
my $new = $ARGV[1];

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

my $top = cwd();

if ( -f "start_caQtDM_${old}" )
{
	printf "\r%-50s", "start_caQtDM_${new}";
	move "start_caQtDM_${old}", "start_caQtDM_${new}";
	doSed("s!/${old}!/${new}!g", "start_caQtDM_${new}");
	doSed("s/${old}.adl/${new}.adl/g", "start_caQtDM_${new}");
	doSed("s/=${old}:/=${new}:/g", "start_caQtDM_${new}");
	doSed("s/ioc${old}/ioc${new}/g", "start_caQtDM_${new}");
	doSed("s/${old}App/${new}App/g", "start_caQtDM_${new}");
	
	#chmod a+x
	my $permissions = ((stat("start_caQtDM_${new}"))[2] | oct("111"));
	chmod $permissions, "start_caQtDM_${new}";
}

if ( -f "start_MEDM_${old}" )
{
	printf "\r%-50s", "start_MEDM_${new}";
	move "start_MEDM_${old}", "start_MEDM_${new}";
	doSed("s!/${old}!/${new}!g", "start_MEDM_${new}");
	doSed("s/${old}.adl/${new}.adl/g", "start_MEDM_${new}");
	doSed("s/=${old}:/=${new}:/g", "start_MEDM_${new}");
	doSed("s/ioc${old}/ioc${new}/g", "start_MEDM_${new}");
	doSed("s/${old}App/${new}App/g", "start_MEDM_${new}");
	
	#chmod a+x
	my $permissions = ((stat("start_MEDM_${new}"))[2] | oct("111"));
	chmod $permissions, "start_MEDM_${new}";
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

foreach my $file (glob("*${old}*Include.dbd"))
{
	if ( -f $file )
	{
		doSed("/Include\\.dbd/s/${old}/${new}/g", $file);
		my $newfile=~s/$old/$new/g;
		move $file, $newfile;
	}
}

`perl -pi.bak -e "s/${old}(?!\\.dbd)/${new}/g" Makefile`;

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

foreach my $dir (glob("ioc*"))
{
	chdir $dir;
	
	foreach my $file (glob("*.cmd*"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", "$file";
			doSed("s!/${old}/!/${new}/!g", $file);
			doSed("s/${old}:/${new}:/g", $file);
			doSed("s/${old}\\./${new}./g", $file);
			doSed("s/ioc${old}/ioc${new}/g", $file);
			doSed("s/${old}Lib/${new}Lib/g", $file);
			doSed("s/${old}App/${new}App/g", $file);
			doSed("s/=${old}/=${new}/g", $file);
			#doSed("/dbLoadDatabase/s/${old}/${new}/g", $file);
			#doSed("/registerRecordDeviceDriver/s/${old}/${new}/g", $file);
			#doSed("/shellPromptSet/s/${old}/${new}/g", $file);
		}
	}
	
	foreach my $file (glob("examples/*.cmd*"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", "$file";
			doSed("s!/${old}/!/${new}/!g", $file);
			doSed("s/${old}:/${new}:/g", $file);
			doSed("s/${old}\\./${new}./g", $file);
			doSed("s/ioc${old}/ioc${new}/g", $file);
			doSed("s/${old}Lib/${new}Lib/g", $file);
			doSed("s/${old}App/${new}App/g", $file);
			doSed("s/=${old}/=${new}/g", $file);
			#doSed("/dbLoadDatabase/s/${old}/${new}/g", $file);
			#doSed("/registerRecordDeviceDriver/s/${old}/${new}/g", $file);
			#doSed("/shellPromptSet/s/${old}/${new}/g", $file);
		}
	}
	
	foreach my $file (glob("*.iocsh"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}:/${new}:/g", $file);
			doSed("s/${old}\\./${new}./g", $file);
			doSed("s/ioc${old}/ioc${new}/g", $file);
			doSed("s/${old}Lib/${new}Lib/g", $file);
			doSed("s/${old}App/${new}App/g", $file);
			doSed("s/=${old}/=${new}/g", $file);
			#doSed("/dbLoadDatabase/s/${old}/${new}/g", $file);
			#doSed("/registerRecordDeviceDriver/s/${old}/${new}/g", $file);
			#doSed("/shellPromptSet/s/${old}/${new}/g", $file);
		}
	}
	
	foreach my $file (glob("examples/*.iocsh"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}:/${new}:/g", $file);
			doSed("s/${old}\\./${new}./g", $file);
			doSed("s/ioc${old}/ioc${new}/g", $file);
			doSed("s/${old}Lib/${new}Lib/g", $file);
			doSed("s/${old}App/${new}App/g", $file);
			doSed("s/=${old}/=${new}/g", $file);
			#doSed("/dbLoadDatabase/s/${old}/${new}/g", $file);
			#doSed("/registerRecordDeviceDriver/s/${old}/${new}/g", $file);
			#doSed("/shellPromptSet/s/${old}/${new}/g", $file);
		}
	}
	
	foreach my $file (glob("auto*.req"))
	{
		printf "\r%-50s", $file;
		doSed("s/${old}:/${new}:/g", $file);
	}
	
	foreach my $file (glob("*.substitutions"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}/${new}/g", $file);
			doSed("s/${old}:/${new}:/g", $file);
			doSed("s/${old}App/${new}App/g", $file);
		}
	}
	
	foreach my $file (glob("substitutions/*.substitutions"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}/${new}/g", $file);
			doSed("s/${old}:/${new}:/g", $file);
			doSed("s/${old}App/${new}App/g", $file);
		}
	}
	
	foreach my $file (glob("*.template"))
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
	
	if ( -f "softioc/run" )
	{
		doSed("s/${old}/${new}/g", "softioc/run");
	}
	
	if ( -f "softioc/in-screen.sh" )
	{
		doSed("s/${old}/${new}/g", "softioc/in-screen.sh");
	}
	
	if ( -f "softioc/${old}.sh" )
	{
		doSed("s/${old}/${new}/g", "softioc/${old}.sh");
		move "softioc/${old}.sh", "softioc/${new}.sh";
	}
	
	chdir ".."
}

printf "\r%-50s", "${new}App/op/adl";
chdir "${top}/${new}App/op/adl";
move "${old}.adl", "${new}.adl";

foreach my $file (glob("*.adl"))
{
	printf "\r%-50s", $file;
	doSed("s/${old}:/${new}:/g", $file);
	doSed("s/=${old}/=${new}/g", $file);
	doSed("s/${old}App/${new}App/g", $file);
	doSed("s/${old}\\.adl/${new}.adl/g", $file);
}

chdir "${top}/${new}App/op";
if ( -d "./opi" )
{
	printf "\r%-50s", "${new}App/op/opi";
	chdir "opi";
	
	foreach my $file (glob("*.opi"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}/${new}/g", $file);
		}
	}
	
	foreach my $file (glob("autoconvert/*.opi"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}/${new}/g", $file);
		}
	}
}

chdir "${top}/${new}App/op";
if ( -d "./ui" )
{
	printf "\r%-50s", "${new}App/op/ui";
	chdir "ui";
	
	foreach my $file (glob("*.ui"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}/${new}/g", $file);
		}
	}
	
	foreach my $file (glob("autoconvert/*.ui"))
	{
		if ( -f $file )
		{
			printf "\r%-50s", $file;
			doSed("s/${old}/${new}/g", $file);
		}
	}
}

chdir "${top}/${new}App/op";
if ( -d "./burt" )
{
	printf "\r%-50s", "${new}App/op/burt";
	chdir "burt";
	foreach my $file (glob("*"))
	{
		printf "\r%-50s", $file;
		doSed("s/${old}/${new}/g", $file);
	}
}

chdir "${top}/${new}App/op";
if ( -d "./python" )
{
	printf "\r%-50s", "${new}App/op/python";
	chdir "python";


	if ( -f "macros_${old}.py" )
	{
		move "macros_${old}.py", "macros_${new}.py";
	}

	foreach my $file (glob("*"))
	{
		printf "\r%-50s", $file;
		doSed("s/${old}:/${new}:/g", $file);
	}
}

printf "\r%-50s\n", "Done.";
