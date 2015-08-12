#! /usr/bin/perl
#
# update-rc.d	Update the links in /etc/rc[0-9S].d/
#

use strict;
use warnings;

my $initd = "/etc/init.d";
my $etcd  = "/etc/rc";
my $notreally = 0;

# Print usage message and die.

sub usage {
	print STDERR "update-rc.d: error: @_\n" if ($#_ >= 0);
	print STDERR <<EOF;
usage: update-rc.d [-n] [-f] <basename> remove
       update-rc.d [-n] <basename> defaults [NN | SS KK]
       update-rc.d [-n] <basename> start|stop NN runlvl [runlvl] [...] .
		-n: not really
		-f: force
EOF
	exit (1);
}

# Check out options.
my $force;

while($#ARGV >= 0 && ($_ = $ARGV[0]) =~ /^-/) {
	shift @ARGV;
	if (/^-n$/) { $notreally++; next }
	if (/^-f$/) { $force++; next }
	if (/^-h|--help$/) { &usage; }
	&usage("unknown option");
}

# Action.

&usage() if ($#ARGV < 1);
my $bn = shift @ARGV;

unless ($bn =~ m/[a-zA-Z0-9+.-]+/) {
    print STDERR "update-rc.d: illegal character in name '$bn'\n";
    exit (1);
}

if ($ARGV[0] ne 'remove') {
    if (! -f "$initd/$bn") {
	print STDERR "update-rc.d: $initd/$bn: file does not exist\n";
	exit (1);
    }
    &parse_lsb_header("$initd/$bn");
} elsif (-f "$initd/$bn") {
    if (!$force) {
	printf STDERR "update-rc.d: $initd/$bn exists during rc.d purge (use -f to force)\n";
	exit (1);
    }
}

my @startlinks;
my @stoplinks;

$_ = $ARGV[0];
if    (/^remove$/)       { &checklinks ("remove"); }
elsif (/^defaults$/)     { &defaults; &makelinks }
elsif (/^multiuser$/)    { &multiuser; &makelinks }
elsif (/^(start|stop)$/) { &startstop; &makelinks; }
else                     { &usage; }

exit (0);

# Check if there are links in /etc/rc[0-9S].d/ 
# Remove if the first argument is "remove" and the links 
# point to $bn.

sub is_link () {
    my ($op, $fn, $bn) = @_;
    if (! -l $fn) {
	print STDERR "update-rc.d: warning: $fn is not a symbolic link\n";
	return 0;
    } else {
	my $linkdst = readlink ($fn);
	if (! defined $linkdst) {
	    die ("update-rc.d: error reading symbolic link: $!\n");
	}
	if (($linkdst ne "../init.d/$bn") && ($linkdst ne "$initd/$bn")) {
	    print STDERR "update-rc.d: warning: $fn is not a link to ../init.d/$bn or $initd/$bn\n";
	    return 0;
	}
    }
    return 1;
}

sub checklinks {
    my ($i, $found, $fn, $islnk);

    print " Removing any system startup links for $initd/$bn ...\n"
	if (defined $_[0] && $_[0] eq 'remove');

    $found = 0;

    foreach $i (0..9, 'S') {
	unless (chdir ("$etcd$i.d")) {
	    next if ($i =~ m/^[789S]$/);
	    die("update-rc.d: chdir $etcd$i.d: $!\n");
	}
	opendir(DIR, ".");
	my $saveBN=$bn;
	$saveBN =~ s/\+/\\+/g;
	foreach $_ (readdir(DIR)) {
	    next unless (/^[SK]\d\d$saveBN$/);
	    $fn = "$etcd$i.d/$_";
	    $found = 1;
	    $islnk = &is_link ($_[0], $fn, $bn);
	    next unless (defined $_[0] and $_[0] eq 'remove');
	    if (! $islnk) {
		print "   $fn is not a link to ../init.d/$bn; not removing\n"; 
		next;
	    }
	    print "   $etcd$i.d/$_\n";
	    next if ($notreally);
	    unlink ("$etcd$i.d/$_") ||
		die("update-rc.d: unlink: $!\n");
	}
	closedir(DIR);
    }
    $found;
}

sub parse_lsb_header {
    my $initdscript = shift;
    my %lsbinfo;
    my $lsbheaders = "Provides|Required-Start|Required-Stop|Default-Start|Default-Stop";
    open(INIT, "<$initdscript") || die "error: unable to read $initdscript";
    while (<INIT>) {
        chomp;
        $lsbinfo{'found'} = 1 if (m/^\#\#\# BEGIN INIT INFO$/);
        last if (m/\#\#\# END INIT INFO$/);
        if (m/^\# ($lsbheaders):\s*(\S?.*)$/i) {
    	$lsbinfo{lc($1)} = $2;
        }
    }
    close(INIT);

    # Check that all the required headers are present
    if (!$lsbinfo{found}) {
	printf STDERR "update-rc.d: warning: $initdscript missing LSB information\n";
	printf STDERR "update-rc.d: see <http://wiki.debian.org/LSBInitScripts>\n";
    } else {
        for my $key (split(/\|/, lc($lsbheaders))) {
            if (!exists $lsbinfo{$key}) {
                print STDERR "update-rc.d: warning: $initdscript missing LSB keyword '$key'\n";
            }
        }
    }
}


# Process the arguments after the "defaults" keyword.

sub defaults {
    my ($start, $stop) = (20, 20);

    &usage ("defaults takes only one or two codenumbers") if ($#ARGV > 2);
    $start = $stop = $ARGV[1] if ($#ARGV >= 1);
    $stop  =         $ARGV[2] if ($#ARGV >= 2);
    &usage ("codenumber must be a number between 0 and 99")
	if ($start !~ /^\d\d?$/ || $stop  !~ /^\d\d?$/);

    $start = sprintf("%02d", $start);
    $stop  = sprintf("%02d", $stop);

    $stoplinks[$_]  = "K$stop"  for (0, 1, 6);
    $startlinks[$_] = "S$start" for (2, 3, 4, 5);

    1;
}

# Process the arguments after the "multiuser" keyword.

sub multiuser {
    my ($start, $stop) = (20, 20);

    print STDERR "update-rc.d: warning: multiuser is deprecated; specify runlevels manually\n";
    &usage ("multiuser takes only one or two codenumbers") if ($#ARGV > 2);
    $start = $stop = $ARGV[1] if ($#ARGV >= 1);
    $stop  =         $ARGV[2] if ($#ARGV >= 2);
    &usage ("codenumber must be a number between 0 and 99")
	if ($start !~ /^\d\d?$/ || $stop  !~ /^\d\d?$/);

    $start = sprintf("%02d", $start);
    $stop  = sprintf("%02d", $stop);

    $stoplinks[1] = "K$stop";
    $startlinks[2] = $startlinks[3] =
	$startlinks[4] = $startlinks[5] = "S$start";

    1;
}

# Process the arguments after the start or stop keyword.

sub startstop {

    my($letter, $NN, $level);

    while ($#ARGV >= 0) {
	if    ($ARGV[0] eq 'start') { $letter = 'S'; }
	elsif ($ARGV[0] eq 'stop')  { $letter = 'K' }
	else {
	    &usage("expected start|stop");
	}

	if ($ARGV[1] !~ /^\d\d?$/) {
	    &usage("expected NN after $ARGV[0]");
	}
	$NN = sprintf("%02d", $ARGV[1]);

	shift @ARGV; shift @ARGV;
	$level = shift @ARGV;
        &usage("action with list of runlevels not terminated by \".\"")
            if ($ARGV[$#ARGV] ne '.');
	do {
	    if ($level !~ m/^[0-9S]$/) {
		&usage(
		       "expected runlevel [0-9S] (did you forget \".\" ?)");
	    }
	    if (! -d "$etcd$level.d") {
		print STDERR
		    "update-rc.d: $etcd$level.d: no such directory\n";
		exit(1);
	    }
	    $level = 99 if ($level eq 'S');
	    $startlinks[$level] = "$letter$NN" if ($letter eq 'S');
	    $stoplinks[$level]  = "$letter$NN" if ($letter eq 'K');
	} while (($level = shift @ARGV) ne '.');
    }
    1;
}

# Create the links.

sub makelinks {
    my($t, $i);
    my @links;

    if (&checklinks) {
	print " System startup links for $initd/$bn already exist.\n";
	exit (0);
    }
    print " Adding system startup for $initd/$bn ...\n";

    # nice unreadable perl mess :)

    for($t = 0; $t < 2; $t++) {
	@links = $t ? @startlinks : @stoplinks;
	for($i = 0; $i <= $#links; $i++) {
	    my $lvl = $i;
	    $lvl = 'S' if ($i == 99);
	    next if (!defined $links[$i] or $links[$i] eq '');
	    print "   $etcd$lvl.d/$links[$i]$bn -> ../init.d/$bn\n";
	    next if ($notreally);
	    symlink("../init.d/$bn", "$etcd$lvl.d/$links[$i]$bn")
		|| die("update-rc.d: symlink: $!\n");
	}
    }

    1;
}
