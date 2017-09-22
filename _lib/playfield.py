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

import pyaudio
import wave

import threading
import random

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gst

#Gst.init(None)

from _lib.OCP import *

from _lib.media import Player as localplayer


#from contextlib import contextmanager

ABANDONED = 'Abandoned!'

CHUNK = 1024

class ReturnParameter:
    def __init__( self):
        self.result = ABANDONED
        self.inverted = False
        self.puzzlecells = {}
        self.remainingtime = 0
        self.thepuzzle = None

class Puzzle(Gtk.Window):
    def __init__( self, myApp, parent, apuzzle, mymedia, cellsize, hint):
        Gtk.Window.__init__(self, name = 'A Field', title = 'Game Over - Playground')
        self.App = myApp
        self.set_modal(True)
        self.set_transient_for(parent)
        self.puzzleruns = False
        self.InstanceName = 'OCP' + self.App.appname + self.App.version + '-' + str(datetime.datetime.now()) + '-AGAME'

        self.Appdir = myApp.workingdir

        self.mymedia = mymedia
        #self.myplayer = theplayer
        #self.myplayer = localplayer()
        self.cellsize = cellsize
        self.mybuilder = Gtk.Builder()


        mainbox = 'onegamewindowgrid'
        self.connect("hide", self.hideme)

        self.load_styles()

        self.puzzledata = apuzzle
        self.timetocomplete = int(self.puzzledata['timetocomplete'] * 1000)
        self.remainingtime = self.timetocomplete

        self.boardsize = int(self.puzzledata['size'])
        self.remainingempty = 0
        self.rowstrings = []
        self.colstrings = []
        self.puzzlecells = {}
        self.rowdata = {}
        self.returnparameter = ReturnParameter()
        self.returnparameter.thepuzzle = apuzzle
        for xcounter in range(self.boardsize):
            self.rowdata[xcounter] = int(self.puzzledata['nums for rows'][xcounter])

        gladename = os.path.abspath( os.path.join(myApp.workingdir, '_glades', 'playfield.glade'))
        self.mybuilder = Gtk.Builder()
        _tmplist = []#[x for x in otherwidjets]
        _tmplist.append( mainbox )
        b = tuple(_tmplist)
        #b.extend(zip(otherwidjets))
        #print (b)
        self.mybuilder.add_objects_from_file(os.path.join(self.Appdir, '_glades', gladename), b )
        #print('added more widgets')
        #print(b)

        self.add(self.mybuilder.get_object(mainbox))
        self.mybuilder.connect_signals(self)

        self.mybuilder.get_object('labelforhint').set_label(hint)
        self.create_data_and_grid()

        self.mybuilder.get_object('onegamewindowgrid').get_style_context().add_class('makeitgrass')

