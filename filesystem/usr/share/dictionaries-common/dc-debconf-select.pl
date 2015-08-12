# -------------------------------------------------------------------------------
# dc-debconf-select.pl:
#  This file will be added to end of dictionaries-common.config-base
#  to make dictionaries-common.config, as well as installed under
#  /usr/share/dictionaries-common for single ispell dicts/wordlists use
# -------------------------------------------------------------------------------

sub dico_get_packages (){
  # Get list of packages sharing the question
  my $class    = shift;
  my $question = "shared/packages-$class";

  my ($errorcode,$packages) = metaget ($question, "owners");
  return [ split (/\s*,\s*/, $packages) ] unless $errorcode;
}

sub dico_parse_languages (){
  # Get a hash reference of package -> list of (e)languages provided by package
  my $class    = shift;
  my $variant  = shift;
  my $packages = shift;
  my %tmphash  = ();

  die "No variant (languages|elanguages) string supplied\n" unless $variant;

  $packages = &dico_get_packages($class) unless $packages;

  foreach $pkg ( @$packages ){
    my ($errorcode, $entry ) = metaget("$pkg/$variant", "default");
    unless ( $errorcode ){
      $entry =~ s/^\s+//;
      $entry =~ s/\s+$//;
      $tmphash{$pkg} = $entry;
    }
  }
  return \%tmphash;
}

sub dico_get_all_choices (){
  # Get $choices and $echoices parallel lists sorted after $echoices and formatted for debconf
  my $class       = shift;
  my $languages   = shift;
  my $debug       = 1 if exists $ENV{'DICT_COMMON_DEBUG'};
  my %mappinghash = ();
  my $debug_prefix = "[dico_get_all_choices]";

  $languages   = &dico_parse_languages($class,"languages") unless $languages;

  my $elanguages  = &dico_parse_languages($class,"elanguages",[ keys %$languages ]);

  if ( $debug ){
    print STDERR "-------- $debug_prefix start --------\n";
    my $langlist  = join(', ',sort keys %{$languages});
    my $elanglist = join(', ',sort keys %{$elanguages});
    print STDERR " * Packages with languages: $langlist\n"  if $debug;
    print STDERR " * Packages with elanguages: $elanglist\n" if $debug;
  }

  foreach $pkg ( keys %$languages ){
    my @langs  = split(/\s*,\s*/, $languages->{$pkg});
    my @elangs = @langs;
    if ( exists $elanguages->{$pkg} ){
      my @tmp = split(/\s*,\s*/, $elanguages->{$pkg});
      if ( $debug ){
	print STDERR " langs: $#langs, "  . join(', ',@langs)  . "\n";
	print STDERR " tmp:   $#tmp, "    . join(', ',@tmp)    . "\n";
      }
      @elangs = @tmp if ( $#langs == $#tmp );
    }
    foreach $index ( 0 .. $#langs ){
      $mappinghash{$langs[$index]} = $elangs[$index];
    }
  }
  my $echoices = join(', ', sort {lc($a) cmp lc($b)} values %mappinghash);
  my $choices  = join(', ',
		      sort {lc($mappinghash{$a}) cmp lc($mappinghash{$b})}
		      keys %mappinghash);
  if ( $debug ){
    print STDERR "- Choices:\n[$choices]\n";
    print STDERR "- Echoices:\n[$echoices]\n";
    print STDERR "-------- $debug_prefix end --------\n";
  }
  return $choices, $echoices;
}

sub dc_debconf_select (){
  my $class       = shift;
  my $priority    = shift;
  my $question    = "dictionaries-common/default-$class";
  my $packages    = &dico_get_packages($class);
  my $debug       = 1 if exists $ENV{'DICT_COMMON_DEBUG'};
  my $reconfigure = 1 if exists $ENV{'DEBCONF_RECONFIGURE'};
  my $flagdir     = "/var/cache/dictionaries-common";
  my $newflag     = "$flagdir/flag-$class-new";
  my $echoices;
  my @oldchoices  = ();
  my %newchoices  = ();
  my %title       = ('ispell'   => "Dictionaries-common: Ispell dictionary",
		     'wordlist' => "Dictionaries-common: Wordlist dictionary"
		     );

  return unless $packages;

  # Get new base list of provided languages
  my $languages = &dico_parse_languages($class,"languages",$packages);
  foreach $pkg ( keys %$languages ) {
    foreach $lang ( split(/\s*,\s*/, $languages->{$pkg}) ){
      $newchoices{$lang}++;
    }
  }
  my $choices = join (', ', sort {lc($a) cmp lc($b)} keys %newchoices);

  # Read current value of default ispell dict / wordlist. No need to have
  # critical priority if is in the new list or set to manual. Otherwise
  # ask with critical priority, name for current value is changed or
  # something wrong happened.
  my $curval  = get ($question) || "undefined";
  unless ( $priority ){
    if ( $curval =~ /^Manual.*/ or exists $newchoices{$curval} ){
      $priority = "medium";     #
    } else {
      $priority = "medium"; # No good value, ask. Do not change!!
    }
  }

  # Get old list of provided languages
  @oldchoices = split(/\s*,\s*/,metaget ($question, "choices-c"));
  pop @oldchoices;            # Remove the manual entry
  my $oldchoices = join (', ', sort {lc($a) cmp lc($b)} @oldchoices);
  print STDERR
    "** dc_debconf_select: $class, $priority, $question\n" .
    "   new choices:[$choices]\n   old choices:[$oldchoices]\n" if $debug;

  # May ask question if there is no match
  if ( scalar %newchoices ) {
    if ( $choices ne $oldchoices) {
      fset ($question, "seen", "false");
      # Let future processes in this apt run know that a new $class element is to be installed
      if ( -d $flagdir ) {
	open ($FLAG,"> $newflag")
	  or die "Could not open $newflag for write. Aborting ...\n";
	print $FLAG "1\n";
	close $FLAG;
      }
    }
    my ( $errorcode, $seen ) = fget($question, "seen");
    if ( $seen eq "false" or $reconfigure ){
      ($choices, $echoices ) = &dico_get_all_choices($class,$languages);
      subst ($question, "choices", $choices);
      subst ($question, "echoices", $echoices);
    }
    input ($priority, $question);
    title ($title{$class});
    go ();
    subst ($question, "echoices", $choices); # Be backwards consistent
  }

  # If called from dictionaries-common.config, check actual values in debug mode
  if ( $debug && $fromdcconfig ){
    print STDERR "** dictionaries-common.config: Checking some real values for $question\n";
    print STDERR "   Real new Choices-C: " . metaget ($question, "choices-c") . "\n";
    print STDERR "   Real new value: "  . get ($question) . "\n";
    print STDERR "---\n";
  }
}

# Local Variables:
# perl-indent-level: 2
# End:

1;

