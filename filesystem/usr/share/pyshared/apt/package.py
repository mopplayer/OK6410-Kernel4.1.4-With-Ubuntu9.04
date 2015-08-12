# package.py - apt package abstraction
#
#  Copyright (c) 2005 Canonical
#
#  Author: Michael Vogt <michael.vogt@ubuntu.com>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA
"""Functionality related to packages."""
import gettext
import httplib
import sys
import re
import socket
import urllib2

import apt_pkg


__all__ = 'BaseDependency', 'Dependency', 'Origin', 'Package', 'Record'


def _(string):
    """Return the translation of the string."""
    return gettext.dgettext("python-apt", string)


class BaseDependency(object):
    """A single dependency.

    Attributes defined here:
        name      - The name of the dependency
        relation  - The relation (>>,>=,==,<<,<=,)
        version   - The version depended on
        preDepend - Boolean value whether this is a pre-dependency.
    """

    def __init__(self, name, rel, ver, pre):
        self.name = name
        self.relation = rel
        self.version = ver
        self.preDepend = pre


class Dependency(object):
    """Represent an Or-group of dependencies.

    Attributes defined here:
        or_dependencies - The possible choices
    """

    def __init__(self, alternatives):
        self.or_dependencies = alternatives


class Origin(object):
    """The origin of a version.

    Attributes defined here:
        archive   - The archive (eg. unstable)
        component - The component (eg. main)
        label     - The Label, as set in the Release file
        origin    - The Origin, as set in the Release file
        site      - The hostname of the site.
        trusted   - Boolean value whether this is trustworthy.
    """

    def __init__(self, pkg, VerFileIter):
        self.archive = VerFileIter.Archive
        self.component = VerFileIter.Component
        self.label = VerFileIter.Label
        self.origin = VerFileIter.Origin
        self.site = VerFileIter.Site
        self.not_automatic = VerFileIter.NotAutomatic
        # check the trust
        indexfile = pkg._list.FindIndex(VerFileIter)
        if indexfile and indexfile.IsTrusted:
            self.trusted = True
        else:
            self.trusted = False

    def __repr__(self):
        return ("<Origin component:'%s' archive:'%s' origin:'%s' label:'%s'"
                "site:'%s' isTrusted:'%s'>") % (self.component, self.archive,
                                                self.origin, self.label,
                                                self.site, self.trusted)


class Record(object):
    """Represent a pkgRecord.

    It can be accessed like a dictionary and can also give the original package
    record if accessed as a string.
    """

    def __init__(self, record_str):
        self._rec = apt_pkg.ParseSection(record_str)

    def __str__(self):
        return str(self._rec)

    def __getitem__(self, key):
        return self._rec[key]

    def __contains__(self, key):
        return self._rec.has_key(key)

    def __iter__(self):
        return iter(self._rec.keys())

    def iteritems(self):
        """An iterator over the (key, value) items of the record."""
        for key in self._rec.keys():
            yield key, self._rec[key]

    def get(self, key, default=None):
        """Return record[key] if key in record, else `default`.

        The parameter `default` must be either a string or None.
        """
        return self._rec.get(key, default)

    def has_key(self, key):
        """deprecated form of 'key in x'."""
        return self._rec.has_key(key)


