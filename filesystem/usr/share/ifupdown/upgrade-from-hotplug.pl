#!/usr/bin/perl -w

use strict;

my %doneifaces = ();
my @orig = ();   # original interfaces file
my $line;

while($line = <STDIN>) {
	if ($line =~ m/^\s*#/) {
		push @orig, $line;
		next;
	}

	my $tmp;
	while ($line =~ m/\\\n$/ and $tmp = <>) {
		$line .= $tmp;
	}
	push @orig, $line;
}

my @autos = ();
sub upgrade
{
	my $block = shift;
	$block =~ s/^(\s*)//s;
	my $pre = $1;

	$block =~ s/(\s*)$//s;
	my $post = $1;
	$post = $1 . $post while $block =~ s/(\s*\n\#[^\n]*)$//s;

	my $out = "";
	if ($block =~ m/^mapping\s+hotplug\b/) {
		while ($block =~ m/^\s*map\s+(\S+)/mg) {
			unless (grep { $_ eq $1 } @autos) {
				$out .= "auto $1\n";
				push @autos, $1;
			}
		}
		$out =~ s/\n$//;
	} elsif ($block =~ m/^auto\b/) {
		$block =~ s/^auto\b//;
		$pre .= "auto";
	
		while ($block =~ m/\s*(\S+)/sg) {
			unless (grep { $_ eq $1 } @autos) {
				$out .= " $1";
				push @autos, $1;
			}
		}

		return "" unless length $out;
	} else {
		$out = $block;
	}

	return $pre . $out . $post;
}

my $out = "";
my $block = "";
for my $x (@orig) {
	my $y = $x;
	$y =~ s/^\s*//s;
	$y =~ s/\\\n//sg;
	$y =~ s/\s*$//s;

	if ($y =~ m/^(iface|auto|allow-\W+|mapping)\b/) {
		$out .= upgrade $block;
		$block = $x;
	} else {
		$block .= $x;
	}
}

$out .= upgrade $block;

print $out;
