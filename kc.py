# coding: utf8
# gen_pos_files.py
#
# Copyright (C) 2018, 2019 Eldar Khayrullin <eldar.khayrullin@mail.ru>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

''' KiCad PCBNew Action Plugin for generating pos files'''

import getpass
import os
import pcbnew
import re
import shutil
import sys
import time
import wx

from pcbnew import ActionPlugin, GetBoard
from platform import platform

__version__ = "2.3"

OUTPUT_DIR = 'output'# + os.path.sep + OUTPUT_NAME

EOL = u'\r\n'
SEP = u' '
JSEP = u'_'
EMPTY_FIELD = u'~'
HEADER = [u'Ref', u'Value',  u'Package', u'PosX', u'PosY', u'Rot', u'Side', u'SMD']
BOM_HEADER = [u'Ref', u'Value',  u'Package', u'Quantity']

REF = 0
VAL = 1
PACKAGE = 2
POSX = 3
POSY = 4
ROT = 5
SIDE = 6
IS_SMD = 7



IGINOR = ("TestPoint_Probe", "MountingHole_Pad", "Fiducial", "NC", "nc")

TRANSLATE_TABLE = {
    ord(u' ') : u'_',
    ord(u',') : u'.',
    ord(u'¹') : u'^1_',
    ord(u'²') : u'^2_',
    ord(u'³') : u'^3_',
    ord(u'±') : u'+-',

    # russian chars
    ord(u'ё') : u'e',
    ord(u'а') : u'a',
    ord(u'б') : u'b',
    ord(u'в') : u'v',
    ord(u'г') : u'g',
    ord(u'д') : u'd',
    ord(u'е') : u'e',
    ord(u'ж') : u'g',
    ord(u'з') : u'z',
    ord(u'и') : u'i',
    ord(u'й') : u'i',
    ord(u'к') : u'k',
    ord(u'л') : u'l',
    ord(u'м') : u'm',
    ord(u'н') : u'n',
    ord(u'о') : u'o',
    ord(u'п') : u'p',
    ord(u'р') : u'r',
    ord(u'с') : u's',
    ord(u'т') : u't',
    ord(u'у') : u'u',
    ord(u'ф') : u'f',
    ord(u'х') : u'h',
    ord(u'ц') : u'c',
    ord(u'ч') : u'ch',
    ord(u'ш') : u'sh',
    ord(u'щ') : u'ch',
    ord(u'ъ') : u'',
    ord(u'ы') : u'i',
    ord(u'ь') : u'',
    ord(u'э') : u'e',
    ord(u'ю') : u'y',
    ord(u'я') : u'ya',

    ord(u'Ё') : u'E',
    ord(u'А') : u'A',
    ord(u'Б') : u'B',
    ord(u'В') : u'V',
    ord(u'Г') : u'G',
    ord(u'Д') : u'D',
    ord(u'Е') : u'E',
    ord(u'Ж') : u'G',
    ord(u'З') : u'Z',
    ord(u'И') : u'I',
    ord(u'Й') : u'I',
    ord(u'К') : u'K',
    ord(u'Л') : u'L',
    ord(u'М') : u'M',
    ord(u'Н') : u'N',
    ord(u'О') : u'O',
    ord(u'П') : u'P',
    ord(u'Р') : u'R',
    ord(u'С') : u'S',
    ord(u'Т') : u'T',
    ord(u'У') : u'U',
    ord(u'Ф') : u'F',
    ord(u'Х') : u'H',
    ord(u'Ц') : u'C',
    ord(u'Ч') : u'CH',
    ord(u'Ш') : u'SH',
    ord(u'Щ') : u'CH',
    ord(u'Ъ') : u'',
    ord(u'Ы') : u'I',
    ord(u'Ь') : u'',
    ord(u'Э') : u'E',
    ord(u'Ю') : u'Y',
    ord(u'Я') : u'YA',
}

