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
        self.parent = parent
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
        self.chars = sorted(self.chars.iteritems(), key=k, reverse=False)
        
        # Prepare data
        data = [[k[0], k[1]*1.0/self.numchars, "", k[1]] for k in self.chars]
        
        import graph
        self.graph = graph.digraph()
        
        nodes = []
        for i in data:
            node = BTNode()
            node.value = i[1]
            node.key = i[0]
            node.code = i[2]
            node.reference = i
            nodes.append(node)
        
        # Code
        self.code(nodes)
        
        data.reverse()
        
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
        
        self.displayGraph()
    
    def displayGraph(self):
        dot = self.graph.write(fmt='dot')
        
        import pydot
        dotgraph = pydot.graph_from_dot_data(dot)
        
        # Tmpfile
        import tempfile
        fh = tempfile.NamedTemporaryFile(suffix='.png')
        
        #dotgraph.write('graph.dot')
        dotgraph.write_png(fh.name)
        
        image = wx.Image(fh.name, wx.BITMAP_TYPE_ANY)
        
        fh.close()
        
        # Init the panel
        panel = GraphPanel(self.parent, image)
        panel.identifierTag = "Huffmann Tree"
        
        # Show the panel
        self.parent.AddPage(panel, "Huffmann Tree")
    
    def code(self, items, code=False):
        if not items or len(items) < 2:
            # Calculates code
            self.graph.add_node(items[0].gid)
            code = True
            
        if code:
            new_tree = []
            
            for i in items:
                
                if i.reference:
                    i.reference[2] = i.code
                    continue
                    
                i.left.code = i.code + "1"
                i.right.code = i.code + "0"
                
                new_tree.append(i.left)
                new_tree.append(i.right)
                
                self.graph.add_node(i.left.gid)
                self.graph.add_node(i.right.gid)
                
                self.graph.add_edge(i.gid, i.left.gid, label="1", attrs=[('shape', 'rectangle'),])
                self.graph.add_edge(i.gid, i.right.gid, label="0")
                
            if len(new_tree):
                return self.code(new_tree, True)
            
            return
            
        def compare(x, y):
            if x.value > y.value:
                return 1
            elif x.value == y.value:
                return 0
            else:
                return -1
                
        items.sort(compare, reverse=True)
        
        parent = BTNode()
        parent.left = items.pop()
        parent.right = items.pop()
        parent.value = parent.left.value + parent.right.value
        parent.key = "%s%s" % (parent.left.key, parent.right.key)
        items.append(parent)
        
        self.code(items)
        
class GraphPanel(wx.Panel):
    def __init__(self, parent, image):
        wx.Panel.__init__(self, parent)
        
        w, h = parent.GetClientSizeTuple()
        ow = image.GetWidth()
        oh = image.GetHeight()
        rw = (w-40)*1.0/ow
        rh = (h-40)*1.0/oh
        
        r = min(rw, rh)
        
        nw = ow * r
        nh = oh * r
        
        image.Rescale(nw, nh, wx.IMAGE_QUALITY_HIGH)
        image.Resize((w, h), (20, 20), 255, 255, 255)
        
        
        bmp = image.ConvertToBitmap()
        
        self.graph = wx.StaticBitmap(self, -1, bmp, (0, 0), (bmp.GetWidth(), bmp.GetHeight()))
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        
        self.sizer.Add(self.graph, 1)
        
class BTNode(object):
    left = None
    right = None
    value = None
    key = None
    code = ""
    parent = None
    reference = None

    def graph(self):
        if not self.left:
            code = self.code
        else:
            code = ""

        return "%s %.5f %s" % (self.key, self.value, code)
    gid = property(graph)

    def __repr__(self):
        left = right = 0

        if self.left:
            left = self.left.value

        if self.right:
            right = self.right.value

        return "<%s : %s : %s Left: %f, Right: %f>" % (self.key, self.value, self.code, left, right)

    def __str__(self):
        return "%s: %d" % (self.key, self.value)