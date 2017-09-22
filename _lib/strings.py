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

import os, sys, random

class Puzzles:
    def __init__( self, datadir):
        with open(os.path.join(datadir, 'puzzledata'), mode='rt', encoding='utf-8') as f:
            alllines = f.readlines()
        self.allpuzzles = {}
        xcounter = 0
        for line in alllines:
            if len(line.strip()):
                splittedline = line.split(',')
                self.allpuzzles[xcounter] = {'name': splittedline[0][1:-1],
                        'size': int(splittedline[1]),
                        'nums for rows': tuple([int(x) for x in splittedline[2:]])}
                xcounter += 1

    def get_a_puzzle(self):
        random.seed()
        selectednum = random.randrange(len(self.allpuzzles))
        return self.allpuzzles[selectednum]

class Hints:
    def __init__( self, datadir):
        with open(os.path.join(datadir, 'hints'), mode='rt', encoding='utf-8') as f:
            alllines = f.readlines()
        self.allhints = []
        xcounter = 0
        for line in alllines:
            if len(line.strip()):
                self.allhints.append(line)
                xcounter += 1

    def get_a_hint(self):
        random.seed()
        selectednum = random.randrange(len(self.allhints))
        return self.allhints[selectednum]
