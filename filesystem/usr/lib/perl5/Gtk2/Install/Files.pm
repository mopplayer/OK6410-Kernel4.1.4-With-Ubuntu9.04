package Gtk2::Install::Files;

$self = {
          'inc' => '-I/usr/include/gtk-2.0 -I/usr/lib/gtk-2.0/include -I/usr/include/atk-1.0 -I/usr/include/cairo -I/usr/include/pango-1.0 -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include -I/usr/include/pixman-1 -I/usr/include/freetype2 -I/usr/include/libpng12   -I./build ',
          'typemaps' => [
                          'gtk2perl.typemap',
                          'gdk.typemap',
                          'gtk.typemap',
                          'pango.typemap'
                        ],
          'deps' => [
                      'Glib',
                      'Cairo'
                    ],
          'libs' => '-lgtk-x11-2.0 -lgdk-x11-2.0 -latk-1.0 -lpangoft2-1.0 -lgdk_pixbuf-2.0 -lm -lpangocairo-1.0 -lgio-2.0 -lcairo -lpango-1.0 -lfreetype -lz -lfontconfig -lgobject-2.0 -lgmodule-2.0 -lglib-2.0  '
        };


# this is for backwards compatiblity
@deps = @{ $self->{deps} };
@typemaps = @{ $self->{typemaps} };
$libs = $self->{libs};
$inc = $self->{inc};

	$CORE = undef;
	foreach (@INC) {
		if ( -f $_ . "/Gtk2/Install/Files.pm") {
			$CORE = $_ . "/Gtk2/Install/";
			last;
		}
	}

1;
