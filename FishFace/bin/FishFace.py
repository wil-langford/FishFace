#!/usr/bin/env python
"""The wxPython GUI for FishFace."""
try:
    import wx
except:
    raise ImportError("The FishFace GUI requires the wxPython module.")


class FishFaceApp(wx.Frame):
    """The primary application class."""
    def __init__(self, parent, wxid, title):
        wx.Frame.__init__(self, parent, wxid, title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.startup()

    def startup(self):
        """Build widgets and show window."""

        self.Bind(wx.EVT_CLOSE, self.onExit)

        # Start menubar
        mBar = wx.MenuBar()

        # File menu
        fileMenu = wx.Menu()
        m_exit = fileMenu.Append(wx.ID_EXIT, "E&xit", "Exit FishFace")
        self.Bind(wx.EVT_MENU, self.onExit, m_exit)
        mBar.Append(fileMenu, "&File")

        # Help Menu
        helpMenu = wx.Menu()
        m_about = helpMenu.Append(wx.ID_ABOUT, "About", "About FishFace")
        self.Bind(wx.EVT_MENU, self.onAbout, m_about)
        mBar.Append(helpMenu, "&Help")

        # Assign menubar
        self.SetMenuBar(mBar)

        # Primary splitter (left panels from right panel)
        splitter = wx.SplitterWindow(self, style=wx.SP_3D)
        leftPanel = wx.Panel(splitter, style=wx.SUNKEN_BORDER)
        rightPanel = wx.Panel(splitter, style=wx.SUNKEN_BORDER)
        splitter.SplitVertically(leftPanel, rightPanel)
        splitter.SetMinimumPaneSize(120)

        # Left splitter (top panel from bottom panels)
        leftSplitter = wx.SplitterWindow(leftPanel, style=wx.SP_3D)
        self.sourcesPanel = wx.Panel(leftSplitter, style=wx.SUNKEN_BORDER)
        bottomPanels = wx.Panel(leftSplitter)
        leftSplitter.SplitHorizontally(self.sourcesPanel, bottomPanels)
        leftSplitter.SetMinimumPaneSize(80)

        # bottom splitter (mid panel from low panel)
        bottomSplitter = wx.SplitterWindow(bottomPanels, style=wx.SP_3D)
        self.chainsPanel = wx.Panel(bottomSplitter, style=wx.SUNKEN_BORDER)
        self.sinksPanel = wx.Panel(bottomSplitter, style=wx.SUNKEN_BORDER)
        bottomSplitter.SplitHorizontally(self.chainsPanel, self.sinksPanel)
        bottomSplitter.SetMinimumPaneSize(80)

        # Sizers and such
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add(bottomSplitter, 1, wx.EXPAND)
        bottomPanels.SetSizer(bottomSizer)

        leftSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftSizer.Add(leftSplitter, 1, wx.EXPAND)
        leftPanel.SetSizer(leftSizer)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Set overall window geometry and show window
        self.SetSize((900, 600))
        self.Show(True)

        # Set initial splitter sash positions and gravities
        leftSplitter.SetSashPosition(int(leftSplitter.GetSizeTuple()[1] / 3))
        leftSplitter.SetSashGravity(0.3333)
        bottomSplitter.SetSashGravity(0.5)
        splitter.SetSashPosition(int(splitter.GetSizeTuple()[0] / 4))

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

#    def onSize(self, event):
#        print event

if __name__ == '__main__':
    app = wx.App()
    mainwin = FishFaceApp(None, -1, 'FishFace')
    app.MainLoop()
