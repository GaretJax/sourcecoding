import wx
import wx.grid


class Grid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        
        self.EnableEditing(False)
        
        self.CreateGrid(0, 5, wx.grid.Grid.SelectRows)
        
        self.SetColLabelValue(0, "Count")
        self.SetColFormatNumber(0)
        
        self.SetColLabelValue(1, "Probability")
        self.SetColFormatFloat(1)
        self.SetColSize(1, 100)
        
        self.SetColLabelValue(2, "Code")
        self.SetColFormatNumber(2)
        self.SetColSize(2, 120)
             
        self.SetColLabelValue(3, "Length")
        self.SetColFormatNumber(3)
        self.SetColSize(3, 60)
             
        self.SetColLabelValue(4, "Average")
        self.SetColFormatFloat(4)
        self.SetColSize(4, 80)
        
        # Alignment
        attrs = wx.grid.GridCellAttr()
        attrs.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
        self.SetColAttr(2, attrs)

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
        
        # Prepare data
        data = [[k[0], k[1]*1.0/self.numchars, "", k[1]] for k in self.chars]
        
        # Code
        self.code(data)
        
        # Update the table
        from math import log
        
        self.grid.AppendRows(len(data)+1)
        currentRow = 0
        total = 0
        for char, probability, code, count in data:
            p = count*1.0/self.numchars
            average = len(code)*probability
            total += average
            
            self.grid.SetRowLabelValue(currentRow, char)
            self.grid.SetCellValue(currentRow, 0, "%d" % count)
            self.grid.SetCellValue(currentRow, 1, "%.7f" % p)
            self.grid.SetCellValue(currentRow, 2, code)
            self.grid.SetCellValue(currentRow, 3, "%d" % len(code))
            self.grid.SetCellValue(currentRow, 4, "%.7f" % average)
            
            currentRow += 1
        
        attrs = wx.grid.GridCellAttr()
        attrs.SetBackgroundColour((200, 200, 200))
        self.grid.SetRowAttr(currentRow, attrs)
        
        # Total row
        self.grid.SetRowLabelValue(currentRow, "Total")
        self.grid.SetCellValue(currentRow, 0, "%d" % self.numchars)
        self.grid.SetCellValue(currentRow, 1, "%.7f" % 1)
        self.grid.SetCellValue(currentRow, 4, "%.7f" % total)
    
    def code(self, items, prefix="", tot_prob=1.0):
        """
        Calculates the code of single characters using the shannon-fano algorithm.
        The supplied items argument should be in the form:

        >>> ((char, probability, code),) with code an empty string

        The list or tuple has to be ordered from the biggest to the smallest
        probability.
        """

        if len(items) < 2:
            items[0][2] += prefix
            return

        # Init
        sum = 0
        delta = 0
        prev_delta = 1
        probability = 1.0

        # Top and bottom
        top = []
        bottom = []

        # Separate items
        for i in items:
            sum += i[1]
            i[2] += prefix

            delta = abs(tot_prob/2-sum)

            if delta > prev_delta:
                bottom.append(i)
            else:
                top.append(i)
                probability = sum

            prev_delta = delta

        self.code(top, "0", probability)
        self.code(bottom, "1", tot_prob-probability)