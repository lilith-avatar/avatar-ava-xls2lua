#! /usr/bin/env python
# -*- coding: utf-8 -*
# description: xls2lua GUI
# git repo: https://github.com/lilith-avatar/avatar-ava-xls2lua

__author__ = "Yuancheng Zhang"
__copyright__ = "Copyright 2020, Lilith Games, Project DaVinci, Avatar Team"
__credits__ = ["Yuancheng Zhang"]
__license__ = "MIT"
__version__ = "1.1"
__maintainer__ = "Yuancheng Zhang"
__status__ = "Develop"

import wx
import wx.richtext as rt
import ava_xls2lua as x2l


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)

        self.SetIcon(wx.Icon("icon.ico"))

        self.panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        # 采用多行显示
        self.logs = rt.RichTextCtrl(
            self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # 1为响应容器改变大小，expand占据窗口的整个宽度
        sizer.Add(self.logs, 1, wx.ALIGN_TOP | wx.EXPAND)
        self.button = wx.Button(self.panel, label='Convert')
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        sizer.Add(self.button)
        self.panel.SetSizerAndFit(sizer)
        self.panel.Layout()

    # 响应button事件
    def OnClick(self, event):
        if x2l is not None:
            self.button.Disable()
            self.logs.Clear()
            self.logs.Refresh()
            x2l.run()
            self.button.Enable()
        else:
            self.logs.WriteText('x2l is not found.')

    def write(self, s):
        self.logs.WriteText(s + '\n')


if __name__ == '__main__':
    app = wx.App()
    mainFrame = MainFrame(None, 'Project DaVinci - XLS to LUA Convertor')
    mainFrame.Show()
    if x2l is not None:
        x2l.set_gui(mainFrame)
    app.MainLoop()
