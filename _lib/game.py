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

import threading
import random

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import GObject


from _lib.OCP import *

ABANDONED = 'Abandoned!'

class ReturnParameter:
    def __init__( self):
        self.result = ABANDONED
        self.inverted = False
        self.gamecells = {}
        self.remainingtime = 0
        self.thegame = None

class Game(Gtk.Window):
    def __init__( self, myApp, parent, agame, mymedia, cellsize, hint):
        Gtk.Window.__init__(self, name = 'A Game', title = 'Game Over - Playground')
        self.App = myApp
        self.set_modal(True)
        self.set_transient_for(parent)
        self.gameruns = False
        self.InstanceName = 'OCP' + self.App.appname + self.App.version + '-' + str(datetime.datetime.now()) + '-AGAME'

        self.Appdir = myApp.workingdir

        self.mymedia = mymedia
        self.cellsize = cellsize
        self.mybuilder = Gtk.Builder()

        mainbox = 'onegamewindowgrid'
        self.connect("hide", self.hideme)

        self.load_styles()

        self.gamedata = agame
        self.timetocomplete = int(self.gamedata['timetocomplete'] * 1000)
        self.remainingtime = self.timetocomplete

        self.boardsize = int(self.gamedata['size'])
        self.remainingempty = 0
        self.rowstrings = []
        self.colstrings = []
        self.gamecells = {}
        self.rowdata = {}
        self.returnparameter = ReturnParameter()
        self.returnparameter.thegame = agame
        for xcounter in range(self.boardsize):
            self.rowdata[xcounter] = int(self.gamedata['nums for rows'][xcounter])

        gladename = os.path.abspath( os.path.join(myApp.workingdir, '_glades', 'game.glade'))
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

        gamegrid = self.mybuilder.get_object('gridforgame')
        gamegrid.get_style_context().add_class('bluebg')
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
                    self.gamecells[cellnumber] = {'hasbomb' : False}
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
                    self.gamecells[cellnumber] = {'hasbomb' : True}
                rowpreviousvalue = cellvalue
            #grid
                eventbox = Gtk.EventBox()
                gamegrid.attach(eventbox,colcounter,rowcounter,1,1)

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
                #print('0' if self.gamecells[cellnumber]['hasbomb'] else '1',end = ',')

                self.gamecells[cellnumber]={'eventbox':eventbox, 'imgwidget': img,
                    'imgname': 'black', 'hasbomb': self.gamecells[cellnumber]['hasbomb'],
                    'lucky' : 0}
            #print()
            if rowcountingones > 0:
                rowstring += str(rowcountingones) + '-'
            rowstring = rowstring.strip(' -')
            if rowstring == '': rowstring = '0'
            #print(rowcounter, rowstring)
            self.rowstrings.append(rowstring)
            self.returnparameter.gamecells = self.gamecells
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
        gamegrid.set_visible(True)
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

    def start_game(self):
        self.gameruns = True
        GLib.timeout_add(1000, self.update_timer)

########################################################################
#
#              GAME RUN BUTTONS
#
########################################################################
    def on_any_cell_button_released(self, widget, *args):
        if not self.gameruns:
            return
        buttonreleased = args[0].button
        ebname = widget.get_name()
        #print(ebname)
        cellnumber = int(ebname[1:])
        _bombed = False

        if buttonreleased == 1:#left button pressed to open it
            if self.gamecells[cellnumber]['imgname'] == 'flag':
                return
            if self.gamecells[cellnumber]['hasbomb']:
                self.bomb_found(widget, cellnumber)
            elif self.gamecells[cellnumber]['lucky']:
                pass#TODO: give gift
            elif self.gamecells[cellnumber]['imgname'] == 'white':
                return
            else:
                self.open_cell(widget, cellnumber)
        elif buttonreleased == 3:
            #self.rightbuttonpressed(widget,row,col)
            if self.gamecells[cellnumber]['lucky']:
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
        if self.gamecells[cellnumber]['lucky']:
            self.give_gift(widget, cellnumber)
        self.ring('opened')
        self.gamecells[cellnumber]['imgname'] = 'white'
        self.set_new_image(cellnumber)
        self.remainingempty -= 1
        if self.remainingempty <= 0:
            self.returnparameter.remainingtime = self.remainingtime
            self.returnparameter.result = 'Solved!'
            self.stop_game()
            self.ring('solved')
            return

        self.remainingtime += 500
        self.update_progressbar()

    def bomb_found(self, widget, cellnumber):
        #print(cellnumber, 'bomb')
        if self.gamecells[cellnumber]['lucky']:
            self.give_gift(widget, cellnumber)
        else:
            self.returnparameter.result = 'Bomb found.'
            self.stop_game()
            self.ring('bomb')
            #self.gamecells[cellnumber]['imgname'] = 'exploded'
            #self.set_new_image(cellnumber)

    def give_gift(self, widget, cellnumber):
        self.ring('gift')
        #TODO:give some gift...

    def flag_cell(self, widget, cellnumber):
        if self.gamecells[cellnumber]['imgname'] == 'flag':
            self.gamecells[cellnumber]['imgname'] = 'black'
        else:
            self.gamecells[cellnumber]['imgname'] = 'flag'
        self.set_new_image(cellnumber)

    def stop_game(self):
        self.gameruns = False

    def time_over(self):
        self.gameruns = False
        self.returnparameter.result = 'Time over!'
        self.hideme()

    def update_timer(self):
        #progressbarfortime
        if not self.gameruns:
            #myprint('==========says game not running in  update timer')
            return False
        if self.remainingtime > self.timetocomplete:
            self.remainingtime = self.timetocomplete
        self.remainingtime -= 1000
        if self.remainingtime < 0 :
            #myprint('says time over')
            self.time_over()
            return False
        #self.ring('timebell')
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
        _thesoundfile = self.mymedia.soundfiles[soundfor]
        subprocess.run(["ffplay", '-v', 'quiet', "-nodisp",'-hide_banner', "-autoexit", _thesoundfile], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

########################################################################
#
#              IMAGES
#
########################################################################
    def set_new_image(self, cellnumber):
        self.gamecells[cellnumber]['imgwidget'].set_from_pixbuf(self.mymedia.images[self.gamecells[cellnumber]['imgname']])

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
        self.start_game()
        #loop eternaly
        while True:
            #if we want to exit
            if not self.gameruns:
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
        self.gameruns = False
        if self.returnparameter.result == ABANDONED:
            self.ring('timeout')
        self.wecanexitnow = True
