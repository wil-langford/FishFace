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

        # Left splitter (top panel from bottom panel)
        leftSplitter = wx.SplitterWindow(leftPanel, style=wx.SP_3D)
        self.sourcesPanel = wx.Panel(leftSplitter, style=wx.SUNKEN_BORDER)
        self.chainsPanel = wx.Panel(leftSplitter)
        leftSplitter.SplitHorizontally(self.sourcesPanel, self.chainsPanel)
        leftSplitter.SetMinimumPaneSize(120)

        # Sizers and such
        leftSizer = wx.BoxSizer(wx.HORIZONTAL)
        leftSizer.Add(leftSplitter, 1, wx.EXPAND)
        leftPanel.SetSizer(leftSizer)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Source Tree
        self.sourcesTree = wx.TreeCtrl(self.sourcesPanel)
        self.sourcesButtonBar = wx.Panel(self.sourcesPanel)
        sourceSizer = wx.BoxSizer(wx.VERTICAL)
        sourceSizer.Add(self.sourcesTree, 1, wx.EXPAND)
        sourceSizer.Add(self.sourcesButtonBar, 0, wx.ALL)
        self.sourcesPanel.SetSizer(sourceSizer)

        # Chains List
        self.chainsList = wx.ListCtrl(self.chainsPanel)
        self.chainsButtonBar = wx.Panel(self.chainsPanel)
        chainsSizer = wx.BoxSizer(wx.VERTICAL)
        chainsSizer.Add(self.chainsList, 1, wx.EXPAND)
        chainsSizer.Add(self.chainsButtonBar, 0, wx.ALL)
        self.chainsPanel.SetSizer(chainsSizer)

        # button bars' layouts
        sourcesBBS = wx.BoxSizer(wx.HORIZONTAL)
        sourcesBBS.Add(wx.Button(self.sourcesButtonBar, id=wx.ID_ADD, style=wx.BU_EXACTFIT))
        sourcesBBS.Add(wx.Button(self.sourcesButtonBar, id=wx.ID_REMOVE, style=wx.BU_EXACTFIT))
        sourcesBBS.Add(wx.Button(self.sourcesButtonBar, id=wx.ID_EDIT, style=wx.BU_EXACTFIT))
        self.sourcesButtonBar.SetSizer(sourcesBBS)

        chainsBBS = wx.BoxSizer(wx.HORIZONTAL)
        chainsBBS.Add(wx.Button(self.chainsButtonBar, id=wx.ID_ADD, style=wx.BU_EXACTFIT))
        chainsBBS.Add(wx.Button(self.chainsButtonBar, id=wx.ID_REMOVE, style=wx.BU_EXACTFIT))
        chainsBBS.Add(wx.Button(self.chainsButtonBar, id=wx.ID_EDIT, style=wx.BU_EXACTFIT))
        self.chainsButtonBar.SetSizer(chainsBBS)

        # Set overall window geometry and show window
        self.SetSize((900, 600))
        self.Show(True)

        # Set initial splitter sash positions and gravities
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
