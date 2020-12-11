#!/usr/bin/perl

my $argc = @ARGV;

# Inputs are 1) path to convertRelease.pl, 2) path to module, 3) Macro name of module, 4) list of modules to build against

my $convertrelease = $ARGV[0];
my $dir = $ARGV[1];
my $module = $ARGV[2];
my $module_list = $ARGV[3];

if ( ! -e "${dir}/configure/RELEASE" )
{
	print "";
	exit;
}

# Parse the configure file
my $data = `perl ${convertrelease} -T ${dir} releaseTops`;
$data =~ s/\r//g;
$data =~ s/\n//g;

my @list = split / /, $data;

my @modules = split / /, $module_list;
my %modcheck = map { $_ => 1 } @modules;

# Modules shouldn't depend on themselves
delete($modcheck{$module});

my $output = "";

foreach my $test (@list)
{
	
	# Only match against the list of modules given
	if (exists($modcheck{$test}))
	{		
		# Put $() around the macros
		$output = $output . "\$\($test\) ";
	}
}

print ${output};
