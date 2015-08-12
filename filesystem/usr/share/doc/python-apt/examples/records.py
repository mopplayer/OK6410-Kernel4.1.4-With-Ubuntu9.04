#!/usr/bin/env python

import apt

cache = apt.Cache()

for pkg in cache:
    if not pkg.candidateRecord:
        continue
    if "Task" in pkg.candidateRecord:
        print "Pkg %s is part of '%s'" % (
            pkg.name, pkg.candidateRecord["Task"].split())
        #print pkg.candidateRecord
