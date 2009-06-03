import wx
import wx.grid

class Grid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        
        self.EnableEditing(False)
        
        self.CreateGrid(0, 4, wx.grid.Grid.SelectRows)
        
        self.SetColLabelValue(0, "Count")
        self.SetColFormatNumber(0)
        
        self.SetColLabelValue(1, "Probability")
        self.SetColFormatFloat(1)
        self.SetColSize(1, 100)
        
        self.SetColLabelValue(2, "Self-information")
        self.SetColFormatFloat(2)
        self.SetColSize(2, 130)
        
        self.SetColLabelValue(3, "Entropy")
        self.SetColFormatFloat(3)
        self.SetColSize(3, 100)

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.grid = Grid(self)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.grid, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
    
    def process(self, data):
        # Cleanup
        n = self.grid.GetNumberRows()
        if n:
            self.grid.DeleteRows(0, n)
        
        # Reset
        self.data = data
        self.numchars = 0
        self.chars = {}
        
        import re
        
        # Statistics
        for c in self.data:
            # Filter our all chars
            if not re.match(r'[A-Za-z ]', c):
                continue
            
            # Convert all to uppercase
            c = c.upper()
            
            # Change the space to a symbol
            if c == ' ':
                c = '_'
            
            # Count references
            if c not in self.chars:
                self.chars[c] = 1
            else:
                self.chars[c] += 1
                
            self.numchars += 1
        
        # Sort
        order_by = 1 # 0 = by char, 1 = by probability
        
        k = lambda (k,v): [(k,v), (v, k)][order_by]
        self.chars = sorted(self.chars.iteritems(), key=k, reverse=order_by)
        
        # Update the table
        from math import log
        
        self.grid.AppendRows(len(self.chars)+1)
        currentRow = 0
        entropy = 0
        for char, count in self.chars:
            p = count*1.0/self.numchars
            h = -log(p)/log(2)
            e = p*h
            entropy += e
            
            self.grid.SetRowLabelValue(currentRow, char)
            self.grid.SetCellValue(currentRow, 0, "%d" % count)
            self.grid.SetCellValue(currentRow, 1, "%.7f" % p)
            self.grid.SetCellValue(currentRow, 2, "%.7f" % h)
            self.grid.SetCellValue(currentRow, 3, "%.7f" % e)
            
            currentRow += 1
        
        attrs = wx.grid.GridCellAttr()
        attrs.SetBackgroundColour((200, 200, 200))
        self.grid.SetRowAttr(currentRow, attrs)
        
        # Total row
        self.grid.SetRowLabelValue(currentRow, "Total")
        self.grid.SetCellValue(currentRow, 0, "%d" % self.numchars)
        self.grid.SetCellValue(currentRow, 1, "%.7f" % 1)
        self.grid.SetCellValue(currentRow, 3, "%.7f" % entropy)