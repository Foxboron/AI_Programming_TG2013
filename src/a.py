
import heapq

class Cell(object):
    def __init__(self, x, y, reachable):
        """
        Initialize new cell

        @param x cell x coordinate
        @param y cell y coordinate
        @param reachable is cell reachable? not a wall?
        """
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0
        self.xy = (self.x, self.y)

class AStar(object):
    def __init__(self, board, start, end, cant_move, enemy=None):
        if enemy:
            self.enemy = enemy
        else:
            self.enemy = []
        self.board = board
        self.start = start
        self.end = end
        self.cant = cant_move
        self.op = []
        heapq.heapify(self.op)
        self.cl = set()
        self.cells = {}
        self.gridHeight = 15
        self.gridWidth = 15
        self.ll = []
        self.init_grid()
    
    def init_grid(self):
        for x in range(self.gridWidth+1):
            for y in range(self.gridHeight+1):
                if self.board[x][y] in self.cant:
                    reachable = False
                elif (x, y) in self.enemy:
                    reachable = False
                else:
                    reachable = True
                self.cells[(x,y)] = Cell(x, y, reachable)
        self.start = self.get_cell(self.start[0],self.start[1])
        try:
            self.end = self.get_cell(self.end[0],self.end[1])
        except:
            pass
            #print self.end


    def get_heuristic(self, cell):
        """
        Compute the heuristic value H for a cell: distance between
        this cell and the ending cell multiply by 10.

        @param cell
        @returns heuristic value H
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))


    def get_cell(self, x, y):
        """
        Returns a cell from the cells list

        @param x cell x coordinate
        @param y cell y coordinate
        @returns cell
        """
        l = self.cells[(x,y)]
        return l


    def get_adjacent_cells(self, cell):
        """
        Returns adjacent cells to a cell. Clockwise starting
        from the one on the right.

        @param cell get adjacent cells for this cell
        @returns adjacent cells list 
        """
        cells = []        
        #up-right
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y-1))
        
        #up-left
        if cell.x > 0:
            cells.append(self.get_cell(cell.x-1, cell.y))
        
        #up
        if cell.x > 0 and cell.y > 0:
            cells.append(self.get_cell(cell.x-1, cell.y-1))
        
        #down-right
        if cell.x < self.gridWidth:
            cells.append(self.get_cell(cell.x+1, cell.y))
        
        #down
        if cell.y < self.gridHeight and cell.x < self.gridWidth:
            cells.append(self.get_cell(cell.x+1, cell.y+1))
        
        #down-left
        if cell.y < self.gridHeight:
            cells.append(self.get_cell(cell.x, cell.y+1))
        return cells

    def display_path(self):
        cell = self.end
        self.ll.append(self.end.xy)
        while cell.parent is not self.start:
            cell = cell.parent
            self.ll.append((cell.x, cell.y))
        self.ll.append(self.start.xy)
        self.ll = self.ll[::-1]

    def update_cell(self, adj, cell):
        """
        Update adjacent cell

        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def convert(self):
        paths = self.ll
        moves = {
            (0,-1): "left-up",
            (-1,0): "right-up",
            (-1,-1): "up",
            (1,0): "left-down",
            (1,1): "down",
            (0,1): "right-down"}
        p = []
        for i in range(len(paths)-1):
            n = paths[i]
            n2 = paths[i+1]
            try:
                p.append(moves[(n2[0]-n[0],n2[1]-n[1])])
            except Exception, e:
                p.append((n[0]-n2[0],n[1]-n2[1]))
        return p

    def process(self):
        # add starting cell to open heap queue
        heapq.heappush(self.op, (self.start.f, self.start))
        while len(self.op):
            # pop cell from heap queue 
            f, cell = heapq.heappop(self.op)
            # add cell to closed list so we don't process it twice
            self.cl.add(cell)
            # if ending cell, display found path
            if cell is self.end:
                self.display_path()
                break
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for c in adj_cells:
                if c.reachable and c not in self.cl:
                    if (c.f, c) in self.op:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found for this adj
                        # cell.
                        if c.g > cell.g + 10:
                            self.update_cell(c, cell)
                    else:
                        self.update_cell(c, cell)
                        # add adj cell to open list
                        heapq.heappush(self.op, (c.f, c))