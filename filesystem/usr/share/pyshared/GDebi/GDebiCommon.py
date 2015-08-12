#!/usr/bin/env python
# Copyright (c) 2005-2009 Canonical Ltd
#
# AUTHOR:
# Michael Vogt <mvo@ubuntu.com>
#
# This file is part of GDebi
#
# GDebi is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# GDebi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GDebi; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


import sys
import os
import string
import warnings
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)
from mimetypes import guess_type

import apt
import apt_pkg

from DebPackage import DebPackage, Cache
import gettext

def _(str):
    return utf8(gettext.gettext(str))

def utf8(str):
    if isinstance(str, unicode):
        return str
    try:
        return unicode(str, 'UTF-8')
    except:
        # assume latin1 as fallback
        return unicode(str, 'latin1')
	  
class GDebiCommon(object):
    # cprogress may be different in child classes
    def __init__(self, datadir, options, file=""):
        self.cprogress = None
        self.deps = ""
        self.version_info_title = ""
        self.version_info_msg = ""
        self._deb = None
     	self._options = options
        self.install = []
        self.remove = []
        self.unauthenticated = 0

    def openCache(self):
        self._cache = Cache(self.cprogress)
        if self._cache._depcache.BrokenCount > 0:
                self.error_header = _("Broken dependencies")
                self.error_body = _("Your system has broken dependencies. "
                             "This application can not continue until "
                             "this is fixed. "
                             "To fix it run 'gksudo synaptic' or "
                             "'sudo apt-get install -f' "
                             "in a terminal window.")
		return False
        return True

    def open(self, file):
        # open the package
        try:
            self._deb = DebPackage(self._cache, file)
        except (IOError,SystemError),e:
            mimetype=guess_type(file)
            if (mimetype[0] != None and 
                mimetype[0] != "application/x-debian-package"):
                self.error_header = _("'%s' is not a Debian package") % os.path.basename(file)
                self.error_body = _("The MIME type of this file is '%s' "
                             "and can not be installed on this system.") % mimetype[0]
                return False    
            else:
                self.error_header = _("Could not open '%s'") % os.path.basename(file)
                self.error_body = _("The package might be corrupted or you are not "
                             "allowed to open the file. Check the permissions "
                             "of the file.")
                return False

    def compareDebWithCache(self):
        # check if the package is available in the normal sources as well
        res = self._deb.compareToVersionInCache(useInstalled=False)
        if not self._options.non_interactive and res != DebPackage.NO_VERSION:
            pkg = self._cache[self._deb.pkgName]
            
            # FIXME: make this strs better, improve the dialog by
            # providing a option to install from repository directly
            # (when possible)
            if res == DebPackage.VERSION_SAME:
                if self._cache.downloadable(pkg,useCandidate=True):
                    self.version_info_title = _("Same version is available in a software channel")
                    self.version_info_msg = _("You are recommended to install the software "
                            "from the channel instead.")
            elif res == DebPackage.VERSION_IS_NEWER:
                if self._cache.downloadable(pkg,useCandidate=True):
                    self.version_info_title = _("An older version is available in a software channel")
                    self.version_info_msg = _("Generally you are recommended to install "
                            "the version from the software channel, since "
                            "it is usually better supported.")
            elif res == DebPackage.VERSION_OUTDATED:
                if self._cache.downloadable(pkg,useCandidate=True):
                    self.version_info_title = _("A later version is available in a software "
                              "channel")
                    self.version_info_msg = _("You are strongly advised to install "
                            "the version from the software channel, since "
                            "it is usually better supported.")

    def getChanges(self):
        (self.install, self.remove, self.unauthenticated) = self._deb.requiredChanges
        self.deps = ""
        if len(self.remove) == len(self.install) == 0:
            self.deps = _("All dependencies are satisfied")
        if len(self.remove) > 0:
            # FIXME: use ngettext here
            self.deps += _("Requires the <b>removal</b> of %s packages\n") % len(self.remove)
        if len(self.install) > 0:
            self.deps += _("Requires the installation of %s packages") % len(self.install)
        return True

    def try_acquire_lock(self):
        " check if we can lock the apt database "
        try:
            apt_pkg.PkgSystemLock()
        except SystemError:
            self.error_header = _("Only one software management tool is allowed to"
                       " run at the same time")
            self.error_body = _("Please close the other application e.g. 'Update "
                     "Manager', 'aptitude' or 'Synaptic' first.")
            return False
        apt_pkg.PkgSystemUnLock()
        return True

    def acquire_lock(self):
        " lock the pkgsystem for install "
        # sanity check ( moved here )
        if self._deb is None:
          return False

        # check if we can lock the apt database
        try:
            apt_pkg.PkgSystemLock()
        except SystemError:
            self.error_header = _("Only one software management tool is allowed to"
                                  " run at the same time")
            self.error_body = _("Please close the other application e.g. 'Update "
                                "Manager', 'aptitude' or 'Synaptic' first.")
            return False
        return True

    def release_lock(self):
        " release the pkgsystem lock "
        apt_pkg.PkgSystemLock()
        return True
    
