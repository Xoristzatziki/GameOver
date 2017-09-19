#Copyright Ηλιάδης Ηλίας, 2017
#v.0.0.41
# contact http://gnu.kekbay.gr/OCPcompanion/  -- mailto:OCPcompanion@kekbay.gr
#
# This file is part of OCPcompanion.
#
# OCPcompanion is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3.0 of the License, or (at your option) any
# later version.
#
# OCPcompanion is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with OCPcompanion.  If not, see <http://www.gnu.org/licenses/>.

try:
    import sys, os
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except:
    sys.exit(1)

def YesNo(forwindow, thetitle, thequestion):
    dialog = Gtk.MessageDialog(forwindow, 0, Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.YES_NO, thetitle)
    dialog.format_secondary_text(thequestion)
    #dialog.set_transient_for(forwindow)
    response = dialog.run()
    dialog.destroy()
    return (response == Gtk.ResponseType.YES)

def AreYouSure(forwindow, thequestion):
    dialog = Gtk.MessageDialog(forwindow, 0, Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.YES_NO, 'Are You Sure?')
    dialog.format_secondary_text(thequestion)
    #dialog.set_transient_for(forwindow)
    response = dialog.run()
    dialog.destroy()
    return (response == Gtk.ResponseType.YES)

def NotYet(forwindow):
    dialog = Gtk.MessageDialog(forwindow, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "NOT YET!")
    dialog.format_secondary_text("Not yet implemented!")
    #dialog.set_transient_for(appwindow)
    dialog.run()
    dialog.destroy()

def Msg(forwindow, msg):
    dialog = Gtk.MessageDialog(forwindow, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, msg)
    #dialog.format_secondary_text("Not yet implemented!")
    #dialog.set_transient_for(appwindow)
    dialog.run()
    dialog.destroy()