class Package(object):
    """Representation of a package in a cache.

    This class provides methods and properties for working with a package. It
    lets you mark the package for installation, check if it is installed, and
    much more.
    """

    def __init__(self, cache, depcache, records, sourcelist, pcache, pkgiter):
        """ Init the Package object """
        self._cache = cache             # low level cache
        self._depcache = depcache
        self._records = records
        self._pkg = pkgiter
        self._list = sourcelist               # sourcelist
        self._pcache = pcache           # python cache in cache.py
        self._changelog = ""            # Cached changelog

    def _lookupRecord(self, UseCandidate=True):
        """Internal helper that moves the Records to the right position.

        Must be called before _records is accessed.
        """
        if UseCandidate:
            ver = self._depcache.GetCandidateVer(self._pkg)
        else:
            ver = self._pkg.CurrentVer

        # check if we found a version
        if ver is None:
            #print "No version for: %s (Candidate: %s)" % (self._pkg.Name,
            #                                              UseCandidate)
            return False

        if ver.FileList is None:
            print "No FileList for: %s " % self._pkg.Name()
            return False
        f, index = ver.FileList.pop(0)
        self._records.Lookup((f, index))
        return True

    @property
    def name(self):
        """Return the name of the package."""
        return self._pkg.Name

    @property
    def id(self):
        """Return a uniq ID for the package.

        This can be used eg. to store additional information about the pkg."""
        return self._pkg.ID

    def __hash__(self):
        """Return the hash of the object.

        This returns the same value as ID, which is unique."""
        return self._pkg.ID

    @property
    def installedVersion(self):
        """Return the installed version as string."""
        ver = self._pkg.CurrentVer
        if ver is not None:
            return ver.VerStr
        else:
            return None

    @property
    def candidateVersion(self):
        """Return the candidate version as string."""
        ver = self._depcache.GetCandidateVer(self._pkg)
        if ver is not None:
            return ver.VerStr
        else:
            return None

    def _getDependencies(self, ver):
        """Get the dependencies for a given version of a package."""
        depends_list = []
        depends = ver.DependsList
        for t in ["PreDepends", "Depends"]:
            try:
                for depVerList in depends[t]:
                    base_deps = []
                    for depOr in depVerList:
                        base_deps.append(BaseDependency(depOr.TargetPkg.Name,
                                        depOr.CompType, depOr.TargetVer,
                                        (t == "PreDepends")))
                    depends_list.append(Dependency(base_deps))
            except KeyError:
                pass
        return depends_list

    @property
    def candidateDependencies(self):
        """Return a list of candidate dependencies."""
        candver = self._depcache.GetCandidateVer(self._pkg)
        if candver is None:
            return []
        return self._getDependencies(candver)

    @property
    def installedDependencies(self):
        """Return a list of installed dependencies."""
        ver = self._pkg.CurrentVer
        if ver is None:
            return []
        return self._getDependencies(ver)

    @property
    def architecture(self):
        """Return the Architecture of the package"""
        if not self._lookupRecord():
            return None
        sec = apt_pkg.ParseSection(self._records.Record)
        try:
            return sec["Architecture"]
        except KeyError:
            return None

    def _downloadable(self, useCandidate=True):
        """Return True if the package is downloadable."""
        if useCandidate:
            ver = self._depcache.GetCandidateVer(self._pkg)
        else:
            ver = self._pkg.CurrentVer
        if ver is None:
            return False
        return ver.Downloadable

    @property
    def candidateDownloadable(self):
        """Return True if the candidate is downloadable."""
        return self._downloadable(True)

    @property
    def installedDownloadable(self):
        """Return True if the installed version is downloadable."""
        return self._downloadable(False)

    @property
    def sourcePackageName(self):
        """Return the source package name as string."""
        if not self._lookupRecord():
            if not self._lookupRecord(False):
                return self._pkg.Name
        src = self._records.SourcePkg
        if src != "":
            return src
        else:
            return self._pkg.Name

    @property
    def homepage(self):
        """Return the homepage field as string."""
        if not self._lookupRecord():
            return None
        return self._records.Homepage

    @property
    def section(self):
        """Return the section of the package."""
        return self._pkg.Section

    @property
    def priority(self):
        """Return the priority (of the candidate version)."""
        ver = self._depcache.GetCandidateVer(self._pkg)
        if ver:
            return ver.PriorityStr
        else:
            return None

    @property
    def installedPriority(self):
        """Return the priority (of the installed version)."""
        ver = self._depcache.GetCandidateVer(self._pkg)
        if ver:
            return ver.PriorityStr
        else:
            return None

    @property
    def summary(self):
        """Return the short description (one line summary)."""
        if not self._lookupRecord():
            return ""
        ver = self._depcache.GetCandidateVer(self._pkg)
        desc_iter = ver.TranslatedDescription
        self._records.Lookup(desc_iter.FileList.pop(0))
        return self._records.ShortDesc

    @property
    def description(self, format=True, useDots=False):
        """Return the formatted long description.

        Return the formated long description according to the Debian policy
        (Chapter 5.6.13).
        See http://www.debian.org/doc/debian-policy/ch-controlfields.html
        for more information.
        """
        if not format:
            return self.rawDescription
        if not self._lookupRecord():
            return ""
        # get the translated description
        ver = self._depcache.GetCandidateVer(self._pkg)
        desc_iter = ver.TranslatedDescription
        self._records.Lookup(desc_iter.FileList.pop(0))
        desc = ""
        try:
            dsc = unicode(self._records.LongDesc, "utf-8")
        except UnicodeDecodeError, err:
            dsc = _("Invalid unicode in description for '%s' (%s). "
                  "Please report.") % (self.name, err)
        lines = dsc.split("\n")
        for i in range(len(lines)):
            # Skip the first line, since its a duplication of the summary
            if i == 0:
                continue
            raw_line = lines[i]
            if raw_line.strip() == ".":
                # The line is just line break
                if not desc.endswith("\n"):
                    desc += "\n"
                continue
            elif raw_line.startswith("  "):
                # The line should be displayed verbatim without word wrapping
                if not desc.endswith("\n"):
                    line = "\n%s\n" % raw_line[2:]
                else:
                    line = "%s\n" % raw_line[2:]
            elif raw_line.startswith(" "):
                # The line is part of a paragraph.
                if desc.endswith("\n") or desc == "":
                    # Skip the leading white space
                    line = raw_line[1:]
                else:
                    line = raw_line
            else:
                line = raw_line
            # Use dots for lists
            if useDots:
                line = re.sub(r"^(\s*)(\*|0|o|-) ", ur"\1\u2022 ", line, 1)
            # Add current line to the description
            desc += line
        return desc

    @property
    def rawDescription(self):
        """return the long description (raw)."""
        if not self._lookupRecord():
            return ""
        return self._records.LongDesc

    @property
    def candidateRecord(self):
        """Return the Record of the candidate version of the package."""
        if not self._lookupRecord(True):
            return None
        return Record(self._records.Record)

    @property
    def installedRecord(self):
        """Return the Record of the candidate version of the package."""
        if not self._lookupRecord(False):
            return None
        return Record(self._records.Record)

    # depcache states

    @property
    def markedInstall(self):
        """Return True if the package is marked for install."""
        return self._depcache.MarkedInstall(self._pkg)

    @property
    def markedUpgrade(self):
        """Return True if the package is marked for upgrade."""
        return self._depcache.MarkedUpgrade(self._pkg)

    @property
    def markedDelete(self):
        """Return True if the package is marked for delete."""
        return self._depcache.MarkedDelete(self._pkg)

    @property
    def markedKeep(self):
        """Return True if the package is marked for keep."""
        return self._depcache.MarkedKeep(self._pkg)

    @property
    def markedDowngrade(self):
        """ Package is marked for downgrade """
        return self._depcache.MarkedDowngrade(self._pkg)

    @property
    def markedReinstall(self):
        """Return True if the package is marked for reinstall."""
        return self._depcache.MarkedReinstall(self._pkg)

    @property
    def isInstalled(self):
        """Return True if the package is installed."""
        return (self._pkg.CurrentVer is not None)

    @property
    def isUpgradable(self):
        """Return True if the package is upgradable."""
        return self.isInstalled and self._depcache.IsUpgradable(self._pkg)

    @property
    def isAutoRemovable(self):
        """Return True if the package is no longer required.

        If the package has been installed automatically as a dependency of
        another package, and if no packages depend on it anymore, the package
        is no longer required.
        """
        return self.isInstalled and self._depcache.IsGarbage(self._pkg)

    # sizes

    @property
    def packageSize(self):
        """Return the size of the candidate deb package."""
        ver = self._depcache.GetCandidateVer(self._pkg)
        return ver.Size

    @property
    def installedPackageSize(self):
        """Return the size of the installed deb package."""
        ver = self._pkg.CurrentVer
        return ver.Size

    @property
    def candidateInstalledSize(self, UseCandidate=True):
        """Return the size of the candidate installed package."""
        ver = self._depcache.GetCandidateVer(self._pkg)
        if ver:
            return ver.Size
        else:
            return None

    @property
    def installedSize(self):
        """Return the size of the currently installed package."""
        ver = self._pkg.CurrentVer
        if ver is None:
            return 0
        return ver.InstalledSize

    @property
    def installedFiles(self):
        """Return a list of files installed by the package.

        Return a list of unicode names of the files which have
        been installed by this package
        """
        path = "/var/lib/dpkg/info/%s.list" % self.name
        try:
            file_list = open(path)
            try:
                return file_list.read().decode().split("\n")
            finally:
                file_list.close()
        except EnvironmentError:
            return []

    def getChangelog(self, uri=None, cancel_lock=None):
        """
        Download the changelog of the package and return it as unicode
        string.

        The parameter `uri` refers to the uri of the changelog file. It may
        contain multiple named variables which will be substitued. These
        variables are (src_section, prefix, src_pkg, src_ver). An example is
        the Ubuntu changelog:
            "http://changelogs.ubuntu.com/changelogs/pool" \\
                "/%(src_section)s/%(prefix)s/%(src_pkg)s" \\
                "/%(src_pkg)s_%(src_ver)s/changelog"

        The parameter `cancel_lock` refers to an instance of threading.Lock,
        which if set, prevents the download.
        """
        # Return a cached changelog if available
        if self._changelog != "":
            return self._changelog

        if uri is None:
            if self.candidateOrigin[0].origin == "Debian":
                uri = "http://packages.debian.org/changelogs/pool" \
                      "/%(src_section)s/%(prefix)s/%(src_pkg)s" \
                      "/%(src_pkg)s_%(src_ver)s/changelog"
            elif self.candidateOrigin[0].origin == "Ubuntu":
                uri = "http://changelogs.ubuntu.com/changelogs/pool" \
                      "/%(src_section)s/%(prefix)s/%(src_pkg)s" \
                      "/%(src_pkg)s_%(src_ver)s/changelog"
            else:
                return _("The list of changes is not available")

        # get the src package name
        src_pkg = self.sourcePackageName

        # assume "main" section
        src_section = "main"
        # use the section of the candidate as a starting point
        section = self._depcache.GetCandidateVer(self._pkg).Section

        # get the source version, start with the binaries version
        bin_ver = self.candidateVersion
        src_ver = self.candidateVersion
        #print "bin: %s" % binver
        try:
            # FIXME: This try-statement is too long ...
            # try to get the source version of the pkg, this differs
            # for some (e.g. libnspr4 on ubuntu)
            # this feature only works if the correct deb-src are in the
            # sources.list
            # otherwise we fall back to the binary version number
            src_records = apt_pkg.GetPkgSrcRecords()
            src_rec = src_records.Lookup(src_pkg)
            if src_rec:
                src_ver = src_records.Version
                #if apt_pkg.VersionCompare(binver, srcver) > 0:
                #    srcver = binver
                if not src_ver:
                    src_ver = bin_ver
                #print "srcver: %s" % src_ver
                section = src_records.Section
                #print "srcsect: %s" % section
            else:
                # fail into the error handler
                raise SystemError
        except SystemError:
            src_ver = bin_ver

        l = section.split("/")
        if len(l) > 1:
            src_section = l[0]

        # lib is handled special
        prefix = src_pkg[0]
        if src_pkg.startswith("lib"):
            prefix = "lib" + src_pkg[3]

        # stip epoch
        l = src_ver.split(":")
        if len(l) > 1:
            src_ver = "".join(l[1:])

        uri = uri % {"src_section": src_section,
                     "prefix": prefix,
                     "src_pkg": src_pkg,
                     "src_ver": src_ver}

        timeout = socket.getdefaulttimeout()
        
        # FIXME: when python2.4 vanishes from the archive,
        #        merge this into a single try..finally block (pep 341)
        try:
            try:
                # Set a timeout for the changelog download
                socket.setdefaulttimeout(2)

                # Check if the download was canceled
                if cancel_lock and cancel_lock.isSet():
                    return ""
                changelog_file = urllib2.urlopen(uri)
                # do only get the lines that are new
                changelog = ""
                regexp = "^%s \((.*)\)(.*)$" % (re.escape(src_pkg))

                while True:
                    # Check if the download was canceled
                    if cancel_lock and cancel_lock.isSet():
                        return ""
                    # Read changelog line by line
                    line_raw = changelog_file.readline()
                    if line_raw == "":
                        break
                    # The changelog is encoded in utf-8, but since there isn't any
                    # http header, urllib2 seems to treat it as ascii
                    line = line_raw.decode("utf-8")

                    #print line.encode('utf-8')
                    match = re.match(regexp, line)
                    if match:
                        # strip epoch from installed version
                        # and from changelog too
                        installed = self.installedVersion
                        if installed and ":" in installed:
                            installed = installed.split(":", 1)[1]
                        changelog_ver = match.group(1)
                        if changelog_ver and ":" in changelog_ver:
                            changelog_ver = changelog_ver.split(":", 1)[1]
                        if (installed and 
                                apt_pkg.VersionCompare(changelog_ver, installed) <= 0):
                            break
                    # EOF (shouldn't really happen)
                    changelog += line

                # Print an error if we failed to extract a changelog
                if len(changelog) == 0:
                    changelog = _("The list of changes is not available")
                self._changelog = changelog

            except urllib2.HTTPError:
                return _("The list of changes is not available yet.\n\n"
                         "Please use http://launchpad.net/ubuntu/+source/%s/%s/"
                         "+changelog\n"
                         "until the changes become available or try again "
                         "later.") % (src_pkg, src_ver)
            except (IOError, httplib.BadStatusLine):
                return _("Failed to download the list of changes. \nPlease "
                         "check your Internet connection.")
        finally:
            socket.setdefaulttimeout(timeout)
        return self._changelog

    @property
    def candidateOrigin(self):
        """Return the Origin() of the candidate version."""
        ver = self._depcache.GetCandidateVer(self._pkg)
        if not ver:
            return None
        origins = []
        for (verFileIter, index) in ver.FileList:
            origins.append(Origin(self, verFileIter))
        return origins

    # depcache actions

    def markKeep(self):
        """Mark a package for keep."""
        self._pcache.cachePreChange()
        self._depcache.MarkKeep(self._pkg)
        self._pcache.cachePostChange()

    def markDelete(self, autoFix=True, purge=False):
        """Mark a package for install.

        If autoFix is True, the resolver will be run, trying to fix broken
        packages. This is the default.

        If purge is True, remove the configuration files of the package as
        well. The default is to keep the configuration.
        """
        self._pcache.cachePreChange()
        self._depcache.MarkDelete(self._pkg, purge)
        # try to fix broken stuffsta
        if autoFix and self._depcache.BrokenCount > 0:
            Fix = apt_pkg.GetPkgProblemResolver(self._depcache)
            Fix.Clear(self._pkg)
            Fix.Protect(self._pkg)
            Fix.Remove(self._pkg)
            Fix.InstallProtect()
            Fix.Resolve()
        self._pcache.cachePostChange()

    def markInstall(self, autoFix=True, autoInst=True, fromUser=True):
        """Mark a package for install.

        If autoFix is True, the resolver will be run, trying to fix broken
        packages. This is the default.

        If autoInst is True, the dependencies of the packages will be installed
        automatically. This is the default.

        If fromUser is True, this package will not be marked as automatically
        installed. This is the default. Set it to False if you want to be able
        to remove the package at a later stage if no other package depends on
        it.
        """
        self._pcache.cachePreChange()
        self._depcache.MarkInstall(self._pkg, autoInst, fromUser)
        # try to fix broken stuff
        if autoFix and self._depcache.BrokenCount > 0:
            fixer = apt_pkg.GetPkgProblemResolver(self._depcache)
            fixer.Clear(self._pkg)
            fixer.Protect(self._pkg)
            fixer.Resolve(True)
        self._pcache.cachePostChange()

    def markUpgrade(self):
        """Mark a package for upgrade."""
        if self.isUpgradable:
            self.markInstall()
        else:
            # FIXME: we may want to throw a exception here
            sys.stderr.write(("MarkUpgrade() called on a non-upgrable pkg: "
                              "'%s'\n") % self._pkg.Name)

    def commit(self, fprogress, iprogress):
        """Commit the changes.

        The parameter `fprogress` refers to a FetchProgress() object, as
        found in apt.progress.

        The parameter `iprogress` refers to an InstallProgress() object, as
        found in apt.progress.
        """
        self._depcache.Commit(fprogress, iprogress)


