#!/usr/bin/env python2


class Position(object):
    dirs = {"main": None,
            "up": None,
            "left-up": None,
            "left-down": None,
            "down": None,
            "right-down": None,
            "right-up": None}

    def __init__(self, board, pos):
        self.pos = pos
        self.limits = (15, 15)
        self.board = board["data"]
        self.fields = {
            "V": False, #Void
            "S": False, #Spawn
            "O": False, #Rock
            "G": True,  #Grass
            "E": True, #Explodium
            "R": True, #Rubidium
            "C": True #Scrap
        }
        self.move = []
        self.parse(self.board, self.pos)

    def check(self,f,p):
        if self.fields[p]:
            self.move.append(f)
            return p
        return None

    def parse(self, board, pos):
        if pos[0] < 0: j = 0
        elif pos[0] > 15: j = 15
        else: j = pos[0]
        
        if pos[1] < 0: k = 0
        elif pos[1] > 15: k = 15
        else: k = pos[1]
        
        #print "(%s,%s)" % (str(j),str(k))

        try: self.main = board[j][k]
        except Exception, e:
            print e
            print j
            print k
            print pos
            print board
            exit(0)
            
            #Obsolete shit
            # if k > 0:
            #     self.dirs["left-up"] = self.check("left-up",board[j][k-1])
            
            # if j > 0:
            #     self.dirs["right-up"] = self.check("right-up",board[j-1][k])
            
            # if j > 0 and k > 0:
            #     self.dirs["up"] = self.check("up",board[j-1][k-1])
            
            # if j < self.limits[0]:
            #     self.dirs["left-down"] = self.check("left-down",board[j+1][k])
            
            # if j < self.limits[0] and k < self.limits[1]:
            #     self.dirs["down"] = self.check("down",board[j+1][k+1])
            
            # if k < self.limits[1]:
            #     self.dirs["right-down"] = self.check("right-down",board[j][k+1])

    def retstuff(self):
        ret = {k: v for k,v in self.dirs.items() if v != None}
        return ret
