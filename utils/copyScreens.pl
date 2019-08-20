#!/usr/bin/perl

use File::Copy;
use File::Spec;

sub searchFolder
{	
	my $collection = $_[0];
	my $cur = $_[1];
	my @exts = @{ $_[2] };
	
	my @subs = glob(File::Spec->catfile($cur, "*"));

	print "Searching: $cur\n";
	
	foreach my $file (@subs)
	{
		if (index($file, "all_") > -1)
		{
			next;
		}
		elsif (-d $file)
		{
			searchFolder($collection, $file, \@exts);
		}
		else
		{
			foreach my $ext (@exts)
			{				
				if (index($file, ".$ext") == (length($file) - length($ext) - 1))
				{
					copy $file, $collection or die "File cannot be copied.";
				}
			}
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
my @file_exts = split(",", $ARGV[1]);

my $primary = $file_exts[0];
my $collection_dir = File::Spec->catdir($top_dir, "all_$primary");

mkdir $collection_dir;

searchFolder($collection_dir, $top_dir, \@file_exts);
