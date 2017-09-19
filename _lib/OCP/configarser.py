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

'''When adding a new key or deleteing an old it writes immediately the file.

'''
import configparser
import os

class MyConfigs():
    def __init__(self,filename):
        '''Inisialization.(sic!)
        Requires a full path to conf file.

        '''
        self.myconfigfilename = filename
        #print(filename)
        self.CP = configparser.ConfigParser(empty_lines_in_values=False)
        if not os.path.exists(self.myconfigfilename):
            try:
                with open(self.myconfigfilename, mode = 'at+') as f:
                    pass
            except:
                raise
        with open(self.myconfigfilename, mode = 'rt') as f:
            self.CP.read_file(f)
        #print('self.CP',self.CP,self.myconfigfilename,self.CP.sections() )

    def sections(self):
        return self.CP.sections()

    def options(self, wichsection):
        return self.CP.options(wichsection)

    def deleteconfigvalue(self, wichsection, wichoption):
        try:
            existed = self.CP.remove_option(wichsection,wichoption)
        except configparser.NoSectionError:
            return False
        except configparser.NoOptionError:
            return False
        except:#oops...
            print("Exception: ", str(sys.exc_info()) )
            return False
        if not existed: return False #no need to delete it
        with open(self.myconfigfilename, mode='wt',encoding='utf-8') as f:
            self.CP.write(f)
            return True

    def readconfigvalue(self, wichsection, wichoption, default):
        try:
            return self.CP.get(wichsection,wichoption)
        except configparser.NoSectionError:
            return default
        except configparser.NoOptionError:
            return default
        except:#oops...
            print("Exception: ", str(sys.exc_info()) )
            return default

    def writeconfigvalue(self, whichsection, whichoption, whichvalue):
        if not self.CP.has_section(whichsection):
            self.CP.add_section(whichsection)
        #print('before',self.CP.options(whichsection),'new option',whichoption)
        try:
            self.CP.set(whichsection, whichoption, whichvalue)

            with open(self.myconfigfilename, mode='wt',encoding='utf-8') as f:
                #print('after',self.CP.options(whichsection))
                self.CP.write(f)
        except Exception as e:
            print('WARNING!' + whichoption + ' not written!' , e)



