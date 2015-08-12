package Gnome2::Install::Files;

$self = {
          'inc' => '-DORBIT2=1 -pthread -I/usr/include/libgnomeui-2.0 -I/usr/include/libart-2.0 -I/usr/include/gconf/2 -I/usr/include/gnome-keyring-1 -I/usr/include/libgnome-2.0 -I/usr/include/libbonoboui-2.0 -I/usr/include/libgnomecanvas-2.0 -I/usr/include/gtk-2.0 -I/usr/include/gnome-vfs-2.0 -I/usr/lib/gnome-vfs-2.0/include -I/usr/include/orbit-2.0 -I/usr/include/dbus-1.0 -I/usr/lib/dbus-1.0/include -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include -I/usr/include/libbonobo-2.0 -I/usr/include/bonobo-activation-2.0 -I/usr/include/libxml2 -I/usr/include/pango-1.0 -I/usr/include/gail-1.0 -I/usr/include/freetype2 -I/usr/include/atk-1.0 -I/usr/lib/gtk-2.0/include -I/usr/include/cairo -I/usr/include/pixman-1 -I/usr/include/libpng12   -DORBIT2=1 -pthread -I/usr/include/libbonoboui-2.0 -I/usr/include/orbit-2.0 -I/usr/include/libxml2 -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include -I/usr/include/libbonobo-2.0 -I/usr/include/libgnomecanvas-2.0 -I/usr/include/libgnome-2.0 -I/usr/include/bonobo-activation-2.0 -I/usr/include/pango-1.0 -I/usr/include/gail-1.0 -I/usr/include/libart-2.0 -I/usr/include/gtk-2.0 -I/usr/include/freetype2 -I/usr/include/atk-1.0 -I/usr/lib/gtk-2.0/include -I/usr/include/cairo -I/usr/include/pixman-1 -I/usr/include/libpng12 -I/usr/include/gconf/2 -I/usr/include/gnome-vfs-2.0 -I/usr/lib/gnome-vfs-2.0/include -I/usr/include/dbus-1.0 -I/usr/lib/dbus-1.0/include  ',
          'typemaps' => [
                          'gnome2perl.typemap',
                          'gnome.typemap'
                        ],
          'deps' => [
                      'Gnome2::Canvas',
                      'Glib',
                      'Gnome2::VFS',
                      'Gtk2',
                      'Cairo'
                    ],
          'libs' => '-pthread -lgnomeui-2 -lSM -lICE -lbonoboui-2 -lgnomevfs-2 -lgnomecanvas-2 -lgnome-2 -lpopt -lbonobo-2 -lbonobo-activation -lORBit-2 -lart_lgpl_2 -lgtk-x11-2.0 -lgdk-x11-2.0 -latk-1.0 -lpangoft2-1.0 -lgdk_pixbuf-2.0 -lm -lpangocairo-1.0 -lgio-2.0 -lcairo -lpango-1.0 -lfreetype -lz -lfontconfig -lgconf-2 -lgthread-2.0 -lrt -lgmodule-2.0 -lgobject-2.0 -lglib-2.0   -pthread -lbonoboui-2 -lgnomecanvas-2 -lgnome-2 -lpopt -lart_lgpl_2 -lgtk-x11-2.0 -lgdk-x11-2.0 -latk-1.0 -lpangoft2-1.0 -lgdk_pixbuf-2.0 -lm -lpangocairo-1.0 -lgio-2.0 -lcairo -lpango-1.0 -lfreetype -lz -lfontconfig -lbonobo-2 -lbonobo-activation -lgmodule-2.0 -lORBit-2 -lgthread-2.0 -lrt -lgobject-2.0 -lglib-2.0  '
        };


# this is for backwards compatiblity
@deps = @{ $self->{deps} };
@typemaps = @{ $self->{typemaps} };
$libs = $self->{libs};
$inc = $self->{inc};

	$CORE = undef;
	foreach (@INC) {
		if ( -f $_ . "/Gnome2/Install/Files.pm") {
			$CORE = $_ . "/Gnome2/Install/";
			last;
		}
	}

1;
