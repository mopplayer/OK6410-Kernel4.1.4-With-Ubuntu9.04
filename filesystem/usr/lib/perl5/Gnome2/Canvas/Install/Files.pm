package Gnome2::Canvas::Install::Files;

$self = {
          'inc' => '-I/usr/include/libgnomecanvas-2.0 -I/usr/include/pango-1.0 -I/usr/include/gail-1.0 -I/usr/include/libart-2.0 -I/usr/include/gtk-2.0 -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include -I/usr/include/freetype2 -I/usr/include/atk-1.0 -I/usr/lib/gtk-2.0/include -I/usr/include/cairo -I/usr/include/pixman-1 -I/usr/include/libpng12  ',
          'typemaps' => [
                          'canvas.typemap',
                          'gnomecanvasperl.typemap'
                        ],
          'deps' => [
                      'Glib',
                      'Gtk2',
                      'Cairo'
                    ],
          'libs' => '-lgnomecanvas-2 -lart_lgpl_2 -lgtk-x11-2.0 -lgdk-x11-2.0 -latk-1.0 -lpangoft2-1.0 -lgdk_pixbuf-2.0 -lm -lpangocairo-1.0 -lgio-2.0 -lcairo -lpango-1.0 -lfreetype -lz -lfontconfig -lgobject-2.0 -lgmodule-2.0 -lglib-2.0  '
        };


# this is for backwards compatiblity
@deps = @{ $self->{deps} };
@typemaps = @{ $self->{typemaps} };
$libs = $self->{libs};
$inc = $self->{inc};

	$CORE = undef;
	foreach (@INC) {
		if ( -f $_ . "/Gnome2/Canvas/Install/Files.pm") {
			$CORE = $_ . "/Gnome2/Canvas/Install/";
			last;
		}
	}

1;
