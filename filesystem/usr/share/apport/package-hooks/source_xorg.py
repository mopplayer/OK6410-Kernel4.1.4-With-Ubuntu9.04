#!/usr/bin/python

'''Xorg Apport interface

Copyright (C) 2007, 2008 Canonical Ltd.
Author: Bryce Harrington <bryce.harrington@ubuntu.com>

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
the full text of the license.
'''

# TODO:
#  - Create some general purpose routines (see source_network-manager.py)
#  - Parse files to generate system_environment more concisely
#  - Trim lshal output to just required info

import os.path
import subprocess

def installed_version(pkg):
    script = subprocess.Popen(['apt-cache', 'policy', pkg], stdout=subprocess.PIPE)
    output = script.communicate()[0]
    return output.split('\n')[1].replace("Installed: ", "")

def add_info(report):
    # Build System Environment
    report['system']      = " distro:             Ubuntu\n"
    try:
        script = subprocess.Popen(['uname', '-m'], stdout=subprocess.PIPE)
        report['system'] += " architecture:       " + script.communicate()[0]
    except OSError:
        pass
    try:
        script = subprocess.Popen(['uname', '-r'], stdout=subprocess.PIPE)
        report['system'] += " kernel:             " + script.communicate()[0]
    except OSError:
        pass
    try:
        report['system'] += " xserver-xorg:     " + installed_version('xserver-xorg') + "\n"
    except OSError:
        pass
    try:
        report['system'] += " mesa:             " + installed_version('libgl1-mesa-glx') + "\n"
    except OSError:
        pass
    try:
        report['system'] += " libdrm:           " + installed_version('libdrm2') + "\n"
    except OSError:
        pass
    try:
        report['system'] += " -intel:           " + installed_version('xserver-xorg-video-intel') + "\n"
    except OSError:
        pass
    try:
        report['system'] += " -ati:             " + installed_version('xserver-xorg-video-ati') + "\n"
    except OSError:
        pass

    try:
        report['XorgConf'] = open('/etc/X11/xorg.conf').read()
    except IOError:
        pass

    try:
        report['XorgLog']  = open('/var/log/Xorg.0.log').read()
    except IOError:
        pass

    try:
        report['XorgLogOld']  = open('/var/log/Xorg.0.log.old').read()
    except IOError:
        pass

    try:
        report['ProcVersion']  = open('/proc/version').read()
    except IOError:
        pass

    try:
        script = subprocess.Popen(['lspci', '-vvnn'], stdout=subprocess.PIPE)
        report['LsPci'] = script.communicate()[0]
    except OSError:
        pass

    try:
        script = subprocess.Popen(['lshal'], stdout=subprocess.PIPE)
        report['LsHal'] = script.communicate()[0]
    except OSError:
        pass

    try:
        script = subprocess.Popen(['lsmod'], stdout=subprocess.PIPE)
        report['LsMod'] = script.communicate()[0]
    except OSError:
        pass

    try:
        script = subprocess.Popen(['grep', 'fglrx', '/var/log/kern.log', '/proc/modules'], stdout=subprocess.PIPE)
        matches = script.communicate()[0]
        if (matches):
            report['fglrx-loaded'] = matches
    except OSError:
        pass

    try:
        script = subprocess.Popen(['xrandr', '--verbose'], stdout=subprocess.PIPE)
        report['Xrandr'] = script.communicate()[0]
    except OSError:
        pass

    try:
        monitors_config = os.path.join(os.environ['HOME'], '.config/monitors.xml')
        report['monitors.xml']  = open(monitors_config).read()
    except IOError:
        pass

    try:
        script = subprocess.Popen(['xdpyinfo'], stdout=subprocess.PIPE)
        report['xdpyinfo'] = script.communicate()[0]
    except OSError:
        pass

    try:
        script = subprocess.Popen(['glxinfo'], stdout=subprocess.PIPE)
        report['glxinfo'] = script.communicate()[0]
    except OSError:
        pass

    try:
        script = subprocess.Popen(['setxkbmap', '-print'], stdout=subprocess.PIPE)
        report['setxkbmap'] = script.communicate()[0]
    except OSError:
        pass

    try:
        script = subprocess.Popen(['xkbcomp', ':0', '-w0', '-'], stdout=subprocess.PIPE)
        report['xkbcomp'] = script.communicate()[0]
    except OSError:
        pass

## DEBUGING ##
if __name__ == '__main__':
    report = {}
    add_info(report)
    for key in report:
        print '[%s]\n%s' % (key, report[key])
