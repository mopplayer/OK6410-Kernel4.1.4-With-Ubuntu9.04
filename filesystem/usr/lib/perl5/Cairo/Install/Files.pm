package Cairo::Install::Files;

$self = {
          'inc' => '-I. -Ibuild -I/usr/include/cairo -I/usr/include/pixman-1 -I/usr/include/freetype2 -I/usr/include/libpng12   -I/usr/include/cairo -I/usr/include/freetype2 -I/usr/include/pixman-1 -I/usr/include/libpng12  ',
          'typemaps' => [
                          'cairo-perl-auto.typemap',
                          'cairo-perl.typemap'
                        ],
          'deps' => [],
          'libs' => '-lcairo   -lcairo -lfreetype -lz -lfontconfig  '
        };


# this is for backwards compatiblity
@deps = @{ $self->{deps} };
@typemaps = @{ $self->{typemaps} };
$libs = $self->{libs};
$inc = $self->{inc};

	$CORE = undef;
	foreach (@INC) {
		if ( -f $_ . "/Cairo/Install/Files.pm") {
			$CORE = $_ . "/Cairo/Install/";
			last;
		}
	}

1;
