#!/usr/bin/env python

# 借助Teardrop 模板修改而来

import wx
import pcbnew
import os
import sys

from .kc import  __version__
from .page import *


#class kcDialog(wx.Frame):
class kcDialog(wx.Dialog):
    """Class that gathers all the Gui control"""
    def __init__(self, parent):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY,  pos = wx.DefaultPosition, 
                size = wx.Size( 400,500 ), 
                style = wx.CAPTION|wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

        if sys.version_info[0] == 2:
                self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        else:
                self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.SetTitle("sYs (v{0})".format(__version__))
        p = wx.Panel(self)
        nb = sYsNB(p, -1)
        bs = wx.BoxSizer(wx.VERTICAL)
        bs.Add(nb, 1, wx.EXPAND|wx.ALL, 5)
        p.SetSizer(bs)
        self.Layout()
        self.Show()

        self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

    def onCloseWindow(self, event):
        self.Destroy()
