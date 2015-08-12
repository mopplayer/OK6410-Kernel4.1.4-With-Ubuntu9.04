#define VFS_MAJOR_VERSION (2)
#define VFS_MINOR_VERSION (24)
#define VFS_MICRO_VERSION (0)
#define VFS_CHECK_VERSION(major,minor,micro) \
	(VFS_MAJOR_VERSION > (major) || \
	 (VFS_MAJOR_VERSION == (major) && VFS_MINOR_VERSION > (minor)) || \
	 (VFS_MAJOR_VERSION == (major) && VFS_MINOR_VERSION == (minor) && VFS_MICRO_VERSION >= (micro)))
