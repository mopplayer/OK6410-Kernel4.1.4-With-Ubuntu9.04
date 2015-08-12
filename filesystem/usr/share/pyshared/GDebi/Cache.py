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

import warnings
from warnings import warn
warnings.filterwarnings("ignore", "apt API not stable yet", FutureWarning)
import apt

class Cache(apt.Cache):
    """ helper to provide some additonal functions """

    def __init__(self, progress=None, rootdir=None, memonly=False):
        apt.Cache.__init__(self, progress, rootdir, memonly)
        if progress:
            self.op_progress = progress
        else:
            self.op_progress = apt.progress.OpProgress()

    def clear(self):
        """ unmark all pkgs """
        self._depcache.Init()

    def isVirtualPkg(self, pkgname):
        """ this function returns true if pkgname is a virtual
            pkg """
        try:
            virtual_pkg = self._cache[pkgname]
        except KeyError:
            return False

        if len(virtual_pkg.VersionList) == 0:
            return True
        return False

    def downloadable(self, pkg, useCandidate=True):
        " check if the given pkg can be downloaded "
        if useCandidate:
            ver = self._depcache.GetCandidateVer(pkg._pkg)
        else:
            ver = pkg._pkg.CurrentVer
        if ver == None:
            return False
        return ver.Downloadable

    def getProvidersFor(self, pkgname):
        """
        get providers for a pkgname, this is not limited to
        pure virtual packages
        """
        providers = []
        for pkg in self:
            v = self._depcache.GetCandidateVer(pkg._pkg)
            if v == None:
                continue
            for p in v.ProvidesList:
                #print virtual_pkg
                #print p[0]
                if pkgname == p[0]:
                    # we found a pkg that provides this virtual
                    # pkg, check if the proivdes is any good
                    providers.append(pkg)
                    #cand = self._cache[pkg.name]
                    #candver = self._cache._depcache.GetCandidateVer(cand._pkg)
                    #instver = cand._pkg.CurrentVer
                    #res = apt_pkg.CheckDep(candver.VerStr,oper,ver)
                    #if res == True:
                    #    self._dbg(1,"we can use %s" % pkg.name)
                    #    or_found = True
                    #    break
        return providers

    def getProvidersForVirtual(self, virtual_pkg):
        " get providers for a pure virtual package "
        providers = []
        try:
            vp = self._cache[virtual_pkg]
            if len(vp.VersionList) != 0:
                return providers
        except IndexError:
            return providers
        return self.getProvidersFor(virtual_pkg)

