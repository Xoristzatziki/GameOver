#!/usr/bin/python3
# Copyright Ηλιάδης Ηλίας, 2017.
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
# with this file. If not, see <http://www.gnu.org/licenses/>.

import os, sys
import subprocess
import datetime

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import GObject

class MyMedia():
    def __init__( self, myApp, theiconsize):
        self.App = myApp

        self.theiconsize = theiconsize

        self.images = {}
        self.images['black'], self.images['white'], self.images['exploded'], self.images['flag'] = self.load_pixbufs_with_size()

        self.soundfiles = {}
        self.soundfiles['timebell'] = os.path.abspath( os.path.join(self.App.workingdir, '_sounds', 'bell.oga'))
        self.soundfiles['bomb'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'message.oga'))
        self.soundfiles['solved'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'complete.oga'))
        self.soundfiles['opened'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'button-pressed.ogg'))
        self.soundfiles['timeout'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'camera-shutter.oga'))


    def load_pixbufs_with_size(self):
        #tmpjpg = os.path.join(self.outputfilepath, "out1.jpg")
        pixbufB = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=os.path.abspath(os.path.join(self.App.workingdir, '_icons', 'black.png')),
        width=self.theiconsize,
        height=self.theiconsize,
        preserve_aspect_ratio=True)

        pixbufW = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=os.path.abspath(os.path.join(self.App.workingdir, '_icons', 'white.png')),
        width=self.theiconsize,
        height=self.theiconsize,
        preserve_aspect_ratio=True)

        pixbufE = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=os.path.abspath(os.path.join(self.App.workingdir, '_icons', 'exploded.svg')),
        width=int(0.8 * self.theiconsize),
        height=int(0.8 * self.theiconsize),
        preserve_aspect_ratio=True)

        pixbufF = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=os.path.abspath(os.path.join(self.App.workingdir, '_icons', 'flag.svg')),
        width=int(0.8 * self.theiconsize),
        height=int(0.8 * self.theiconsize),
        preserve_aspect_ratio=True)

        return pixbufB, pixbufW, pixbufE, pixbufF