########################################################################
#
#              INITIALIZING
#
########################################################################
    def load_styles(self):
        style_provider = Gtk.CssProvider()
        stylecssfile = os.path.abspath(os.path.join(self.Appdir, '_css', 'style.css'))
        #print(stylecssfile)
        css = open(stylecssfile, 'rb')
        css_data = css.read()
        css.close()
        style_provider.load_from_data(css_data)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def create_data_and_grid(self):
        thecellforrowstrings = self.mybuilder.get_object('eventboxforrowstrings')
        thecellforrowstrings.get_style_context().add_class('makeitgrass')
        thecellforcolstrings = self.mybuilder.get_object('eventboxforcolstrings')
        thecellforcolstrings.get_style_context().add_class('makeitgrass')

        puzzlegrid = self.mybuilder.get_object('gridforpuzzle')
        puzzlegrid.get_style_context().add_class('bluebg')
        rowstringsgrid = self.mybuilder.get_object('gridforrowstrings')
        colstringsgrid = self.mybuilder.get_object('gridforcolstrings')

        colones = 0
        colpreviousvalue = 0
        colcountingones = 0
        colstring = ''
        rowbins = []
        random.seed()
        _invert = (random.random() >= 0.5)
        self.returnparameter.inverted = _invert
        #print(_invert)
        for xcounter in range(self.boardsize):
            rowint = int(self.rowdata[xcounter])
            rowbinstr = format(rowint, '0' + str(self.boardsize) + 'b')
            rowbinnums = []
            for ycounter in range(self.boardsize):
                rowbinnums.append(rowbinstr[ycounter] == '0' if _invert else rowbinstr[ycounter] != '0')
            rowbins.append(rowbinnums)
            #print(rowint, rowbinnums)#, _invert)
        for rowcounter in range(self.boardsize):
            rowint = self.rowdata[rowcounter]
            rowones = 0
            rowpreviousvalue = 0
            rowcountingones = 0
            rowstring = ''
            for colcounter in range(self.boardsize):
                cellnumber = rowcounter + (colcounter * self.boardsize)
                cellvalue = rowbins[rowcounter][colcounter]
                if cellvalue:
                    self.puzzlecells[cellnumber] = {'hasbomb' : False}
                    self.remainingempty += 1
                    if rowpreviousvalue == 1:
                        rowcountingones += 1
                    else:
                        if rowcountingones > 0:
                            rowstring += str(rowcountingones) + '-'
                        else:
                            rowstring += '-'
                        rowcountingones = 1
                else:
                    self.puzzlecells[cellnumber] = {'hasbomb' : True}
                rowpreviousvalue = cellvalue
            #grid
                eventbox = Gtk.EventBox()
                puzzlegrid.attach(eventbox,colcounter,rowcounter,1,1)

                eventbox.set_name('E' + str(cellnumber))
                eventbox.set_size_request(self.cellsize, self.cellsize)
                eventbox.set_halign(Gtk.Align.START)
                eventbox.set_valign(Gtk.Align.START)
                eventbox.set_hexpand(True)
                eventbox.set_vexpand(True)
                #self.other_set_bg(eventbox)
                #eventbox.get_style_context().add_class('uncolorize')
                eventbox.connect("button-release-event", self.on_any_cell_button_released)
                eventbox.set_visible(True)

                img = Gtk.Image.new_from_pixbuf(self.mymedia.images['black'])
                eventbox.add(img)

                img.set_name('I' + str(cellnumber))
                img.set_visible(True)
                img.set_halign(Gtk.Align.CENTER)
                img.set_valign(Gtk.Align.CENTER)
                img.set_hexpand(True)
                img.set_vexpand(True)
                #self.other_set_bg(img)
                #img.get_style_context().add_class('uncolorize')
                #print('0' if self.puzzlecells[cellnumber]['hasbomb'] else '1',end = ',')

                self.puzzlecells[cellnumber]={'eventbox':eventbox, 'imgwidget': img,
                    'imgname': 'black', 'hasbomb': self.puzzlecells[cellnumber]['hasbomb'],
                    'lucky' : 0}
            #print()
            if rowcountingones > 0:
                rowstring += str(rowcountingones) + '-'
            rowstring = rowstring.strip(' -')
            if rowstring == '': rowstring = '0'
            #print(rowcounter, rowstring)
            self.rowstrings.append(rowstring)
            self.returnparameter.puzzlecells = self.puzzlecells
        #print('for rows')
        for colcounter in range(self.boardsize):
            colones = 0
            colpreviousvalue = 0
            colcountingones = 0
            colstring = ''
            for rowcounter in range(self.boardsize):
                #print(rowcounter, 'rowcounter')
                cellnumber = rowcounter + (colcounter * self.boardsize)
                cellvalue = rowbins[rowcounter][colcounter]
                if cellvalue:
                    if colpreviousvalue == 1:
                        colcountingones += 1
                    else:
                        if colcountingones > 0:
                            colstring += str(colcountingones) + '\n'
                        else:
                            colstring +=  '\n'
                        colcountingones = 1
                else:
                    pass
                colpreviousvalue = cellvalue
            if colcountingones > 0:
                colstring += str(colcountingones) + '\n'
            colstring = colstring.strip('\n')
            if colstring == '': colstring = '0'
            self.colstrings.append(colstring)
        puzzlegrid.set_visible(True)
        for xcounter in range(self.boardsize):

            label = Gtk.Label(self.rowstrings[xcounter])
            rowstringsgrid.attach(label, 0, xcounter, 1,1)
            label.set_visible(True)
            label.set_halign(Gtk.Align.START)
            label.set_valign(Gtk.Align.CENTER)
            label.set_hexpand(True)
            label.set_vexpand(True)
            label.get_style_context().add_class('linelabel')


            label = Gtk.Label(self.colstrings[xcounter])
            colstringsgrid.attach(label, xcounter, 0, 1,1)
            label.set_visible(True)
            label.set_halign(Gtk.Align.CENTER)
            label.set_valign(Gtk.Align.START)
            label.set_hexpand(True)
            label.set_vexpand(True)
            label.get_style_context().add_class('linelabel')

    def start_puzzle(self):
        self.puzzleruns = True
        GLib.timeout_add(1000, self.update_timer)

########################################################################
#
#              GAME RUN BUTTONS
#
########################################################################
    def on_any_cell_button_released(self, widget, *args):
        if not self.puzzleruns:
            return
        buttonreleased = args[0].button
        ebname = widget.get_name()
        #print(ebname)
        cellnumber = int(ebname[1:])
        _bombed = False

        if buttonreleased == 1:#left button pressed to open it
            if self.puzzlecells[cellnumber]['imgname'] == 'flag':
                return
            if self.puzzlecells[cellnumber]['hasbomb']:
                self.bomb_found(widget, cellnumber)
            elif self.puzzlecells[cellnumber]['lucky']:
                pass#TODO: give gift
            elif self.puzzlecells[cellnumber]['imgname'] == 'white':
                return
            else:
                self.open_cell(widget, cellnumber)
        elif buttonreleased == 3:
            #self.rightbuttonpressed(widget,row,col)
            if self.puzzlecells[cellnumber]['lucky']:
                self.give_gift(widget, cellnumber)
            self.flag_cell(widget, cellnumber)

    def on_buttonusehelp_clicked(self, *args):
        pass