def _test():
    """Self-test."""
    print "Self-test for the Package modul"
    import random
    import apt
    apt_pkg.init()
    cache = apt_pkg.GetCache()
    depcache = apt_pkg.GetDepCache(cache)
    records = apt_pkg.GetPkgRecords(cache)
    sourcelist = apt_pkg.GetPkgSourceList()

    pkgiter = cache["apt-utils"]
    pkg = Package(cache, depcache, records, sourcelist, None, pkgiter)
    print "Name: %s " % pkg.name
    print "ID: %s " % pkg.id
    print "Priority (Candidate): %s " % pkg.priority
    print "Priority (Installed): %s " % pkg.installedPriority
    print "Installed: %s " % pkg.installedVersion
    print "Candidate: %s " % pkg.candidateVersion
    print "CandidateDownloadable: %s" % pkg.candidateDownloadable
    print "CandidateOrigins: %s" % pkg.candidateOrigin
    print "SourcePkg: %s " % pkg.sourcePackageName
    print "Section: %s " % pkg.section
    print "Summary: %s" % pkg.summary
    print "Description (formated) :\n%s" % pkg.description
    print "Description (unformated):\n%s" % pkg.rawDescription
    print "InstalledSize: %s " % pkg.installedSize
    print "PackageSize: %s " % pkg.packageSize
    print "Dependencies: %s" % pkg.installedDependencies
    for dep in pkg.candidateDependencies:
        print ",".join("%s (%s) (%s) (%s)" % (o.name, o.version, o.relation,
                        o.preDepend) for o in dep.or_dependencies)
    print "arch: %s" % pkg.architecture
    print "homepage: %s" % pkg.homepage
    print "rec: ", pkg.candidateRecord


    # now test install/remove
    progress = apt.progress.OpTextProgress()
    cache = apt.Cache(progress)
    print cache["2vcard"].getChangelog()
    for i in True, False:
        print "Running install on random upgradable pkgs with AutoFix: %s " % i
        for pkg in cache:
            if pkg.isUpgradable:
                if random.randint(0, 1) == 1:
                    pkg.markInstall(i)
        print "Broken: %s " % cache._depcache.BrokenCount
        print "InstCount: %s " % cache._depcache.InstCount

    print
    # get a new cache
    for i in True, False:
        print "Randomly remove some packages with AutoFix: %s" % i
        cache = apt.Cache(progress)
        for name in cache.keys():
            if random.randint(0, 1) == 1:
                try:
                    cache[name].markDelete(i)
                except SystemError:
                    print "Error trying to remove: %s " % name
        print "Broken: %s " % cache._depcache.BrokenCount
        print "DelCount: %s " % cache._depcache.DelCount

# self-test
if __name__ == "__main__":
    _test()
