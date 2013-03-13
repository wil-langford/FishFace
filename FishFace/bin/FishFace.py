#!/usr/bin/env python
"""The wxPython GUI for FishFace."""

try:
    import wx
except:
    raise ImportError("The FishFace GUI requires the wxPython module.")


class FishFaceApp(wx.Frame):
    """The primary application class."""
    def __init__(self, parent, wxid, title):
        wx.Frame.__init__(self, parent, wxid, title, size=(300, 300), style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.startup()

    def startup(self):
        """Build widgets and show window."""

        self.Bind(wx.EVT_CLOSE, self.onExit)

        mBar = wx.MenuBar()
        fileMenu = wx.Menu()
        m_exit = fileMenu.Append(wx.ID_EXIT, "E&xit", "Exit FishFace")
        self.Bind(wx.EVT_MENU, self.onExit, m_exit)
        mBar.Append(fileMenu, "&File")

        helpMenu = wx.Menu()
        m_about = helpMenu.Append(wx.ID_ABOUT, "About", "About FishFace")
        self.Bind(wx.EVT_MENU, self.onAbout, m_about)
        mBar.Append(helpMenu, "&Help")

        self.SetMenuBar(mBar)

        sizer = wx.GridBagSizer()
        self.SetSizerAndFit(sizer)

        self.Show(True)

    def onExit(self, event):
#        dialog = wx.MessageDialog(self, "Really close?", "Confirm Close", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
#        result = dialog.ShowModal()
#        dialog.Destroy()
#        if result == wx.ID_OK:
#            self.Destroy()

        # FIXME: During testing, don't ask for confirmation on exit.  Uncomment above before release.
        self.Destroy()

    def onAbout(self, event):
        dialog = wx.MessageDialog(self,
                                  "FishFace X.X\n(c)2013 Wil Langford\n\nLicensed under the GPL v3",
                                  "About FishFace",
                                  wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

if __name__ == '__main__':
    app = wx.App()
    mainwin = FishFaceApp(None, -1, 'FishFace')
    app.MainLoop()
