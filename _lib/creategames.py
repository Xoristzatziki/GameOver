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


from _lib.OCP import *

class CreateGame(AbstractGui):
    def __init__( self, myApp, gladefilename, otherwidjets = (),parent = None, mainbox=None, thesize = 5, cellsize = 32, mymedia = None):
        AbstractGui.__init__(self, myApp, gladefilename, parent = parent, otherwidjets=otherwidjets, mainbox=mainbox, savemysettings=self.savemysetings, clearing=self.clearing)
        self.App = myApp
        self.InstanceName = 'OCP' + self.App.appname + self.App.version + '-' + str(datetime.datetime.now()) + '-CREATEGAME'
        self.set_title('Create a game')

        self.mybuilder.get_object('labeltype').set_label(str(thesize) + 'X' + str(thesize))

        self.boardsize = thesize
        self.cellsize = cellsize
        self.mymedia = mymedia

        self.connect("key-press-event", self.somekeypressed)

        self.rowstrings = {}
        self.colstrings = {}
        self.gamegrid = None
        self.icongrid = None


        self.blackimg = Gtk.Image.new_from_pixbuf(self.mymedia.images['black'])
        self.whiteimg = Gtk.Image.new_from_pixbuf(self.mymedia.images['white'])

        self.blackicon = Gtk.Image().new_from_pixbuf(self.blackimg.get_pixbuf().scale_simple(4, 4, GdkPixbuf.InterpType.BILINEAR))
        self.whiteicon = Gtk.Image().new_from_pixbuf(self.whiteimg.get_pixbuf().scale_simple(4, 4, GdkPixbuf.InterpType.BILINEAR))

        self.initialize_grids()

    def savemysetings(self):
        pass

    def clearing(self):
        pass

    def initialize_grids(self):
        if self.gamegrid:
            self.gamegrid.destroy()
            self.icongrid.destroy()
        for xcounter in range(self.boardsize):
            self.rowstrings[xcounter] = { 'label': '0', 'widget': None}
            self.colstrings[xcounter] = { 'label': '0', 'widget': None}
        self.gamecells = {}
        self.create_empty_grids()


    def create_empty_grids(self):
        thewindowgrid = self.mybuilder.get_object('grid1')
        #print(thewindowgrid.Width)
        icongrid = Gtk.Grid()
        thewindowgrid.attach(icongrid, 0, 2, 1, 1)
        self.icongrid = icongrid
        gamegrid = Gtk.Grid()
        thewindowgrid.attach_next_to(gamegrid,self.icongrid, Gtk.PositionType.RIGHT, 1, 1)
        self.gamegrid = gamegrid
        #print(self.icongrid, self.gamegrid)
        gamegrid.get_style_context().add_class('makeitgreen')

        gamegrid.set_column_spacing(2)
        gamegrid.set_row_spacing(2)
        gamegrid.set_halign(Gtk.Align.START)
        gamegrid.set_valign(Gtk.Align.START)
        gamegrid.set_hexpand(True)
        gamegrid.set_vexpand(True)

        icongrid.set_halign(Gtk.Align.START)
        icongrid.set_valign(Gtk.Align.START)
        icongrid.set_hexpand(True)
        icongrid.set_vexpand(True)

        for rowcounter in range(self.boardsize):
            for colcounter in range(self.boardsize):
                cellnumber = colcounter + (rowcounter * self.boardsize)

                eventbox = Gtk.EventBox()
                gamegrid.attach(eventbox, rowcounter, colcounter, 1, 1)

                eventbox.set_name('E' + str(cellnumber))
                eventbox.set_size_request(self.cellsize, self.cellsize)
                eventbox.set_halign(Gtk.Align.START)
                eventbox.set_valign(Gtk.Align.START)
                eventbox.set_hexpand(True)
                eventbox.set_vexpand(True)
                self.other_set_bg(eventbox)
                eventbox.connect("button-release-event", self.on_any_cell_button_released)
                eventbox.set_visible(True)

                img = Gtk.Image.new_from_pixbuf(self.blackimg.get_pixbuf())
                eventbox.add(img)

                iconimg = Gtk.Image.new_from_pixbuf(self.blackicon.get_pixbuf())
                icongrid.attach(iconimg, rowcounter, colcounter, 1, 1)

                img.set_name('I' + str(cellnumber))
                img.set_visible(True)
                img.set_halign(Gtk.Align.CENTER)
                img.set_valign(Gtk.Align.CENTER)
                img.set_hexpand(True)
                img.set_vexpand(True)
                self.other_set_bg(img)

                iconimg.set_visible(True)
                iconimg.set_halign(Gtk.Align.CENTER)
                iconimg.set_valign(Gtk.Align.CENTER)
                iconimg.set_hexpand(True)
                iconimg.set_vexpand(True)
                self.other_set_bg(iconimg)

                self.gamecells[cellnumber]={'eventbox':eventbox, 'imgwidget': img,
                    'imgname': 'black', 'hasbomb': True, 'iconwidget': iconimg,
                    'lucky' : 0}

            label = Gtk.Label(self.rowstrings[rowcounter]['label'])
            gamegrid.attach(label, colcounter+1, rowcounter,1,1)
            self.rowstrings[rowcounter]['widget'] = label

            label.set_visible(True)
            label.set_halign(Gtk.Align.START)
            label.set_valign(Gtk.Align.CENTER)
            label.set_hexpand(True)
            label.set_vexpand(True)
            label.get_style_context().add_class('makeitgreen')

            label = Gtk.Label(self.colstrings[rowcounter]['label'])
            gamegrid.attach(label, rowcounter, colcounter+1,1,1)
            self.colstrings[rowcounter]['widget'] = label

            label.set_visible(True)
            label.set_halign(Gtk.Align.CENTER)
            label.set_valign(Gtk.Align.START)
            label.set_hexpand(True)
            label.set_vexpand(True)
            label.get_style_context().add_class('makeitgreen')

            gamegrid.set_visible(True)
            icongrid.set_visible(True)
            gamegrid.get_style_context().add_class('makeitwhite')

    def on_any_cell_button_released(self, widget, *args):
        buttonreleased = args[0].button
        ebname = widget.get_name()
        cellnumber = int(ebname[1:])
        if self.gamecells[cellnumber]['hasbomb']:
            self.gamecells[cellnumber]['imgwidget'].set_from_pixbuf(self.whiteimg.get_pixbuf())
            self.gamecells[cellnumber]['iconwidget'].set_from_pixbuf(self.whiteicon.get_pixbuf())
            self.gamecells[cellnumber]['hasbomb'] = False
        else:
            self.gamecells[cellnumber]['imgwidget'].set_from_pixbuf(self.blackimg.get_pixbuf())
            self.gamecells[cellnumber]['iconwidget'].set_from_pixbuf(self.blackicon.get_pixbuf())
            self.gamecells[cellnumber]['hasbomb'] = True
        self.update_hints()

    def on_buttontest1_clicked(self, *args):
        pass

    def update_hints(self):
        for rowcounter in range(self.boardsize):
            rowones = 0
            rowpreviousvalue = 0
            rowcountingones = 0
            rowstring = ''
            for colcounter in range(self.boardsize):
                cellnumber = rowcounter + (colcounter * self.boardsize)
                cellvalue = not self.gamecells[cellnumber]['hasbomb']
                if cellvalue:
                    if rowpreviousvalue == 1:
                        rowcountingones += 1
                    else:
                        if rowcountingones > 0:
                            rowstring += str(rowcountingones) + '-'
                        else:
                            rowstring += '-'
                        rowcountingones = 1
                rowpreviousvalue = cellvalue
            if rowcountingones > 0:
                rowstring += str(rowcountingones) + '-'
            rowstring = rowstring.strip(' -')
            if rowstring == '': rowstring = '0'
            self.rowstrings[rowcounter]['label'] = rowstring
            self.rowstrings[rowcounter]['widget'].set_label(rowstring)
        for colcounter in range(self.boardsize):
            colones = 0
            colpreviousvalue = 0
            colcountingones = 0
            colstring = ''
            for rowcounter in range(self.boardsize):
                cellnumber = rowcounter + (colcounter * self.boardsize)
                cellvalue = not self.gamecells[cellnumber]['hasbomb']
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
            self.colstrings[colcounter]['label'] = colstring
            self.colstrings[colcounter]['widget'].set_label(colstring)

    def other_set_bg(self, widget):
        style_provider = Gtk.CssProvider()
        stylecssfile = os.path.abspath( os.path.join(self.App.workingdir, '_css', 'style1.css'))
        css = open(stylecssfile, 'rb')
        css_data = css.read()
        css.close()
        style_provider.load_from_data(css_data)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        widget.get_style_context().add_class("colorize")

    def get_current_numbers(self):
        thenumlist = []
        for rowcounter in range(self.boardsize):
            binstr = ''
            for colcounter in range(self.boardsize):
                cellnumber = rowcounter + (colcounter * self.boardsize)
                cellvalue = self.gamecells[cellnumber]['hasbomb']
                binstr += '0' if cellvalue else '1'
            thenumlist.append(int(binstr,2))
        #print(thenumlist)
        return tuple(thenumlist)

    def save_game(self):
        self.create_game_for_save()

    def create_game_for_save(self):
        strtowrite = '"' + self.mybuilder.get_object('entrynewname').get_text() + '", '
        strtowrite += str(self.boardsize) + ', '
        #nums = [str(x) for x in self.get_current_numbers()]
        #for xcounter in range(self.boardsize):
        strtowrite += ','.join([str(x) for x in self.get_current_numbers()])
        with open(os.path.join(self.App.workingdir, '_data', 'gamedata'), mode='a+t', encoding='utf-8') as f:
            f.write('\n' + strtowrite)

    def on_bsave_clicked(self, *args):
        self.save_game()
        Msg(self, 'Game Saved!')
        print('saved')
        self.hideme('saved')

    def on_entrynewname_changed(self, *args):
        self.mybuilder.get_object('bsave').set_sensitive(len(self.mybuilder.get_object('entrynewname').get_text().strip()))

    def somekeypressed(self, *args):
        txt = Gdk.keyval_name(args[1].keyval)
        if type(txt) == type(None):
            return
        #print('args[1].keyval',txt,self.mybuilder.get_object('thetabber').get_current_page())
        #print(args[0].get_name())
        txt = txt.replace('KP_', '')
        dummy = False
        if dummy:
            print(args[0])

    def on_buttonrestart_clicked(self, *args):
        if not AreYouSure(self, 'You will lose all modifications!\nReally reset?'):
            return
        self.initialize_grids()
        self.mybuilder.get_object('entrynewname').set_text('')
