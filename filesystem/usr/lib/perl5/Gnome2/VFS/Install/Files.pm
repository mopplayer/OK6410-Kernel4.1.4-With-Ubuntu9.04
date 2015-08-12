package Gnome2::VFS::Install::Files;

$self = {
          'inc' => '-pthread -DORBIT2=1 -I/usr/include/gnome-vfs-2.0 -I/usr/lib/gnome-vfs-2.0/include -I/usr/include/gconf/2 -I/usr/include/orbit-2.0 -I/usr/include/dbus-1.0 -I/usr/lib/dbus-1.0/include -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include   -I build',
          'typemaps' => [
                          'vfs2perl.typemap',
                          'vfs.typemap'
                        ],
          'deps' => [
                      'Glib'
                    ],
          'libs' => '-pthread -lgnomevfs-2 -lgconf-2 -lgthread-2.0 -lrt -lgmodule-2.0 -lgobject-2.0 -lglib-2.0  '
        };


# this is for backwards compatiblity
@deps = @{ $self->{deps} };
@typemaps = @{ $self->{typemaps} };
$libs = $self->{libs};
$inc = $self->{inc};

	$CORE = undef;
	foreach (@INC) {
		if ( -f $_ . "/Gnome2/VFS/Install/Files.pm") {
			$CORE = $_ . "/Gnome2/VFS/Install/";
			last;
		}
	}

1;
