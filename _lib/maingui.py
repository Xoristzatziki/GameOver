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
# with OCPcompanion. If not, see <http://www.gnu.org/licenses/>.

#ffmpeg is required for sounds.

import os, sys
import subprocess

import json
import locale
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
from _lib import playfield #board of running game
from _lib import media #Loader of icons and sounds
from _lib import createpuzzles #GUI for creating new puzzles
from _lib import strings #Loader of puzzles and hint strings

CELLSIZE = 32

def myprint(*args):
    #pass
    print(args)

class GameScore():
    def __init__( self):
        self.score = 0
        self.lifes = 3
        self.difficulty = 0
        self.puzzlesplayed = {}
        self.helps = 0
        self.lastresult = ''

class MainGui(AbstractGui):
    def __init__( self, myApp, gladefilename, otherwidjets = (),parent = None, mainbox=None):
        AbstractGui.__init__(self, myApp, gladefilename, otherwidjets=otherwidjets, mainbox=mainbox, savemysettings=self.savemysetings, clearing=self.clearing)
        self.App = myApp
        self.Appdir = myApp.workingdir

        self.mymedia = media.MyMedia(myApp, CELLSIZE)
        #self.myplayer = media.Player()

        self.connect("key-press-event", self.somekeypressed)
        self.connect("realize", self.on_window_realize)
        self.datadir = os.path.abspath( os.path.join(myApp.workingdir, '_data'))

        self.puzzles = strings.Puzzles(self.datadir)
        self.hints = strings.Hints(self.datadir)

        self.initialising = True
        self.haspuzzle = False
        self.gameruns = False
        self.clearonexit = False
        self.resizing = False
        self.puzzleicongrid = self.mybuilder.get_object('gridforsolution')
        self.newgame = None
        self.videoplayer = None
        self.scoredata = GameScore()

        self.showvideos = (self.MySettings.readconfigvalue('Video','showvideos','True').strip()  == 'True')
        #print('loaded novideo', self.showvideos)
        #self.mybuilder.get_object('checkvideotoggle').set_active(self.novideo)
        self.mybuilder.get_object('imageGO').set_from_file(self.mymedia.icons['logo'])


        _W = int(self.MySettings.readconfigvalue('windowMain','width',str(self.get_screen().get_width()-100)))
        _H = int(self.MySettings.readconfigvalue('windowMain','height', str(self.get_screen().get_height()-100)) )
        #print(_W, self.get_screen().get_width())

        self.resize(_W,_H)
        if self.MySettings.readconfigvalue('windowMain','maximized','False')  == 'True':
              self.maximize()

        self.blackimagefilename = os.path.abspath( os.path.join(myApp.workingdir, '_icons', 'black.png'))
        self.whiteimagefilename = os.path.abspath( os.path.join(myApp.workingdir, '_icons', 'white.png'))
        self.explodedimagefilename = os.path.abspath( os.path.join(myApp.workingdir, '_icons', 'exploded.svg'))
        self.flagimagefilename = os.path.abspath( os.path.join(myApp.workingdir, '_icons', 'flag.svg'))

        self.load_styles()


        self.mybuilder.get_object('eventboxforsolution').set_visible(False)
        self.mybuilder.get_object('gridforsolution').set_visible(False)
        self.mybuilder.get_object('gridforsolution').set_visible(False)

        self.mybuilder.get_object('eventboxforsolution').get_style_context().add_class('makeitblue')
        self.mybuilder.get_object('labelforresult').get_style_context().add_class('uncolorizeR')

        self.mybuilder.get_object('gridforsolution').get_style_context().add_class('makeitblue')
        self.mybuilder.get_object('videoprojector').get_style_context().add_class('backstyle')

        self.initialising = False

########################################################################
#
#              INITIALIZING
#
########################################################################
    def load_styles(self):
        style_provider = Gtk.CssProvider()
        stylecssfile = os.path.abspath( os.path.join(self.Appdir, '_css', 'style.css'))
        css = open(stylecssfile, 'rb')
        css_data = css.read()
        css.close()
        style_provider.load_from_data(css_data)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def savemysetings(self):
        '''Saves user preferences in the predefined conf file.

        '''
        #always remember last radio button for settings
        #print(self.mybuilder.get_object('radiobuttonkeeplast').get_active())
        if self.mybuilder.get_object('radiobuttonkeeplast').get_active():
            self.MySettings.writeconfigvalue('Option', 'lastsetting', '1')
            return
        try:
            W, H = self.get_size()
            #print(self.is_maximized())
            if self.mybuilder.get_object('radiobuttonclearall').get_active():
                self.MySettings.writeconfigvalue('Option', 'lastsetting', '2')
                self.MySettings.deleteconfigvalue('windowMain','Width')
                self.MySettings.deleteconfigvalue('windowMain','Height')
                self.MySettings.deleteconfigvalue('windowMain','maximized')
            else:
                self.MySettings.writeconfigvalue('Option', 'lastsetting', '0')
                self.MySettings.writeconfigvalue('windowMain','Width',str(W))#.encode('utf-8')
                self.MySettings.writeconfigvalue('windowMain','Height',str(H))#.encode('utf-8')
                self.MySettings.writeconfigvalue('windowMain','maximized',str(self.is_maximized()))#.encode('utf-8')
                self.MySettings.writeconfigvalue('Video','showvideos',str(self.showvideos))
                #print('saved showvideos', self.showvideos)

        except Exception as e:
            print('e in savemysetings:',e)

    def clearing(self):
        pass
        #print('clearing')

