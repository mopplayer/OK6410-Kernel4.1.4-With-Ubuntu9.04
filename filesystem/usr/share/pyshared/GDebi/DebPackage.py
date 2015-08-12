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
import apt_inst, apt_pkg
import apt
import sys
import os
from gettext import gettext as _
from Cache import Cache

class DebPackage(object):
    debug = 0

    def __init__(self, cache, file=None):
        cache.clear()
        self._cache = cache
        self.file = file
        self._needPkgs = []
        self._sections = {}
        self._installedConflicts = set()
        self._failureString = ""
        if file != None:
            self.open(file)
            
    def open(self, file):
        """ read a deb """
        control = apt_inst.debExtractControl(open(file))
        self._sections = apt_pkg.ParseSection(control)
        self.pkgName = self._sections["Package"]

    def _isOrGroupSatisfied(self, or_group):
        """ this function gets a 'or_group' and analyzes if
            at least one dependency of this group is already satisfied """
        self._dbg(2,"_checkOrGroup(): %s " % (or_group))

        for dep in or_group:
            depname = dep[0]
            ver = dep[1]
            oper = dep[2]

            # check for virtual pkgs
            if not self._cache.has_key(depname):
                if self._cache.isVirtualPkg(depname):
                    self._dbg(3,"_isOrGroupSatisfied(): %s is virtual dep" % depname)
                    for pkg in self._cache.getProvidersForVirtual(depname):
                        if pkg.isInstalled:
                            return True
                continue
            # check real dependency
            inst = self._cache[depname]
            instver = inst.installedVersion
            if instver != None and apt_pkg.CheckDep(instver,oper,ver) == True:
                return True
            # if no real dependency is installed, check if there is
            # a package installed that provides this dependency
            # (e.g. scrollkeeper dependecies are provided by rarian-compat)
            for ppkg in self._cache.getProvidersFor(depname):
                if ppkg.isInstalled:
                    self._dbg(3, "found installed '%s' that provides '%s'" % (ppkg.name, depname))
                    return True
        return False
            

    def _satisfyOrGroup(self, or_group):
        """ try to satisfy the or_group """

        or_found = False
        virtual_pkg = None

        for dep in or_group:
            depname = dep[0]
            ver = dep[1]
            oper = dep[2]

            # if we don't have it in the cache, it may be virtual
            if not self._cache.has_key(depname):
                if not self._cache.isVirtualPkg(depname):
                    continue
                providers = self._cache.getProvidersForVirtual(depname)
                # if a package just has a single virtual provider, we
                # just pick that (just like apt)
                if len(providers) != 1:
                    continue
                depname = providers[0].name
                
            # now check if we can satisfy the deps with the candidate(s)
            # in the cache
            cand = self._cache[depname]
            candver = self._cache._depcache.GetCandidateVer(cand._pkg)
            if not candver:
                continue
            if not apt_pkg.CheckDep(candver.VerStr,oper,ver):
                continue

            # check if we need to install it
            self._dbg(2,"Need to get: %s" % depname)
            self._needPkgs.append(depname)
            return True

        # if we reach this point, we failed
        or_str = ""
        for dep in or_group:
            or_str += dep[0]
            if ver and oper:
                or_str += " (%s %s)" % (dep[2], dep[1])
            if dep != or_group[len(or_group)-1]:
                or_str += "|"
        self._failureString += _("Dependency is not satisfiable: %s\n") % or_str
        return False

    def _checkSinglePkgConflict(self, pkgname, ver, oper):
        """ returns true if a pkg conflicts with a real installed/marked
            pkg """
        # FIXME: deal with conflicts against its own provides
        #        (e.g. Provides: ftp-server, Conflicts: ftp-server)
        self._dbg(3, "_checkSinglePkgConflict() pkg='%s' ver='%s' oper='%s'" % (pkgname, ver, oper))
        pkgver = None
        cand = self._cache[pkgname]
        if cand.isInstalled:
            pkgver = cand.installedVersion
        elif cand.markedInstall:
            pkgver = cand.candidateVersion
        #print "pkg: %s" % pkgname
        #print "ver: %s" % ver
        #print "pkgver: %s " % pkgver
        #print "oper: %s " % oper
        if (pkgver and apt_pkg.CheckDep(pkgver,oper,ver) and 
            not self.replacesRealPkg(pkgname, oper, ver)):
            self._failureString += _("Conflicts with the installed package '%s'\n") % cand.name
            return True
        return False

    def _checkConflictsOrGroup(self, or_group):
        """ check the or-group for conflicts with installed pkgs """
        self._dbg(2,"_checkConflictsOrGroup(): %s " % (or_group))

        or_found = False
        virtual_pkg = None

        for dep in or_group:
            depname = dep[0]
            ver = dep[1]
            oper = dep[2]

            # check conflicts with virtual pkgs
            if not self._cache.has_key(depname):
                # FIXME: we have to check for virtual replaces here as 
                #        well (to pass tests/gdebi-test8.deb)
                if self._cache.isVirtualPkg(depname):
                    for pkg in self._cache.getProvidersForVirtual(depname):
                        self._dbg(3, "conflicts virtual check: %s" % pkg.name)
                        # P/C/R on virtal pkg, e.g. ftpd
                        if self.pkgName == pkg.name:
                            self._dbg(3, "conflict on self, ignoring")
                            continue
                        if self._checkSinglePkgConflict(pkg.name,ver,oper):
                            self._installedConflicts.add(pkg.name)
                continue
            if self._checkSinglePkgConflict(depname,ver,oper):
                self._installedConflicts.add(depname)
        return len(self._installedConflicts) != 0

    def getConflicts(self):
        conflicts = []
        key = "Conflicts"
        if self._sections.has_key(key):
            conflicts = apt_pkg.ParseDepends(self._sections[key])
        return conflicts

    def getDepends(self):
        depends = []
        # find depends
        for key in ["Depends","PreDepends"]:
            if self._sections.has_key(key):
                depends.extend(apt_pkg.ParseDepends(self._sections[key]))
        return depends

    def getProvides(self):
        provides = []
        key = "Provides"
        if self._sections.has_key(key):
            provides = apt_pkg.ParseDepends(self._sections[key])
        return provides

    def getReplaces(self):
        replaces = []
        key = "Replaces"
        if self._sections.has_key(key):
            replaces = apt_pkg.ParseDepends(self._sections[key])
        return replaces

    def replacesRealPkg(self, pkgname, oper, ver):
        """ 
        return True if the deb packages replaces a real (not virtual)
        packages named pkgname, oper, ver 
        """
        self._dbg(3, "replacesPkg() %s %s %s" % (pkgname,oper,ver))
        pkgver = None
        cand = self._cache[pkgname]
        if cand.isInstalled:
            pkgver = cand.installedVersion
        elif cand.markedInstall:
            pkgver = cand.candidateVersion
        for or_group in self.getReplaces():
            for (name, ver, oper) in or_group:
                if (name == pkgname and 
                    apt_pkg.CheckDep(pkgver,oper,ver)):
                    self._dbg(3, "we have a replaces in our package for the conflict against '%s'" % (pkgname))
                    return True
        return False

    def checkConflicts(self):
        """ check if the pkg conflicts with a existing or to be installed
            package. Return True if the pkg is ok """
        res = True
        for or_group in self.getConflicts():
            if self._checkConflictsOrGroup(or_group):
                #print "Conflicts with a exisiting pkg!"
                #self._failureString = "Conflicts with a exisiting pkg!"
                res = False
        return res

    def checkBreaksExistingPackages(self):
        """ 
        check if installing the package would break exsisting 
        package on the system, e.g. system has:
        smc depends on smc-data (= 1.4)
        and user tries to installs smc-data 1.6
        """
        # show progress information as this step may take some time
        size = float(len(self._cache))
        steps = int(size/50)
        debver = self._sections["Version"]
        for (i, pkg) in enumerate(self._cache):
            if i%steps == 0:
                self._cache.op_progress.update(float(i)/size*100.0)
            if not pkg.isInstalled:
                continue
            # check if the exising dependencies are still satisfied
            # with the package
            ver = pkg._pkg.CurrentVer
            for dep_or in pkg.installedDependencies:
                for dep in dep_or.or_dependencies:
                    if dep.name == self.pkgName:
                        if not apt_pkg.CheckDep(debver,dep.relation,dep.version):
                            self._dbg(2, "would break (depends) %s" % pkg.name)
                            # TRANSLATORS: the first '%s' is the package that breaks, the second the dependency that makes it break, the third the releation (e.g. >=) and the latest the version for the releation
                            self._failureString += _("Breaks exisiting package '%s' dependency %s (%s %s)\n") % (pkg.name, dep.name, dep.relation, dep.version)
                            self._cache.op_progress.done()
                            return False
            # now check if there are conflicts against this package on
            # the existing system
            if ver.DependsList.has_key("Conflicts"):
                for conflictsVerList in ver.DependsList["Conflicts"]:
                    for cOr in conflictsVerList:
                        if cOr.TargetPkg.Name == self.pkgName:
                            if apt_pkg.CheckDep(debver, cOr.CompType, cOr.TargetVer):
                                self._dbg(2, "would break (conflicts) %s" % pkg.name)
				# TRANSLATORS: the first '%s' is the package that conflicts, the second the packagename that it conflicts with (so the name of the deb the user tries to install), the third is the relation (e.g. >=) and the last is the version for the relation
                                self._failureString += _("Breaks exisiting package '%s' conflict: %s (%s %s)\n") % (pkg.name, cOr.TargetPkg.Name, cOr.CompType, cOr.TargetVer)
                                self._cache.op_progress.done()
                                return False
        self._cache.op_progress.done()
        return True

    # some constants
    (NO_VERSION,
     VERSION_OUTDATED,
     VERSION_SAME,
     VERSION_IS_NEWER) = range(4)
    
    def compareToVersionInCache(self, useInstalled=True):
        """ checks if the pkg is already installed or availabe in the cache
            and if so in what version, returns if the version of the deb
            is not available,older,same,newer
        """
        self._dbg(3,"compareToVersionInCache")
        pkgname = self._sections["Package"]
        debver = self._sections["Version"]
        self._dbg(1,"debver: %s" % debver)
        if self._cache.has_key(pkgname):
            if useInstalled:
                cachever = self._cache[pkgname].installedVersion
            else:
                cachever = self._cache[pkgname].candidateVersion
            if cachever != None:
                cmp = apt_pkg.VersionCompare(cachever,debver)
                self._dbg(1, "CompareVersion(debver,instver): %s" % cmp)
                if cmp == 0:
                    return self.VERSION_SAME
                elif cmp < 0:
                    return self.VERSION_IS_NEWER
                elif cmp > 0:
                    return self.VERSION_OUTDATED
        return self.NO_VERSION

    def checkDeb(self):
        self._dbg(3,"checkDepends")

        # check arch
        if not self._sections.has_key("Architecture"):
            self._dbg(1, "ERROR: no architecture field")
            self._failureString = _("No Architecture field in the package")
            return False
        arch = self._sections["Architecture"]
        if  arch != "all" and arch != apt_pkg.Config.Find("APT::Architecture"):
            self._dbg(1,"ERROR: Wrong architecture dude!")
            self._failureString = _("Wrong architecture '%s'") % arch
            return False

        # check version
        res = self.compareToVersionInCache()
        if res == self.VERSION_OUTDATED: # the deb is older than the installed
            self._failureString = _("A later version is already installed")
            return False

        # FIXME: this sort of error handling sux
        self._failureString = ""

        # check conflicts
        if not self.checkConflicts():
            return False

        # set progress information
        self._cache.op_progress.subOp = _("Analysing dependencies")

        # check if installing it would break anything on the 
        # current system
        if not self.checkBreaksExistingPackages():
            return False

        # try to satisfy the dependencies
        res = self._satisfyDepends(self.getDepends())
        if not res:
            return False

        # check for conflicts again (this time with the packages that are
        # makeed for install)
        if not self.checkConflicts():
            return False

        if self._cache._depcache.BrokenCount > 0:
            self._failureString = _("Failed to satisfy all dependencies (broken cache)")
            # clean the cache again
            self._cache.clear()
            return False
        return True

    def satisfyDependsStr(self, dependsstr):
        return self._satisfyDepends(apt_pkg.ParseDepends(dependsstr))

    def _satisfyDepends(self, depends):
        # turn off MarkAndSweep via a action group (if available)
        try:
            _actiongroup = apt_pkg.GetPkgActionGroup(self._cache._depcache)
        except AttributeError, e:
            pass
        # check depends
        for or_group in depends:
            #print "or_group: %s" % or_group
            #print "or_group satified: %s" % self._isOrGroupSatisfied(or_group)
            if not self._isOrGroupSatisfied(or_group):
                if not self._satisfyOrGroup(or_group):
                    return False
        # now try it out in the cache
            for pkg in self._needPkgs:
                try:
                    self._cache[pkg].markInstall(fromUser=False)
                except SystemError, e:
                    self._failureString = _("Cannot install '%s'") % pkg
                    self._cache.clear()
                    return False
        return True

    def missingDeps(self):
        self._dbg(1, "Installing: %s" % self._needPkgs)
        if self._needPkgs == None:
            self.checkDeb()
        return self._needPkgs
    missingDeps = property(missingDeps)

    def requiredChanges(self):
        """ gets the required changes to satisfy the depends.
            returns a tuple with (install, remove, unauthenticated)
        """
        install = []
        remove = []
        unauthenticated = []
        for pkg in self._cache:
            if pkg.markedInstall or pkg.markedUpgrade:
                install.append(pkg.name)
                # check authentication, one authenticated origin is enough
                # libapt will skip non-authenticated origins then
                authenticated = False
                for origin in pkg.candidateOrigin:
                    authenticated |= origin.trusted
                if not authenticated:
                    unauthenticated.append(pkg.name)
            if pkg.markedDelete:
                remove.append(pkg.name)
        return (install,remove, unauthenticated)
    requiredChanges = property(requiredChanges)

    def filelist(self):
        """ return the list of files in the deb """
        files = []
        def extract_cb(What,Name,Link,Mode,UID,GID,Size,MTime,Major,Minor):
            #print "%s '%s','%s',%u,%u,%u,%u,%u,%u,%u"\
            #      % (What,Name,Link,Mode,UID,GID,Size, MTime, Major, Minor)
            files.append(Name)
        try:
            try:
                apt_inst.debExtract(open(self.file), extract_cb, "data.tar.gz")
            except SystemError, e:
                try:
                    apt_inst.debExtract(open(self.file), extract_cb, "data.tar.bz2")
                except SystemError, e:
                    try:
                        apt_inst.debExtract(open(self.file), extract_cb, "data.tar.lzma")
                    except SystemError, e:
                        return [_("List of files could not be read, please report this as a bug")]
        # IOError may happen because of gvfs madness (LP: #211822)
        except IOError, e:
            return [_("IOError during filelist read: %s") % e]
        return files
    filelist = property(filelist)
    
    # properties
    def __getitem__(self,item):
        if not self._sections.has_key(item):
            # Translators: it's for missing entries in the deb package,
            # e.g. a missing "Maintainer" field
            return _("%s is not available") % item
        return self._sections[item]

    def _dbg(self, level, msg):
        """Write debugging output to sys.stderr.
        """
        if level <= self.debug:
            print >> sys.stderr, msg


if __name__ == "__main__":

    cache = Cache()

    vp = "www-browser"
    print "%s virtual: %s" % (vp,cache.isVirtualPkg(vp))
    providers = cache.getProvidersForVirtual(vp)
    print "Providers for %s :" % vp
    for pkg in providers:
        print " %s" % pkg.name
    
    d = DebPackage(cache, sys.argv[1])
    print "Deb: %s" % d.pkgName
    if not d.checkDeb():
        print "can't be satified"
        print d._failureString
    print "missing deps: %s" % d.missingDeps
    print d.requiredChanges

