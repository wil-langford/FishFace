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
        self.createMainWindow()
        self.Show(True)

    def createMainWindow(self):
        """Build widgets and show window."""

        self.SetSize((800, 600))

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
        dummy_splitter, leftPanel, self.viewPanel = self._splitWidget(self, paneStyle2=wx.SUNKEN_BORDER, minPaneSize=250)

        # Left splitter (top panel from bottom panel)
        leftSplitter, temp1, temp2 = self._splitWidget(leftPanel, vertical=False)
        self.sourcesPanel = SourcesTreePanel(leftSplitter, 'tree')
        leftSplitter.ReplaceWindow(temp1, self.sourcesPanel)
        self.chainsPanel = ChainsListPanel(leftSplitter)
        leftSplitter.ReplaceWindow(temp2, self.chainsPanel)

        temp1.Destroy()
        temp2.Destroy()

        self.chainsPanel.bar.butAdd.Bind(wx.EVT_BUTTON, self.onAddChain)
        self.sourcesPanel.bar.butAdd.Bind(wx.EVT_BUTTON, self.onAddSource)
        self.chainsPanel.bar.butRemove.Bind(wx.EVT_BUTTON, self.onRemoveChain)
        self.sourcesPanel.bar.butRemove.Bind(wx.EVT_BUTTON, self.onRemoveSource)
        self.chainsPanel.bar.butEdit.Bind(wx.EVT_BUTTON, self.onEditChain)
        self.sourcesPanel.bar.butEdit.Bind(wx.EVT_BUTTON, self.onEditSource)
        self.chainsPanel.bar.butCopy.Bind(wx.EVT_BUTTON, self.onCopyChain)
        self.sourcesPanel.bar.butCopy.Bind(wx.EVT_BUTTON, self.onCopySource)

        src = self.sourcesPanel.treeCtrl
        chn = self.chainsPanel.listCtrl

        srcroot = src.AddRoot('Sources')

        for i in range(10):
            item = src.AppendItem(srcroot, "Source {}".format(i))
            src.AppendItem(item, "Subitem {}".format(i))
            chn.Append(["Chain {}".format(i)])

    def _splitWidget(self, parentWidget, vertical=True, minPaneSize=120, paneStyle1=wx.NORMAL, paneStyle2=wx.NORMAL, sizerAxis=wx.VERTICAL):
        splitter = wx.SplitterWindow(parentWidget, style=wx.SP_3D)
        panel1 = wx.Panel(splitter, style=paneStyle1)
        panel2 = wx.Panel(splitter, style=paneStyle2)

        # split vertically or horizontally
        if vertical:
            splitfunc = splitter.SplitVertically
        else:
            splitfunc = splitter.SplitHorizontally
        splitfunc(panel1, panel2)

        splitter.SetMinimumPaneSize(minPaneSize)

        sizer = wx.BoxSizer(sizerAxis)
        sizer.Add(splitter, 1, wx.EXPAND)
        parentWidget.SetSizer(sizer)

        return splitter, panel1, panel2

    #########################################

    def onAddChain(self, event):
        print "Adding chain!"

    def onAddSource(self, event):
        print "Adding source!"

    def onRemoveChain(self, event):
        print "Removing chain!"

    def onRemoveSource(self, event):
        print "Removing source!"

    def onEditChain(self, event):
        print "Editing chain!"

    def onEditSource(self, event):
        print "Editing source!"

    def onCopyChain(self, event):
        print "Copying chain!"

    def onCopySource(self, event):
        print "Copying source!"

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


class SourcesTreePanel(wx.Panel):
    def __init__(self, parentWidget, butAdd=True, butRemove=True, butEdit=True, butCopy=True, style=wx.SUNKEN_BORDER, setMyButtons=True):
        wx.Panel.__init__(self, parentWidget, style=style)

        vertSizer = wx.BoxSizer(wx.VERTICAL)

        self.treeCtrl = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        vertSizer.Add(self.treeCtrl, 1, wx.EXPAND)

        self.bar = ButtonBar(self, butAdd=butAdd, butRemove=butRemove, butEdit=butEdit, butCopy=butCopy, setParentButtons=setMyButtons)
        vertSizer.Add(self.bar, 0, wx.ALL)
        self.SetSizer(vertSizer)


class ChainsListPanel(wx.Panel):
    def __init__(self, parentWidget, butAdd=True, butRemove=True, butEdit=True, butCopy=True, style=wx.SUNKEN_BORDER, setMyButtons=True):
        wx.Panel.__init__(self, parentWidget, style=style)

        vertSizer = wx.BoxSizer(wx.VERTICAL)

        self.listCtrl = wx.ListCtrl(self)
        vertSizer.Add(self.listCtrl, 1, wx.EXPAND)

        self.bar = ButtonBar(self, butAdd=butAdd, butRemove=butRemove, butEdit=butEdit, butCopy=butCopy, setParentButtons=setMyButtons)
        vertSizer.Add(self.bar, 0, wx.ALL)
        self.SetSizer(vertSizer)


class ButtonBar(wx.Panel):
    def __init__(self, parentWidget, butAdd=True, butRemove=True, butEdit=True, butCopy=True, setParentButtons=True):
        wx.Panel.__init__(self, parentWidget)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        if butAdd or butRemove or butEdit or butCopy:
            if butAdd:
                self.butAdd = wx.Button(self, id=wx.ID_ADD, style=wx.BU_EXACTFIT)
                sizer.Add(self.butAdd)
                if setParentButtons:
                    parentWidget.butAdd = self.butAdd
            if butRemove:
                self.butRemove = wx.Button(self, id=wx.ID_REMOVE, style=wx.BU_EXACTFIT)
                sizer.Add(self.butRemove)
                if setParentButtons:
                    parentWidget.butRemove = self.butRemove
            if butEdit:
                self.butEdit = wx.Button(self, id=wx.ID_EDIT, style=wx.BU_EXACTFIT)
                sizer.Add(self.butEdit)
                if setParentButtons:
                    parentWidget.butEdit = self.butEdit
            if butCopy:
                self.butCopy = wx.Button(self, id=wx.ID_COPY, style=wx.BU_EXACTFIT)
                sizer.Add(self.butCopy)
                if setParentButtons:
                    parentWidget.butCopy = self.butCopy
        else:
            raise FishFaceAppError("ButtonBar is helpless without buttons.")
        self.SetSizer(sizer)


class FishFaceAppError(Exception):
    pass


if __name__ == '__main__':
    app = wx.App()
    mainwin = FishFaceApp(None, -1, 'FishFace')
    app.MainLoop()