########################################################################
#
#              GAME RUN FUNCTIONS
#
########################################################################
    def open_cell(self, widget, cellnumber):
        timeremaining = self.remainingtime
        if self.puzzlecells[cellnumber]['lucky']:
            self.give_gift(widget, cellnumber)
        self.ring('opened')
        self.puzzlecells[cellnumber]['imgname'] = 'white'
        self.set_new_image(cellnumber)
        self.remainingempty -= 1
        if self.remainingempty <= 0:
            self.returnparameter.remainingtime = self.remainingtime
            self.returnparameter.result = 'Solved!'
            self.stop_puzzle()
            #self.ring('solved')
            return

        self.remainingtime += 500
        self.update_progressbar()

    def bomb_found(self, widget, cellnumber):
        #print(cellnumber, 'bomb')
        if self.puzzlecells[cellnumber]['lucky']:
            self.give_gift(widget, cellnumber)
        else:
            self.returnparameter.result = 'Bomb found.'
            self.stop_puzzle()
            #self.ring('bomb')
            #self.puzzlecells[cellnumber]['imgname'] = 'exploded'
            #self.set_new_image(cellnumber)

    def give_gift(self, widget, cellnumber):
        self.ring('gift')
        #TODO:give some gift...

    def flag_cell(self, widget, cellnumber):
        if self.puzzlecells[cellnumber]['imgname'] == 'flag':
            self.puzzlecells[cellnumber]['imgname'] = 'black'
        else:
            self.puzzlecells[cellnumber]['imgname'] = 'flag'
        self.set_new_image(cellnumber)

    def stop_puzzle(self):
        self.puzzleruns = False

    def time_over(self):
        self.puzzleruns = False
        self.returnparameter.result = 'Time over!'
        self.hideme()

    def update_timer(self):
        #progressbarfortime
        if not self.puzzleruns:
            #myprint('==========says game not running in  update timer')
            return False
        if self.remainingtime > self.timetocomplete:
            self.remainingtime = self.timetocomplete
        self.remainingtime -= 1000
        if self.remainingtime < 0 :
            #myprint('says time over')
            self.time_over()
            return False
        self.ring('timebell')
        #myprint('did bell ringed?')
        self.update_progressbar()
        return True

    def update_progressbar(self):
        if self.remainingtime > self.timetocomplete:
            self.remainingtime = self.timetocomplete
        _fraction = 1 - (1/self.timetocomplete) * self.remainingtime
        self.mybuilder.get_object('progressbarfortime').set_fraction(_fraction)
        self.mybuilder.get_object('progressbarfortime').set_text(str(int(self.remainingtime / 1000)) + ' s')

########################################################################
#
#              SOUNDS
#
########################################################################
    def ring(self, soundfor):
        threading.Thread(target=self.ring_in_thread, args=(soundfor,)).start()

    def ring_in_thread(self, soundfor):
        _thesoundfile = self.mymedia.sounduris[soundfor]
        localplayer().play_the_sound(_thesoundfile)
        #print(threading.active_count())

########################################################################
#
#              IMAGES
#
########################################################################
    def set_new_image(self, cellnumber):
        self.puzzlecells[cellnumber]['imgwidget'].set_from_pixbuf(self.mymedia.images[self.puzzlecells[cellnumber]['imgname']])

########################################################################
#
#              WINDOW
#
########################################################################
    def run(self):
        #now we can show the window
        self.show_all()
        self.mybuilder.get_object('buttonusehelp').set_sensitive(False)
        self.set_resizable(False)
        self.start_puzzle()
        #loop eternaly
        while True:
            #if we want to exit
            if not self.puzzleruns:
                #print('wecanexitnow')
                #break the loop
                break
            #else...
            #give others a change...
            while Gtk.events_pending():
                Gtk.main_iteration()
        #we can now return to calling procedure
        #can return any variable we want
        #or we can check the widgets and/or variables
        #from inside calling procedure
        #print('from abstract',self.returnparameter)
        return self.returnparameter

    def hideme(self, *args):
        self.puzzleruns = False
        #if self.returnparameter.result == ABANDONED:
            #self.ring('timeout')
        self.wecanexitnow = True

def play_simple_sound(theuri):
    player = Gst.parse_launch ("playbin uri=" + theuri)
    player.set_state(Gst.State.PLAYING)


#@contextmanager
#def silence_stdout():
    #new_target = open(os.devnull, "w")
    #old_target, sys.stdout = sys.stdout, new_target
    #try:
        #yield new_target
    #finally:
        #sys.stdout = old_target

def play_with_pyaudio(thefile):
    new_target = open(os.devnull, "w")
    old_target, sys.stdout = sys.stdout, new_target
    old_err_target, sys.stderr = sys.stderr, new_target
    try:
        wf = wave.open(thefile, 'rb')
        # instantiate PyAudio (1)
        p = pyaudio.PyAudio()
        # open stream (2)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
        # read data
        data = wf.readframes(CHUNK)
        # play stream (3)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(CHUNK)

        # stop stream (4)
        stream.stop_stream()
        stream.close()

        # close PyAudio (5)
        p.terminate()
    finally:
        sys.stdout = old_target
        sys.stderr = old_err_target