########################################################################
#
#              START NEW GAME
#
########################################################################
    def on_buttonnextpuzzle_clicked(self, *args):
        self.start_next_puzzle()

    def reset_game(self):
        #NotYet(self)
        self.scoredata = GameScore()
        self.show_score()
        self.hide_last_puzzle()
        self.mybuilder.get_object('buttonnextpuzzle').set_sensitive(True)

    def start_next_puzzle(self):
        self.hide_last_puzzle()
        apuzzle = self.puzzles.get_a_puzzle()
        ahint = self.hints.get_a_hint()
        apuzzle['timetocomplete'] = 30
        _thepuzzle = playfield.Puzzle(self.App, self, apuzzle, self.mymedia, CELLSIZE, ahint)
        _result = _thepuzzle.run()
        _thepuzzle.destroy()
        self.set_score(_result)
        self.mybuilder.get_object('buttonnextpuzzle').set_sensitive(self.scoredata.lifes > 0)
        self.gameruns = self.mybuilder.get_object('buttonnextpuzzle').get_sensitive()
        #print('self.gameruns', self.gameruns)

########################################################################
#
#              SET-SHOW RESULTS
#
########################################################################
    def show_solution(self, result):
        #print('showing solution ===================================')
        puzzlecells = result.puzzlecells
        inverted = result.inverted
        boardonesize = result.thepuzzle['size']
        _label = self.mybuilder.get_object('labelpuzzlename')
        _label.set_label('You managed to find: ' + result.thepuzzle['name'])
        _label.set_visible(True)

        eb = self.mybuilder.get_object('eventboxforsolution')

        self.puzzleicongrid = Gtk.Grid()
        eb.add(self.puzzleicongrid)

        for rowcounter in range(boardonesize):
            for colcounter in range(boardonesize):
                cellnumber = colcounter + (rowcounter * boardonesize)
                if puzzlecells[cellnumber]['hasbomb'] ^ inverted:
                    img = Gtk.Image.new_from_file(self.blackimagefilename)
                else:
                    img = Gtk.Image.new_from_file(self.whiteimagefilename)
                self.puzzleicongrid.attach(img, rowcounter, colcounter, 1, 1)
                img.set_visible(True)
                img.set_halign(Gtk.Align.START)
                img.set_valign(Gtk.Align.START)
                img.set_hexpand(True)
                img.set_vexpand(True)
        self.puzzleicongrid.set_halign(Gtk.Align.START)
        self.puzzleicongrid.set_valign(Gtk.Align.START)
        self.puzzleicongrid.set_hexpand(True)
        self.puzzleicongrid.set_vexpand(True)

        self.puzzleicongrid.set_visible(True)
        eb.set_visible(True)

    def set_score(self, result):
        self.scoredata.puzzlesplayed[len(self.scoredata.puzzlesplayed) + 1 ] = result.thepuzzle
        self.scoredata.lastresult = result.result
        if result.result == 'Solved!':
            self.ring('solved')
            self.play('solved')
            self.show_solution(result)
            self.scoredata.score += result.remainingtime // 10
        else:
            self.ring('bomb')
            self.play('bomb')
            self.scoredata.lifes -= 1
            self.mybuilder.get_object('labelpuzzlename').set_label('Bad Robot!')
            self.scoredata.score -= 500
            if self.scoredata.score < 0:
                self.scoredata.score = 0
        self.show_score()

    def show_score(self):
        self.mybuilder.get_object('labellifes').set_label(str(self.scoredata.lifes))
        self.mybuilder.get_object('labelscore').set_label(locale.format_string('%0d', self.scoredata.score, grouping = True))
        self.mybuilder.get_object('labelpuzzlesplayed').set_label(str(len(self.scoredata.puzzlesplayed)))
        widget = self.mybuilder.get_object('labelforresult')

        if self.scoredata.lastresult == 'Solved!':
            if widget.get_style_context().has_class('uncolorizeR'):
                pass
            else:
                widget.get_style_context().remove_class('colorizeR')
                widget.get_style_context().add_class('uncolorizeR')
        else:
            if widget.get_style_context().has_class('uncolorizeR'):
                widget.get_style_context().remove_class('uncolorizeR')
                widget.get_style_context().add_class('colorizeR')
        widget.set_label(self.scoredata.lastresult)

    def hide_last_puzzle(self):
        self.mybuilder.get_object('labelpuzzlename').set_label('a new puzzle')
        if self.videoplayer:
            self.videoplayer.stopb()
        if self.puzzleicongrid:
            self.puzzleicongrid.destroy()

