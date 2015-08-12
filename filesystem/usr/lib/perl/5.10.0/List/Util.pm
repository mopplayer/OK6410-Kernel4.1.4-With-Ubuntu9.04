# List::Util.pm
#
# Copyright (c) 1997-2006 Graham Barr <gbarr@pobox.com>. All rights reserved.
# This program is free software; you can redistribute it and/or
# modify it under the same terms as Perl itself.

package List::Util;

use strict;
use vars qw(@ISA @EXPORT_OK $VERSION $XS_VERSION $TESTING_PERL_ONLY);
require Exporter;

@ISA        = qw(Exporter);
@EXPORT_OK  = qw(first min max minstr maxstr reduce sum shuffle);
$VERSION    = "1.19";
$XS_VERSION = $VERSION;
$VERSION    = eval $VERSION;

eval {
  # PERL_DL_NONLAZY must be false, or any errors in loading will just
  # cause the perl code to be tested
  local $ENV{PERL_DL_NONLAZY} = 0 if $ENV{PERL_DL_NONLAZY};
  eval {
    require XSLoader;
    XSLoader::load('List::Util', $XS_VERSION);
    1;
  } or do {
    require DynaLoader;
    local @ISA = qw(DynaLoader);
    bootstrap List::Util $XS_VERSION;
  };
} unless $TESTING_PERL_ONLY;

# This code is only compiled if the XS did not load
# of for perl < 5.6.0

if (!defined &reduce) {
eval <<'ESQ' 

sub reduce (&@) {
  my $code = shift;
  no strict 'refs';

  return shift unless @_ > 1;

  use vars qw($a $b);

  my $caller = caller;
  local(*{$caller."::a"}) = \my $a;
  local(*{$caller."::b"}) = \my $b;

  $a = shift;
  foreach (@_) {
    $b = $_;
    $a = &{$code}();
  }

  $a;
}

sub first (&@) {
  my $code = shift;

  foreach (@_) {
    return $_ if &{$code}();
  }

  undef;
}

ESQ
}

# This code is only compiled if the XS did not load
eval <<'ESQ' if !defined &sum;

use vars qw($a $b);

sub sum (@) { reduce { $a + $b } @_ }

sub min (@) { reduce { $a < $b ? $a : $b } @_ }

sub max (@) { reduce { $a > $b ? $a : $b } @_ }

sub minstr (@) { reduce { $a lt $b ? $a : $b } @_ }

sub maxstr (@) { reduce { $a gt $b ? $a : $b } @_ }

sub shuffle (@) {
  my @a=\(@_);
  my $n;
  my $i=@_;
  map {
    $n = rand($i--);
    (${$a[$n]}, $a[$n] = $a[$i])[0];
  } @_;
}

ESQ

1;

__END__

