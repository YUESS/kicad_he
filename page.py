#!/usr/bin/env python


import wx
import sys
import re
import wx.grid

from .kc import KC , HEADER, BOM_HEADER, REF
import pcbnew
from pcbnew import ActionPlugin, GetBoard

class PosViewGrid(wx.Frame):
    def __init__(self, parent, id, title,pos=wx.DefaultPosition,
            size = wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, 
            data = [], head=[], info=[]):
        wx.Frame.__init__(self, parent, id, title,pos, size, style)
        grid = wx.grid.Grid(self, -1)

        
        col = len(data[0])
        row = len(data)

        colnum = len(head)
        inforownum = len(info)

        collen = []
        for c in range(colnum):
            lmax = 0
            for item in data:
                l = len(str(item[c]))
                if lmax < l:
                    lmax = l
            l = len(str(head[c]))
            if lmax < l:
                lmax = l
            collen.append(lmax)

        grid.CreateGrid(row + inforownum,col)

        grid.SetRowSize(0, 30)
        for i, value in enumerate(collen):
            grid.SetColSize(i,value*8 + 20)

        for i, item in enumerate(head):
            grid.SetColLabelValue(i, item)
            
        
        for irow, x in enumerate(data):
            for icol ,item in enumerate(x):
                grid.SetCellValue(irow + inforownum ,icol, str(item))
                grid.SetReadOnly(irow + inforownum, icol)

        #设置头信息格

        headstr = ''
        for item in info:
            headstr += item
            
        grid.SetCellSize(0,0, inforownum, colnum)
        grid.SetCellValue(0 ,0, headstr)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    def OnCloseWindow(self, event):
        self.Destroy()

class BomViewGrid(wx.Frame):
    def __init__(self, parent, id, title,pos=wx.DefaultPosition,
            size = wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, 
            data = [], head=[], info=[]):
        wx.Frame.__init__(self, parent, id, title,pos, size, style)
        grid = wx.grid.Grid(self, -1)

        col = len(data[0])
        row = len(data)

        colnum = len(head)
        inforownum = len(info)

        collen = []
        for c in range(colnum):
            lmax = 0
            for item in data:
                l = len(str(item[c]))
                if lmax < l:
                    lmax = l
            l = len(str(head[c]))
            if lmax < l:
                lmax = l
                
            collen.append(lmax)

        grid.CreateGrid(row + inforownum,col)

        grid.SetRowSize(0, 30)
        for i, value in enumerate(collen):
            grid.SetColSize(i,value*8 + 20)

        for i, item in enumerate(head):
            grid.SetColLabelValue(i, item)
            
        
        for irow, x in enumerate(data):
            for icol ,item in enumerate(x):
                grid.SetCellValue(irow + inforownum ,icol, str(item))
                grid.SetReadOnly(irow + inforownum, icol)

        #设置头信息格

        headstr = ''
        for item in info:
            headstr += item
            
        grid.SetCellSize(0,0, inforownum, colnum)
        grid.SetCellValue(0 ,0, headstr)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    def OnCloseWindow(self, event):
        self.Destroy()

class ShowPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, size=(390,500))
        #wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        b = wx.Button(self, -1, "隐藏元件值")
        sizer.Add(b, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL|wx.EXPAND, 5)
        self.Bind(wx.EVT_BUTTON, self.OnHideValue, b)


        b = wx.Button(self, -1, "移动元件值")
        self.Bind(wx.EVT_BUTTON, self.OnMoveValue, b)
        sizer.Add(b, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL|wx.EXPAND, 5)

        b = wx.Button(self, -1, "设置元件参考")
        self.Bind(wx.EVT_BUTTON, self.OnSetRef, b)
        sizer.Add(b, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        x,y = sizer.Fit(self)
        self.Fit()
        #设置panel背景颜色
        self.SetBackgroundColour("Green")
        #x,y = self.GetBestSize()
        #x,y = self.GetSize()
        #dlg = wx.MessageDialog(self, str(x) + '_' + str(y) ,"aa", style=wx.OK)
        #dlg.ShowModal()
        #dlg.Destroy()

 

    def OnHideValue(self, evt):
        board = pcbnew.GetBoard()
        KC().setValueDisVisible(board)
        pcbnew.Refresh() #Show up newly added vias

    def OnMoveValue(self, evt):
        board = pcbnew.GetBoard()
        KC().setValueOnOtherLayer(board)
        pcbnew.Refresh() #Show up newly added vias

    def OnSetRef(self, evt):
        board = pcbnew.GetBoard()
        KC().setRefSize(board)
        pcbnew.Refresh() #Show up newly added vias

class PositionPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.StaticBox(self, -1, "屏蔽项")

        hsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.list = wx.ListBox(box, -1, size=(200,300),choices=[],style=wx.LB_SINGLE)
        
        hsizer.Add(self.list, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        b = wx.Button(box, -1, "+",size = (60,40))
        self.Bind(wx.EVT_BUTTON, self.Onlistadd, b)
        vsizer.Add(b, 0, wx.EXPAND|wx.TOP|wx.LEFT, 5)
        b = wx.Button(box, -1, "-",size = (60,40))
        self.Bind(wx.EVT_BUTTON, self.Onlistdel, b)
        vsizer.Add(b, 0, wx.EXPAND|wx.BOTTOM|wx.LEFT, 5)
        
        hsizer.Add(vsizer, 0, wx.ALIGN_CENTRE|wx.ALL,5)

        sizer.Add(hsizer, 1, wx.EXPAND|wx.ALL, 25)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)

        b = wx.Button(self, -1, "生成SMD位置文件")
        self.Bind(wx.EVT_BUTTON, self.OnSMDpos, b)
        btnsizer.Add(b,0, wx.ALIGN_CENTRE|wx.ALL, 5)

        b = wx.Button(self, -1, "生成所有位置文件")
        self.Bind(wx.EVT_BUTTON, self.OnAllpos, b)
        btnsizer.Add(b,0, wx.ALIGN_CENTRE|wx.ALL, 5)

        b = wx.Button(self, -1, "预览")
        self.Bind(wx.EVT_BUTTON, self.OnViewPos, b)
        btnsizer.Add(b,0, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def Onlistadd(self, evt):
        dlg = wx.TextEntryDialog(None,
                "请输入需要屏蔽的项(支持*匹配)",
                "Text Entry", "*", style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            self.list.Append(dlg.GetValue())

        dlg.Destroy()

    def Onlistdel(self, evt):
        sel = self.list.GetSelection()
        if sel != -1:
            self.list.Delete(sel)

    def OnSMDpos(self, evt):
        num = self.list.GetCount()
        self.listData =[] 

        for i in range(num):
            listvalue = self.list.GetString(i)
            self.listData.append(listvalue)

        board = pcbnew.GetBoard()
        #board = pcbnew.LoadBoard("./ijw-E6001.kicad_pcb")
        posinfo, headinfo = KC().generalPosition(board)
        posinfo_filter = IgnoreHandle(self.listData, posinfo, REF)

        KC().save_placement_info(board, posinfo_filter, headinfo,'SMT')
        dlg = wx.MessageDialog(self, "完成","aa", style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    def OnAllpos(self, evt):
        num = self.list.GetCount()
        self.listData =[] 

        for i in range(num):
            listvalue = self.list.GetString(i)
            self.listData.append(listvalue)

        #board = pcbnew.LoadBoard("./ijw-E6001.kicad_pcb")
        board = pcbnew.GetBoard()
        posinfo, headinfo = KC().generalPosition(board)
        posinfo_filter = IgnoreHandle(self.listData, posinfo, REF)

        KC().save_placement_info(board, posinfo_filter, headinfo,'ALL')
        dlg = wx.MessageDialog(self, "完成","aa", style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    def OnViewPos(self, evt):
        
        #获取屏蔽列表个数
        num = self.list.GetCount()
        self.listData =[] 
        for i in range(num):
            listvalue = self.list.GetString(i)
            self.listData.append(listvalue)

        #board = pcbnew.LoadBoard("./ijw-E6001.kicad_pcb")
        board = pcbnew.GetBoard()
        posinfo, headinfo = KC().generalPosition(board)
        posinfo_filter = IgnoreHandle(self.listData, posinfo, REF)
            
        if len(posinfo_filter) == 0:
            dlg = wx.MessageDialog(self, "无数据", style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            win = PosViewGrid(self, -1, "position view", size=(800, 600),
                    style = wx.DEFAULT_FRAME_STYLE, 
                    data = posinfo_filter, head = HEADER, info = headinfo)
            win.Show(True)

def IgnoreHandle(igitem, data, index = 0):
    # 每个元素头和尾 加入^ $字符
    lst = ['^'+ i + '$' for i in igitem ]
    # 用|连接每个元素成一个字符串
    ig = '|'.join(lst)
    # 替换ig中*号为\w*
    ig = re.sub('\*','\\\\w*',ig)

    data_filter = []

    if ig == '':
        data_filter = data

    for item in data:
        if re.match(ig, item[index], re.I) == None:
            data_filter.append(item)
    return data_filter


class BOMPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.StaticBox(self, -1, "屏蔽项")

        hsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        self.list = wx.ListBox(box, -1, size=(200,300),choices=[],style=wx.LB_SINGLE)
        
        hsizer.Add(self.list, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        b = wx.Button(box, -1, "+",size = (60,40))
        self.Bind(wx.EVT_BUTTON, self.Onlistadd, b)
        vsizer.Add(b, 0, wx.EXPAND|wx.TOP|wx.LEFT, 5)
        b = wx.Button(box, -1, "-",size = (60,40))
        self.Bind(wx.EVT_BUTTON, self.Onlistdel, b)
        vsizer.Add(b, 0, wx.EXPAND|wx.BOTTOM|wx.LEFT, 5)
        
        hsizer.Add(vsizer, 0, wx.ALIGN_CENTRE|wx.ALL,5)

        sizer.Add(hsizer, 1, wx.EXPAND|wx.ALL, 25)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)


        b = wx.Button(self, -1, "生成BOM")
        self.Bind(wx.EVT_BUTTON, self.OnGenBOM, b)
        btnsizer.Add(b,0, wx.ALIGN_CENTRE|wx.ALL, 5)

        # 暂时不开放，无法使用
        b = wx.Button(self, -1, "预览")
        self.Bind(wx.EVT_BUTTON, self.OnViewBOM, b)
        btnsizer.Add(b,0, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def Onlistadd(self, evt):
        dlg = wx.TextEntryDialog(None,
                "请输入需要屏蔽的项(支持*匹配)",
                "Text Entry", "*", style=wx.OK|wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            self.list.Append(dlg.GetValue())

        dlg.Destroy()

    def Onlistdel(self, evt):
        sel = self.list.GetSelection()
        if sel != -1:
            self.list.Delete(sel)

    def OnGenBOM(self, evt):
        num = self.list.GetCount()
        self.listData =[] 
        for i in range(num):
            listvalue = self.list.GetString(i)
            self.listData.append(listvalue)

        board = pcbnew.GetBoard()
        #board = pcbnew.LoadBoard("./ijw-E6001.kicad_pcb")
        info, headinfo = KC().generalBOM(board)
        info_filter = IgnoreHandle(self.listData, info, REF)
        headinfo.append('# Total: ' + str(len(info_filter)) + u'\r\n')
        group = CombingHandle(info_filter)

        KC().save_info(board, group, headinfo,'BOM')
        dlg = wx.MessageDialog(self, "完成","aa", style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnViewBOM(self, evt):
        #获取屏蔽列表个数
        num = self.list.GetCount()
        self.listData =[] 
        for i in range(num):
            listvalue = self.list.GetString(i)
            self.listData.append(listvalue)

        #board = pcbnew.LoadBoard("./ijw-E6001.kicad_pcb")
        board = pcbnew.GetBoard()
        info, headinfo = KC().generalBOM(board)
        info_filter = IgnoreHandle(self.listData, info, REF)
        headinfo.append('# Total: ' + str(len(info_filter)) + u'\r\n')
        group = CombingHandle(info_filter)
        #print(group)

        if len(group) == 0:
            dlg = wx.MessageDialog(self, "无数据", style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            win = BomViewGrid(self, -1, "BOM view", size=(800, 600),
                    style = wx.DEFAULT_FRAME_STYLE, 
                    data = group, head = BOM_HEADER, info = headinfo)
            win.Show(True)

def CombingHandle(data):
    res = []
    s = data
    total = 0

    while len(s) > 0:
        v = s[0]
        cnt = 1
        dup = []
        dup.append(0)
        for x, item in enumerate(s[1:]):
            if v[1] == item[1] and v[2] == item[2]:
                v[0] = v[0] + ','+ item[0]
                cnt += 1
                dup.append(x + 1)
                #合并后记下合并项标号，后续在统一删除
        v[3] = cnt
        res.append(v)
        for i,x in enumerate(dup):
            del s[x - i]
        total += cnt
    #print(total)
    return res
        

#---------------------------------------------------------------------------
class sYsNB(wx.Notebook):
    def __init__(self, parent, id ):
        wx.Notebook.__init__(self, parent, id, size=(400,500), style=
                             #wx.NB_DEFAULT
                             wx.NB_TOP
                             #wx.NB_BOTTOM
                             #wx.NB_LEFT
                             #wx.NB_RIGHT
                             # | wx.NB_MULTILINE
                             )

        win = ShowPanel(self)
        self.AddPage(win, "展示")

        win = PositionPanel(self)
        self.AddPage(win, "位置文件")

        win = BOMPanel(self)
        self.AddPage(win, "BOM")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)


    def OnPageChanged(self, event):
        if self:
            old = event.GetOldSelection()
            new = event.GetSelection()
            sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        if self:
            old = event.GetOldSelection()
            new = event.GetSelection()
            sel = self.GetSelection()
        event.Skip()


#---------------------------------------------------------------------------

#app = wx.App(False)
#
#frame = wx.Frame(None, title="sYs tools",size=(400,500))
#
#sYsNB(frame, -1)
##nb = wx.Notebook(frame)
##nb.AddPage(TestPanel(nb,'aa'), "Absolute Positioning")
#
#frame.Show()
#
#app.MainLoop()

