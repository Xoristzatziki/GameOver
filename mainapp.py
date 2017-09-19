#!/usr/bin/python3
#Copyright Ηλίας Ηλιάδης

# contact http://gnu.kekbay.gr/games/  -- mailto:OCPcompanion@kekbay.gr
#
# This file is part of Game Over Gtk3 game.
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3.0 of the License, or (at your
# option) any later version.
#
# It is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GPLv3 along
# with OCPcompanion. If not, see <http://www.gnu.org/licenses/>.

#ffmpeg is required for sounds.

import time
import os, sys
try:
    import gi
    gi.require_version('Gtk', '3.0')
except:
    sys.exit(1)

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import GObject

import datetime

from _lib.OCP import *
import _lib.maingui as myMainGui

APPNAME = 'Game Over'
#TODO:set version before production
version = ''

class App:
    def __init__( self, realfile_dir):
        self.appname = APPNAME
        #TODO: on producted game get it from version
        #print(os.path.basename(realfile_dir))
        #relversionnums = os.path.basename(realfile_dir)[1:].split('.')
        if version == '':
            self.version = os.path.basename(realfile_dir)[2:]
        else:
            self.version = version
        self.workingdir = realfile_dir
        self.icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join(self.workingdir, '_icons', "logo.png"))
        userdir = os.getenv('USERPROFILE') or os.getenv('HOME')
        confpath = os.path.join(userdir, '.OCP' + self.appname)
        #TODO: what if we cannot create conf directory?
        if not os.path.exists(confpath):
            os.mkdir(confpath)
        self.conf = os.path.join(confpath, 'OCP.conf')
        self.MySettings = OCPPrivateProfile(self.conf)


def main(realfile_dir):
    myApp = App(realfile_dir)
    gladenongraphicstuple =('adjcounternew','adjustmentslider')
    mainwindow = myMainGui.MainGui(myApp, 'maingui.glade', gladenongraphicstuple, mainbox='grid1')
    mainwindow.set_position(Gtk.WindowPosition.CENTER)
    response = mainwindow.run()
    sys.exit(response)

if __name__ == "__main__":
    realfile = os.path.realpath(__file__)
    realfile_dir = os.path.dirname(os.path.abspath(realfile))
    test = main(realfile_dir)
