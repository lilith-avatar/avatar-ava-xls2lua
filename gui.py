#! /usr/bin/env python
# -*- coding: utf-8 -*
# description: xls2lua GUI
# git repo: https://github.com/lilith-avatar/avatar-ava-xls2lua

import wx
import wx.richtext as rt
import ava_xls2lua as x2l
import sys
import os

__authors__ = ['Yuancheng Zhang']
__copyright__ = 'Copyright 2020, Lilith Games, Project DaVinci, Avatar Team'
__credits__ = ['Yuancheng Zhang']
__license__ = 'MIT'
__version__ = 'v2.4.0.17'
__maintainer__ = 'Yuancheng Zhang'
__status__ = 'Production'


class MainFrame(wx.Frame):
    prefix_color = {
        'info': 'blue',
        'error': 'red',
        'sucess': 'sea green',
        'failed': 'red'
    }

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size=wx.Size(720, 320))
        self.SetIcon(wx.Icon(self.resource_path('icon.ico')))
        self.panel = wx.Panel(self)

        self.sizer_v = wx.BoxSizer(wx.VERTICAL)

        font1 = wx.Font(8, wx.MODERN, wx.NORMAL,
                        wx.NORMAL, False, u'Consolas')

        # 采用多行显示
        self.logs = rt.RichTextCtrl(
            self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.logs.SetFont(font1)

        # 1为响应容器改变大小，expand占据窗口的整个宽度
        self.sizer_v.Add(self.logs, 1, wx.ALIGN_TOP | wx.EXPAND)
        self.panel.SetSizerAndFit(self.sizer_v)

        # Config - input path
        self.sizer_cfg_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.st1 = wx.StaticText(
            self.panel, label=' Input Path:', size=(120, -1))
        self.sizer_cfg_1.Add(self.st1, flag=wx.RIGHT, border=4)
        self.tc1 = wx.TextCtrl(self.panel)
        self.sizer_cfg_1.Add(self.tc1, proportion=1)

        # Config - output path
        self.sizer_cfg_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.st2 = wx.StaticText(
            self.panel, label=' Output Path:', size=(120, -1))
        self.sizer_cfg_2.Add(self.st2, flag=wx.RIGHT, border=4)
        self.tc2 = wx.TextCtrl(self.panel)
        self.sizer_cfg_2.Add(self.tc2,  proportion=1)

        # Config - output lua template
        self.sizer_cfg_3 = wx.BoxSizer(wx.HORIZONTAL)
        self.st3 = wx.StaticText(
            self.panel, label=' Output Lua Template:', size=(120, -1))
        self.sizer_cfg_3.Add(self.st3, flag=wx.RIGHT, border=4)
        self.tc3 = wx.TextCtrl(self.panel)
        self.sizer_cfg_3.Add(self.tc3,  proportion=1)

        # Config - kv format excels
        self.sizer_cfg_4 = wx.BoxSizer(wx.HORIZONTAL)
        self.st4 = wx.StaticText(
            self.panel, label=' KV Format Excel Files:', size=(120, -1))
        self.sizer_cfg_4.Add(self.st4, flag=wx.RIGHT, border=4)
        self.tc4 = wx.TextCtrl(self.panel)
        self.sizer_cfg_4.Add(self.tc4,  proportion=1)

        # Config - translate excel
        self.sizer_cfg_5 = wx.BoxSizer(wx.HORIZONTAL)
        self.st5 = wx.StaticText(
            self.panel, label=' Translate Excel File:', size=(120, -1))
        self.sizer_cfg_5.Add(self.st5, flag=wx.RIGHT, border=4)
        self.tc5 = wx.TextCtrl(self.panel)
        self.sizer_cfg_5.Add(self.tc5,  proportion=1)

        self.sizer_v.Add(self.sizer_cfg_1, flag=wx.EXPAND |
                         wx.LEFT | wx.RIGHT | wx.TOP, border=4)
        self.sizer_v.Add(self.sizer_cfg_2, flag=wx.EXPAND |
                         wx.LEFT | wx.RIGHT | wx.TOP, border=4)
        self.sizer_v.Add(self.sizer_cfg_3, flag=wx.EXPAND |
                         wx.LEFT | wx.RIGHT | wx.TOP, border=4)
        self.sizer_v.Add(self.sizer_cfg_4, flag=wx.EXPAND |
                         wx.LEFT | wx.RIGHT | wx.TOP, border=4)
        self.sizer_v.Add(self.sizer_cfg_5, flag=wx.EXPAND |
                         wx.LEFT | wx.RIGHT | wx.TOP, border=4)

        # Bottom sizer
        self.sizer_btm = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_btm_l = wx.BoxSizer(wx.VERTICAL)
        self.sizer_btm_r = wx.BoxSizer(wx.VERTICAL)

        # Convert
        self.btn_convert = wx.Button(self.panel, label='Convert')
        self.Bind(wx.EVT_BUTTON, self.on_convert_click, self.btn_convert)
        self.sizer_btm_l.Add((-1, 4))
        self.sizer_btm_l.Add(self.btn_convert, flag=wx.LEFT, border=4)

        # Config
        self.cb_config = wx.CheckBox(self.panel, label='Config')
        self.Bind(wx.EVT_CHECKBOX, self.on_config_checked, self.cb_config)
        self.sizer_btm_r.Add(self.cb_config,
                             flag=wx.RIGHT | wx.ALIGN_RIGHT, border=4)

        # version
        version_str = __version__ + '  '
        self.st_version = wx.StaticText(
            self.panel, label=version_str, size=(100, -1), style=wx.ALIGN_RIGHT)
        self.sizer_btm_r.Add(self.st_version,
                             flag=wx.RIGHT | wx.ALIGN_RIGHT, border=4)

        self.sizer_v.Add((-1, 4))
        self.sizer_v.Add(self.sizer_btm,  proportion=0,
                         flag=wx.EXPAND, border=4)
        self.sizer_btm.Add(self.sizer_btm_l, proportion=1,
                           flag=wx.LEFT | wx.EXPAND, border=4)
        self.sizer_btm.Add(self.sizer_btm_r, proportion=1,
                           flag=wx.RIGHT | wx.EXPAND, border=4)
        self.sizer_v.Add((-1, 4))

        if not x2l:
            self.cb_config.Hide()

        # Init panel
        self.panel.Layout()
        self.sizer_v.Hide(self.sizer_cfg_1, recursive=True)
        self.sizer_v.Hide(self.sizer_cfg_2, recursive=True)
        self.sizer_v.Hide(self.sizer_cfg_3, recursive=True)
        self.sizer_v.Hide(self.sizer_cfg_4, recursive=True)
        self.sizer_v.Hide(self.sizer_cfg_5, recursive=True)

    # 响应button事件
    def on_convert_click(self, event):
        if self.cb_config.IsChecked():
            self.hide_config()

        self.btn_convert.Disable()
        self.clear_log()
        x2l.run()
        self.btn_convert.Enable()

    def clear_log(self):
        self.logs.Clear()
        self.logs.Refresh()

    def save_config(self):
        # print('save_config')
        x2l.INPUT_FOLDER = self.tc1.GetValue()
        x2l.OUTPUT_FOLDER = self.tc2.GetValue()
        x2l.OUTPUT_LUA_TEMPLATE = self.tc3.GetValue()
        x2l.KV_XLS = self.tc4.GetValue()
        x2l.TRANSLATE_XLS = self.tc5.GetValue()
        x2l.save_config()

    def load_config(self):
        # print('load_config')
        x2l.load_config()
        self.tc1.Clear()
        self.tc2.Clear()
        self.tc3.Clear()
        self.tc4.Clear()
        self.tc5.Clear()
        self.tc1.Refresh()
        self.tc2.Refresh()
        self.tc3.Refresh()
        self.tc4.Refresh()
        self.tc5.Refresh()
        self.tc1.write(x2l.INPUT_FOLDER)
        self.tc2.write(x2l.OUTPUT_FOLDER)
        self.tc3.write(x2l.OUTPUT_LUA_TEMPLATE)
        self.tc4.write(str(x2l.KV_XLS))
        self.tc5.write(x2l.TRANSLATE_XLS)

    def on_config_checked(self, event):
        self.toggle_config()

    def toggle_config(self):
        if self.cb_config.IsChecked():
            self.show_config()
        else:
            self.hide_config()

    def show_config(self):
        self.load_config()
        self.sizer_v.Show(self.sizer_cfg_1, recursive=True)
        self.sizer_v.Show(self.sizer_cfg_2, recursive=True)
        self.sizer_v.Show(self.sizer_cfg_3, recursive=True)
        self.sizer_v.Show(self.sizer_cfg_4, recursive=True)
        self.sizer_v.Show(self.sizer_cfg_5, recursive=True)
        self.panel.Layout()
        self.cb_config.SetValue(True)

    def hide_config(self):
        self.save_config()
        self.sizer_v.Hide(self.sizer_cfg_1, recursive=True)
        self.sizer_v.Hide(self.sizer_cfg_2, recursive=True)
        self.sizer_v.Hide(self.sizer_cfg_3, recursive=True)
        self.sizer_v.Hide(self.sizer_cfg_4, recursive=True)
        self.sizer_v.Hide(self.sizer_cfg_5, recursive=True)
        self.panel.Layout()
        self.cb_config.SetValue(False)

    def write(self, prefix, s):
        self.logs.WriteText('[')
        self.logs.BeginTextColour(self.prefix_color[prefix])
        self.logs.WriteText(prefix)
        self.logs.EndTextColour()
        self.logs.WriteText(']')
        self.logs.WriteText(' {}\n'.format(s))

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath('.')
        return os.path.join(base_path, relative_path)


class App(wx.App):
    def OnInit(self):
        self.main_frame = MainFrame(
            None, 'Project DaVinci - XLS to LUA Convertor')
        self.main_frame.Show()
        if x2l:
            x2l.set_gui(self.main_frame)
        return True


def main():
    app = App()
    app.MainLoop()


if __name__ == '__main__':
    main()
