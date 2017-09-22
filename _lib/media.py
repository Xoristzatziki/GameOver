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

from urllib import parse
import threading
import time


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GdkX11, GstVideo

Gst.init(None)

class MyMedia():
    def __init__( self, myApp, theiconsize):
        self.App = myApp

        self.theiconsize = theiconsize

        self.images = {}
        self.images['black'], self.images['white'], self.images['exploded'], self.images['flag'] = self.load_pixbufs_with_size()

        self.icons = {}
        self.icons['logo'] = os.path.abspath( os.path.join(self.App.workingdir, '_icons', 'logobig.png'))

        self.soundfiles = {}
        self.soundfiles['timebell'] = os.path.abspath( os.path.join(self.App.workingdir, '_sounds', 'bell.oga'))
        self.soundfiles['bomb'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'message.oga'))
        self.soundfiles['solved'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'complete.oga'))
        self.soundfiles['opened'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'button-pressed.ogg'))
        self.soundfiles['timeout'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'camera-shutter.oga'))

        self.sounduris = {}
        self.sounduris['timebell'] = file_to_local_uri(os.path.abspath( os.path.join(self.App.workingdir, '_sounds', 'bell.oga')))
        self.sounduris['bomb'] = file_to_local_uri(os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'message.oga')))
        self.sounduris['solved'] = file_to_local_uri(os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'complete.oga')))
        self.sounduris['opened'] = file_to_local_uri(os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'button-pressed.ogg')))
        self.sounduris['timeout'] = file_to_local_uri(os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'camera-shutter.oga')))

        self.soundwavs = {}
        self.soundwavs['timebell'] = os.path.abspath( os.path.join(self.App.workingdir, '_sounds', 'bell.wav'))
        self.soundwavs['bomb'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'message.wav'))
        self.soundwavs['solved'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'complete.wav'))
        self.soundwavs['opened'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'button-pressed.wav'))
        self.soundwavs['timeout'] = os.path.abspath(os.path.join(self.App.workingdir, '_sounds', 'camera-shutter.wav'))

        self.videouris = {}
        self.videouris['solved'] = os.path.abspath( os.path.join(self.App.workingdir, '_videos', 'well done.ogg'))
        self.videouris['bomb'] = os.path.abspath( os.path.join(self.App.workingdir, '_videos', 'hammer.ogg'))

        #self.create_player()


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

class Player:
    def __init__(self):
        #self.player = Gst.ElementFactory.make("playbin")
        pass

    def play_the_sound(self, theuri):
        self.player = Gst.parse_launch ("playbin uri=" + theuri)
        self.isplaying = True
        self.player.set_state(Gst.State.PLAYING)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.player.set_state(Gst.State.VOID_PENDING)
        if t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.player.set_state(Gst.State.VOID_PENDING)

class VideoPlayer:
    def __init__( self, widget, theuri, thecallback):
        self.movie_window = widget
        self.thecallback = thecallback
        self.xid = self.movie_window.get_property('window').get_xid()
        #print('xid', self.xid)
        self.is_playing = False
        self.paused = False
        self.stoped = True
        uri = file_to_local_uri(theuri)
        #self.player = Gst.parse_launch ("playbin uri=file://" + theuri)
        self.player = Gst.parse_launch ("playbin uri=" + uri)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        #bus.connect("sync-message::element::prepare-window-handle", self.on_bus_prepare_window_handle)
        bus.connect("sync-message::element", self.on_sync_message)

    def new_uri(self, theuri):
        uri = file_to_local_uri(theuri)
        if self.is_playing:
            self.stopb()
        #self.player = Gst.parse_launch ("playbin uri=file://" + theuri)
        #self.player.unlink()
        self.player = Gst.parse_launch ("playbin uri=" + uri)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        #bus.connect("sync-message::element::prepare-window-handle", self.on_bus_prepare_window_handle)
        bus.connect("sync-message::element", self.on_sync_message)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            if not self.stoped:
                self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)
                self.player.set_state(Gst.State.PLAYING)
            #self.is_playing = False
            #self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)
            self.player.set_state(Gst.State.NULL)
            self.is_playing = False
            #.button.set_label("Start")

    def on_sync_message(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            #print('self.xid',self.xid)
            imagesink = message.src
            #imagesink.set_property("force-aspect-ratio", True)
            #print('imagesink', imagesink)
            #print('imagesink', imagesink.videobox)
            Gdk.threads_enter()
            #print('1set_window_handle', imagesink)
            imagesink.set_window_handle(self.xid)
            #imagesink.fill(34,139,34,1)
            #print('2set_window_handle', imagesink)
            Gdk.threads_leave()

    def startb(self):
        self.player.set_state(Gst.State.PLAYING)
        self.stoped = False
        self.paused = False
        self.is_playing = True

    def continueb(self):
        self.player.set_state(Gst.State.PLAYING)
        self.paused = False
        self.is_playing = True

    def pauseb(self):
        #print('pausing...')
        self.player.set_state(Gst.State.PAUSED)
        self.paused = True
        self.is_playing = False
        #print('paused')

    def stopb(self):
        self.player.set_state(Gst.State.NULL)
        self.stoped = True
        self.paused = False
        self.is_playing = False

    def seek(self,time):
        self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, time)

def file_to_local_uri(filename):
    filepath = os.path.abspath(filename)
    drive, filepath = os.path.splitdrive(filepath)
    filepath = parse.quote(filepath.replace(os.sep, '/'))
    return 'file://%s%s' % (drive, filepath)