class KC():
    def setRefSize(self, board = None):
        if board == None:
            board = GetBoard()

        self.board = board

        for module in self.board.GetModules():
            module.Reference().SetThickness(80000)
            module.Reference().SetTextWidth(650000)
            module.Reference().SetTextHeight(650000)

    def setValueSize(self, board = None):
        if board == None:
            board = GetBoard()

        self.board = board
        for module in self.board.GetModules():
            module.Value().SetThickness(150000)
            module.Value().SetTextWidth(800000)
            module.Value().SetTextHeight(800000)

    def setValueDisVisible(self, board = None):
        if board == None:
            board = GetBoard()

        self.board = board

        for module in self.board.GetModules():
            module.Value().SetVisible(False)

    def setValueOnOtherLayer(self,board = None):
        if board == None:
            board = GetBoard()

        self.board = board
        origin = self.board.GetAuxOrigin()
        for module in self.board.GetModules():
            reference = module.GetReference()
            #print(module.Reference().GetPosition())

            if self.is_non_annotated_ref(reference):
                continue

            value = module.GetValue()

            excluded = False
            for ig in IGINOR:
                if value == ig:
                    excluded = True
            if excluded:
                module.Value().SetVisible(False)
                continue
            
            value = module.Value()
            value.SetVisible(True)
            lay = value.GetLayer()

            #print(module.GetValue())
            #print(pcbnew.B_CrtYd)
            #print(pcbnew.F_CrtYd)
            #print(pcbnew.B_Fab)
            #print(pcbnew.F_Fab)
            if lay == pcbnew.F_Fab: 
                value.SetLayer(pcbnew.F_CrtYd)
            elif lay == pcbnew.B_Fab:
                value.SetLayer(pcbnew.B_CrtYd)

            value.SetThickness(80000)
            value.SetTextWidth(500000)
            value.SetTextHeight(500000)
            mpos = module.GetPosition()
            value.SetTextPos(mpos)

    def generalBOM(self, board = None):
        if board == None:
            board = GetBoard()

        self.board = board
        self.get_bom_info()
        self.generalBOMHeaderInfo()
        return self.info, self.headinfo

    def generalBOMHeaderInfo(self):
        self.headinfo = []
        shtamp = self.get_shtamp_str()
        self.headinfo.append(shtamp)

        ver = self.board.GetTitleBlock().GetRevision()
        name = '# File name: ' + self.get_board_name() + '  Revision: ' + ver + EOL
        self.headinfo.append(name)

    def generalPosition(self, board = None):
        if board == None:
            board = GetBoard()

        self.board = board
        self.get_placement_info()
        self.getPositionHeaderInfo()
        return self.info, self.headinfo

    def getPositionHeaderInfo(self):
        self.headinfo = []

        shtamp = self.get_shtamp_str()
        self.headinfo.append(shtamp)

        ver = self.board.GetTitleBlock().GetRevision()
        name = '# File name: ' + self.get_board_name() + '  Revision: ' + ver + EOL
        self.headinfo.append(name)

        total1 = '# Total(All): ' + str(self.numALL) + EOL
        self.headinfo.append(total1)
        total1 = '# Total(SMT): ' + str(self.numSMT) + EOL
        self.headinfo.append(total1)

    def get_placement_info(self):
        self.info = []
        self.numALL = 0 
        self.numSMT = 0 

        origin = self.board.GetAuxOrigin()

        for module in self.board.GetModules():
            reference = module.GetReference()

            if self.is_non_annotated_ref(reference):
                continue

            value = module.GetValue()
            excluded = False
            '''

            for ig in IGINOR:
                if value == ig:
                    excluded = True
            if excluded:
                continue
            '''
            
            self.numALL += 1
            package = str(module.GetFPID().GetLibItemName())

            pos = module.GetPosition() - origin

            pos_x = pcbnew.ToMM(pos.x)
            if module.IsFlipped():
                pos_x = -pos_x

            pos_y = -pcbnew.ToMM(pos.y)

            rotation = module.GetOrientationDegrees()

            if module.IsFlipped():
                side = u'bottom'
            else:
                side = u'top'

            is_smd = self.is_smd_module(module)
            smdor = u'HID'
            if is_smd:
                self.numSMT +=1
                smdor = u'SMD'

            self.info.append([reference, value, package, pos_x, pos_y, rotation, side, smdor])

        self.info.sort(key=self.get_ref_num)
        self.info.sort(key=self.get_ref_group)
        self.info.sort(key=self.get_side_group, reverse=True)
    def get_bom_info(self):
        self.info = []
        self.cnt = 0
        for module in self.board.GetModules():
            reference = module.GetReference()

            if self.is_non_annotated_ref(reference):
                continue

            value = module.GetValue()
            excluded = False
            '''
            for ig in IGINOR:
                if value == ig:
                    excluded = True
            if excluded:
                continue
            '''
            package = str(module.GetFPID().GetLibItemName())
            cnt = 1

            self.info.append([reference, value, package, cnt])

        self.info.sort(key=self.get_ref_num)
        self.info.sort(key=self.get_ref_group)

    def is_non_annotated_ref(self, ref):
        return ref[-1] == u'*'

    def is_smd_module(self, module):
        attr = module.GetAttributes()
        return (attr == pcbnew.MOD_CMS) or (attr == pcbnew.MOD_VIRTUAL)

    def get_ref_group(self, item):
        return re.sub('[0-9]*$', u'', item[REF])
    def get_side_group(self, item):
        return re.sub('[0-9]*$', u'', item[SIDE])

    def get_ref_num(self, item):
        try:
            return int(re.findall('[0-9]*$', item[REF])[0])
        except:
            return 0

    def mkdir_out(self, path):
        if os.path.exists(path) == False:
            os.makedirs(path)

    def clean_output(self, path):
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=False, onerror=None)
        os.makedirs(path)

    def save_info(self,board, info, headinfo, type='ALL'):
        self.info = info
        self.headinfo = headinfo
        self.board = board

        self.mkdir_out(self.get_output_abs_path())
        self.collect_fields_length_statistic(BOM_HEADER)

        path = self.get_output_abs_path()
        name = path + os.path.sep + self.get_board_name()

        ver = self.board.GetTitleBlock().GetRevision()

        pos_file = open(name +  u'-' + ver + u'-' + type +u'.csv', mode='w')
        for item in self.headinfo:
            pos_file.write(item)

        self.write_info(pos_file, BOM_HEADER)
        pos_file.close()

    def write_info(self, ofile, header):
        self.write_item(header, ofile)
        for item in self.info:
            self.write_item(item, ofile)

    def save_placement_info(self,board, info, headinfo, type='ALL'):
        self.info = info
        self.headinfo = headinfo
        self.board = board

        self.mkdir_out(self.get_output_abs_path())

        self.collect_fields_length_statistic(HEADER)

        path = self.get_output_abs_path()
        name = path + os.path.sep + self.get_board_name()

        ver = self.board.GetTitleBlock().GetRevision()

        pos_file = open(name + u'-' + ver + u'-' + type+ u'.pos', mode='w')
        for item in self.headinfo:
            pos_file.write(item)

        self.write_placement_info(pos_file, type, HEADER)
        pos_file.close()

    def collect_fields_length_statistic(self, head):
        self.fields_max_length = []
        for i in range(0, len(head)):
            self.fields_max_length.append(len(head[i]))
        self.fields_max_length[0] += 1

        for item in self.info:
            for field in range(0, len(self.info[0]) - 1):
                cur_len = len(str(item[field]))
                if self.fields_max_length[field] < cur_len:
                    self.fields_max_length[field] = cur_len

    def get_shtamp_str(self):
        return '# Author: ' + getpass.getuser() + \
               ' , Timeshtamp: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+ \
               ' , Plugin: ' + __version__ + \
               EOL

    def get_output_abs_path(self):
        self.board = GetBoard()
        path = os.path.dirname(os.path.abspath(self.board.GetFileName()))
        return path + os.path.sep + OUTPUT_DIR

    def get_board_name(self):
        name = self.board.GetTitleBlock().GetComment(0)
        if name == '':
            name = os.path.splitext(os.path.basename(self.board.GetFileName()))[0]
        return name

    def get_separators_str(self, n):
        separators = ''
        for i in range(0, n):
            separators += SEP
        return separators

    def write_placement_info(self, ofile, isall, head):
        self.write_item(head, ofile)
        for item in self.info:
            if isall == 'SMT':
                if item[IS_SMD] == "HID":
                    continue
            self.write_item(item, ofile)

    def write_item(self, items, ofile):
        for i, item in enumerate(items):
            ofile.write(str(item))
            num_sep = self.fields_max_length[i] - len(str(item)) + 1
            ofile.write(self.get_separators_str(num_sep))
            if i < len(items) - 1:
                ofile.write('|')
        ofile.write(EOL)

    #def write_item_tofile(self, item, ofile):
    #    s = [str(x) for x in item]
    #    s = '|'.join(s)
    #    ofile.write(s)
    #    ofile.write(EOL)
