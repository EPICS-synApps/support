#!/usr/bin/perl

use File::Copy;
use File::Spec;

sub searchFolder
{	
	my $collection = $_[0];
	my $cur = $_[1];
	my $ext = $_[2];
	
	my @subs = glob(File::Spec->catfile($cur, "*"));

	print"Searching: $cur\n";
	
	foreach my $file (@subs)
	{
		if (index($file, "all_adl") > -1)
		{
			next;
		}
		elsif (-d $file)
		{
			searchFolder($collection, $file, $ext);
		}
		elsif (index($file, ".$ext") == (length($file) - length($ext) - 1))
		{
			copy $file, $collection or die "File cannot be copied.";
		}
	}
}


my $argc = @ARGV;

if ( $argc < 2 || $argc > 2)
{
	print "usage: copyScreens top_dir file_ext\n";
	exit 2;
}

my $top_dir = $ARGV[0];
my $file_ext = $ARGV[1];
my $collection_dir = File::Spec->catdir($top_dir, "all_$file_ext");

mkdir $collection_dir;

searchFolder($collection_dir, $top_dir, $file_ext);