########################################################################
#
#              EVENTS
#
########################################################################
    def somekeypressed(self, *args):
        #False is returned by default, so event is passed to the rest of widgets
        #print(args)
        txt = Gdk.keyval_name(args[1].keyval)
        if type(txt) == type(None):
            return
        #print('args[1].keyval',txt,self.mybuilder.get_object('thetabber').get_current_page())
        txt = txt.replace('KP_', '')
        dummy = False
        if dummy:
            if self.mybuilder.get_object('thetabber').get_current_page() == 0:
                if txt == 'space': #in ['Enter','Return']:
                    #print('self.videoplayer.is_playing',self.videoplayer.is_playing)
                    if self.videoplayer.is_playing:
                        self.pause_video()
                    elif self.videoplayer.paused:
                        self.continue_video()
                    elif self.videoplayer.stoped:
                        self.start_video()
                if txt in ['F5','F6']:
                    return self.set_new_position(txt == 'F5')

    def on_grid1_size_allocate(self, *args):
        #widget = self.mybuilder.get_object('backforvideo')
        #widget2 = self.mybuilder.get_object('videoprojector')
        widget = self.mybuilder.get_object('videoprojector')
        W = widget.get_allocated_width()
        #widget.set_height_request(int(W * (3/4)))
        widget.set_size_request(-1, int(W * (3/4)))

########################################################################
#
#              GAME BUTTONS
#
########################################################################
    def on_buttoncreatenew_clicked(self, *args):
        gladenongraphicstuple = tuple()
        thesizestr = self.mybuilder.get_object('entrysizefornew').get_text()
        thenewsize = 5
        try:
            thenewsize = int(thesizestr)
        except Exception as e:
            print('size error', e)
        if thenewsize < 5:
            thenewsize = 5
        if thenewsize > 20:
            thenewsize = 20
        createpuzzlesswindow = createpuzzles.CreatePuzzle(self.App, 'creategames.glade', gladenongraphicstuple, mainbox='grid1',
                thesize = thenewsize, cellsize = CELLSIZE, mymedia = self.mymedia, parent = self)
        createpuzzlesswindow.set_position(Gtk.WindowPosition.CENTER)
        response = createpuzzlesswindow.run()
        #print('response',response)
        createpuzzlesswindow.destroy()


########################################################################
#
#              OTHER
#
########################################################################
    def on_buttontest2_clicked(self, *args):
        Msg(self, 'something')

    def on_buttontest1_clicked(self, *args):
        self.mybuilder.get_object('buttonnextpuzzle').set_sensitive(True)

    def on_checkvideotoggle_toggled(self, *args):
        self.set_if_video()

    def on_buttonstartnewgame_clicked(self, *args):
        if self.gameruns:
            result = AreYouSure(self, 'There is a game running.\nReally abandon it?')
            if not result:
                return
        self.reset_game()

    def on_grid1_realize(self, *args):
        #self.set_if_video()
        #print('grid realized')
        pass

    def on_window_realize(self, *args):
        #update from cinf file, after window starts
        #(because we have a show all in AbstractGui)
        self.mybuilder.get_object('checkvideotoggle').set_active(self.showvideos)

        self.set_if_video()
        #print('window realized')

########################################################################
#
#              GENERAL
#
########################################################################
    def set_if_video(self):
        self.showvideos = self.mybuilder.get_object('checkvideotoggle').get_active()
        #print('now showvideos = ', self.showvideos)
        self.mybuilder.get_object('videoprojector').set_visible(self.showvideos)
        self.mybuilder.get_object('imageGO').set_visible(not self.showvideos)
        if (self.videoplayer and (not self.showvideos)):
            self.videoplayer.stopb()

    def update_videoslider(self):
        print('check if something is done else not used.')

    def ring(self, soundfor):
        threading.Thread(target=self.ring_in_thread, args=(soundfor,)).start()

    def ring_in_thread(self, soundfor):
        _thesoundfile = self.mymedia.sounduris[soundfor]
        media.Player().play_the_sound(_thesoundfile)
        #print(threading.active_count())

    def play(self, videofor):
        if self.showvideos:
            self.mybuilder.get_object('videoprojector').set_visible(True)
            uri = self.mymedia.videouris[videofor]
            widget = self.mybuilder.get_object('videoprojector')
            self.videoplayer = media.VideoPlayer(widget, uri, self.update_videoslider)
            self.videoplayer.startb()

