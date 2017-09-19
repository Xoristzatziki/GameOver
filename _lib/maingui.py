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
from _lib import game #board of running game
from _lib import media #Loader of icons and sounds
from _lib import creategames #GUI for creating new puzzles
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
        self.gamesplayed = {}
        self.helps = 0
        self.lastresult = ''

class MainGui(AbstractGui):
    def __init__( self, myApp, gladefilename, otherwidjets = (),parent = None, mainbox=None):
        AbstractGui.__init__(self, myApp, gladefilename, otherwidjets=otherwidjets, mainbox=mainbox, savemysettings=self.savemysetings, clearing=self.clearing)
        self.App = myApp
        self.Appdir = myApp.workingdir

        self.mymedia = media.MyMedia(myApp, CELLSIZE)

        self.connect("key-press-event", self.somekeypressed)
        self.datadir = os.path.abspath( os.path.join(myApp.workingdir, '_data'))

        self.games = strings.Games(self.datadir)
        self.hints = strings.Hints(self.datadir)

        self.initialising = True
        self.hasgame = False
        self.gameruns = False
        self.clearonexit = False
        self.resizing = False
        self.gamegrid =  None
        self.gameicongrid = self.mybuilder.get_object('gridforsolution')
        self.newgame = None
        self.givinggift = None

        self.scoredata = GameScore()
        #self.show_score()

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

        self.initialising = False

########################################################################
#
#              INITIALIZING
#
########################################################################
    def load_games(self):
        with open(os.path.join(self.App.workingdir, '_data', 'gamedata'), mode='rt', encoding='utf-8') as f:
            alllines = f.readlines()
        self.allgames = {}
        xcounter = 0
        for line in alllines:
            if len(line.strip()):
                splittedline = line.split(',')
                #agame = {}
                #agame['name'] = splittedline[0]
                #agame['size'] = int(splittedline[1])
                #agame['nums for rows'] = tuple([int(x) for x in splittedline[2:])
                #agame['timetocomplete'] = 20
                 #= (17, 10, 4, 10, 17)
                self.allgames[xcounter] = {'name': splittedline[0],
                        'size': int(splittedline[1]),
                        'nums for rows': tuple([int(x) for x in splittedline[2:]])}
                xcounter += 1

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
            print(self.is_maximized())
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

        except Exception as e:
            print('e2',e)

    def clearing(self):
        pass
        #print('clearing')

########################################################################
#
#              START NEW GAME
#
########################################################################
    def on_buttonstartgame_clicked(self, *args):
        self.start_a_game()

    def start_a_game(self):
        self.hide_last_game()
        agame = self.games.get_a_game()
        ahint = self.hints.get_a_hint()
        agame['timetocomplete'] = 30
        self.onegame = game.Game(self.App, self, agame, self.mymedia, CELLSIZE, ahint)
        _result = self.onegame.run()
        self.onegame.destroy()
        self.set_score(_result)
        self.mybuilder.get_object('buttonstartgame').set_sensitive(self.scoredata.lifes > 0)


########################################################################
#
#              SET-SHOW RESULTS
#
########################################################################
    def show_solution(self, result):
        #print('showing solution ===================================')
        gamecells = result.gamecells
        inverted = result.inverted
        boardonesize = result.thegame['size']
        labelgamename = self.mybuilder.get_object('labelgamename')
        labelgamename.set_label('You managed to find: ' + result.thegame['name'])
        labelgamename.set_visible(True)

        eb = self.mybuilder.get_object('eventboxforsolution')

        self.gameicongrid = Gtk.Grid()
        eb.add(self.gameicongrid)

        for rowcounter in range(boardonesize):
            for colcounter in range(boardonesize):
                cellnumber = colcounter + (rowcounter * boardonesize)
                if gamecells[cellnumber]['hasbomb'] ^ inverted:
                    img = Gtk.Image.new_from_file(self.blackimagefilename)
                else:
                    img = Gtk.Image.new_from_file(self.whiteimagefilename)
                self.gameicongrid.attach(img, rowcounter, colcounter, 1, 1)
                img.set_visible(True)
                img.set_halign(Gtk.Align.START)
                img.set_valign(Gtk.Align.START)
                img.set_hexpand(True)
                img.set_vexpand(True)
        self.gameicongrid.set_halign(Gtk.Align.START)
        self.gameicongrid.set_valign(Gtk.Align.START)
        self.gameicongrid.set_hexpand(True)
        self.gameicongrid.set_vexpand(True)

        self.gameicongrid.set_visible(True)
        eb.set_visible(True)

    def set_score(self, result):
        self.scoredata.gamesplayed[len(self.scoredata.gamesplayed) + 1 ] = result.thegame
        self.scoredata.lastresult = result.result
        if result.result == 'Solved!':
            self.show_solution(result)
            self.scoredata.score += result.remainingtime // 10
        else:
            self.scoredata.lifes -= 1
            self.mybuilder.get_object('labelgamename').set_label('Bad Robot!')
            self.scoredata.score -= 500
            if self.scoredata.score < 0:
                self.scoredata.score = 0
        self.show_score()

    def show_score(self):
        self.mybuilder.get_object('labellifes').set_label(str(self.scoredata.lifes))
        self.mybuilder.get_object('labelscore').set_label(locale.format_string('%0d', self.scoredata.score, grouping = True))
        self.mybuilder.get_object('labelgamesplayed').set_label(str(len(self.scoredata.gamesplayed)))
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

    def hide_last_game(self):
        self.mybuilder.get_object('labelgamename').set_label('a new game')
        if self.gameicongrid:
            self.gameicongrid.destroy()

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
        pass

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
        creategameswindow = creategames.CreateGame(self.App, 'creategames.glade', gladenongraphicstuple, mainbox='grid1',
                thesize = thenewsize, cellsize = CELLSIZE, mymedia = self.mymedia, parent = self)
        creategameswindow.set_position(Gtk.WindowPosition.CENTER)
        response = creategameswindow.run()
        print('response',response)
        creategameswindow.destroy()


########################################################################
#
#              OTHER
#
########################################################################
    def on_buttontest2_clicked(self, *args):
        pass

    def on_buttontest1_clicked(self, *args):
        pass


########################################################################
#
#              GENERAL
#
########################################################################
