#!/usr/bin/env python

# 借助Teardrop 模板修改而来

import wx
import os
from pcbnew import ActionPlugin

from .kc_dialog import kcDialog

class kcPlugin(ActionPlugin):
    """Class that gathers the actionplugin stuff"""
    def defaults(self):
        self.name = "kcbox"
        self.category = "kicad box"
        self.description = "收集或编写的工具集合"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'sys.png')
        self.show_toolbar_button = True

    def Run(self):
        kcDialog(None)
