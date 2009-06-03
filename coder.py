import wx, os
import wx.aui
from wx import grid

import gui_ids as ids

class BasicApp(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, "Sourcecoding - Jonathan Stoppani")
        frame.Show(True)
        
        return True

class MainWindow(wx.Frame):
    data = None
    chars = {}
    
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=(0, 0), size=wx.DisplaySize())
        
        # Status bar
        self.CreateStatusBar()
        self.GetStatusBar().SetStatusText("Open a file to begin processing")
        
        # Menus
        filemenu = wx.Menu()
        filemenu.Append(ids.ABOUT, "&About", "Information about this program")
        filemenu.Append(ids.OPEN, "&Open", "Open a new file")
        filemenu.Append(ids.EXIT, "&Exit", "Terminate the programm")
        
        # Menubar
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        
        self.SetMenuBar(menubar)
        
        # Toolbar
        toolbar = wx.ToolBar(self, style=(wx.TB_HORZ_LAYOUT | wx.TB_TEXT))
        self.SetToolBar(toolbar)
        toolbar.AddLabelTool(ids.OPEN, 'Open', wx.Bitmap("resources/folder_database.png"))
        toolbar.AddSeparator()
        toolbar.AddLabelTool(ids.ANALYZE, 'Analyze', wx.Bitmap("resources/database_lightning.png"))
        toolbar.AddSeparator()
        toolbar.AddLabelTool(ids.SHANNON, 'Shannon-Fano', wx.Bitmap("resources/table_lightning.png"))
        toolbar.AddLabelTool(ids.HUFFMANN, 'Huffmann', wx.Bitmap("resources/table_lightning.png"))
        toolbar.AddLabelTool(ids.LEMPELZIV, 'Lempel-Ziv', wx.Bitmap("resources/table_lightning.png"))
        toolbar.AddLabelTool(ids.ALL, 'All', wx.Bitmap("resources/table_multiple.png"))
        toolbar.AddSeparator()
        toolbar.AddLabelTool(ids.TREE, 'Save Huffmann Tree', wx.Bitmap("resources/sitemap.png"))
        toolbar.Realize()
        
        # Events
        wx.EVT_MENU(self, ids.ABOUT,     self.onAbout)
        wx.EVT_MENU(self, ids.OPEN,      self.onOpen)
        wx.EVT_MENU(self, ids.EXIT,      self.onExit)
        wx.EVT_MENU(self, ids.ANALYZE,   self.onAnalyze)
        wx.EVT_MENU(self, ids.SHANNON,   self.onShannon)
        wx.EVT_MENU(self, ids.HUFFMANN,  self.onHuffmann)
        wx.EVT_MENU(self, ids.LEMPELZIV, self.onAnalyze)
        wx.EVT_MENU(self, ids.ALL,       self.onAnalyze)
        wx.EVT_MENU(self, ids.TREE,      self.onAnalyze)
        
        # Notebook
        self.notebook = wx.aui.AuiNotebook(self) #style=not wx.AUINOTEBOOK_CLOSE_BUTTON)
        
        # Notebook tabs
        #self.notebook.AddPage(DataGrid(self.notebook), "Analysis")
        #self.notebook.AddPage(DataGrid(self.notebook), "Shannon-Fano")
        #self.notebook.AddPage(DataGrid(self.notebook), "Huffmann")
        #self.notebook.AddPage(DataGrid(self.notebook), "Lempel-Ziv")
        
        # Sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        
        self.Maximize()
        
        # Shortcuts
        self.data = open('/Users/garetjax/Desktop/bible_en.txt').read()
        self.onAnalyze(None)
        
    def onOpen(self, e):
        self.dirname = ""
        chooser = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)

        if chooser.ShowModal() == wx.ID_OK:
            self.filename = chooser.GetFilename()
            self.dirname = chooser.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.data = f.read()
            self.GetStatusBar().SetStatusText("%s opened and ready for processing" % self.filename)
            f.close()

        chooser.Destroy()
    
    def onShannon(self, e):
        from sourcecoding import shannon
        
        # Init the panel
        panel = shannon.Panel(self.notebook)
        panel.identifierTag = "Shannon-Fano"
        
        # Process the data
        panel.process(self.data)
        
        # Show the panel
        self.notebook.AddPage(panel, "Shannon-Fano")
    
    def onHuffmann(self, e):
        from sourcecoding import huffmann
        
        # Init the panel
        panel = huffmann.Panel(self.notebook)
        panel.identifierTag = "Huffmann"
        
        # Process the data
        panel.process(self.data)
        
        # Show the panel
        self.notebook.AddPage(panel, "Huffmann")
        
    def onAnalyze(self, e):
        from sourcecoding import analyze
        
        # Init the panel
        panel = analyze.Panel(self.notebook)
        panel.identifierTag = "Analyze"
        
        # Process the data
        panel.process(self.data)
        
        # Show the panel
        self.notebook.AddPage(panel, "Analyze")
        
        
    def onAbout(self, e):
        about = wx.MessageDialog(self, "A sample editor in \n wxPython", "About Sample Editor", wx.OK)
        about.ShowModal()
        about.Destroy()
    
    def onExit(self, e):
        self.Close(True)

BasicApp(1).MainLoop()