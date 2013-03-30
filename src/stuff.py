#!/usr/bin/env python2
from src.soc import ai_soc
from src.pos import Position
from src.skyport import SkyportTransmitter
from src.a import AStar
import random
import time
import operator

nick_list = ["fox", "rev", "lol", "bot", "fucktard", "goat"]

global rest_walks
rest_walks = []

global l_enemy_pos
l_enemy_pos = []

global attack_info
attack_info = {}

global mine_n
mine_n = 0

global player_pos
player_pos = 0

global choose_weps
choose_weps = []
# while len(choose_weps) != 2:
#     asdasd = ["droid", "mortar", "laser"]
#     fghfgh = random.choice(asdasd)
#     if fghfgh not in choose_weps:
#         choose_weps.append(fghfgh)

global SkyTrans
SkyTrans = SkyportTransmitter(ai_soc.send)

global resources_to_mine
resources_to_mine = []

global laser_level
laser_level = 0

global mortar_level
mortar_level = 0

global droid_level
droid_level = 0

global resources_mined
resources_mined = {
    "E": 0, 
    "R": 0, 
    "C": 0
}

global player
player = 0

global turns
turns = 0

global enemies
enemies = {}


def init(*args):
    """Inits the AI."""
    print "Init"


def error(arg):
    """Error dude....."""
    print arg


def parse_pos(pos):
    j,k = pos.split(", ")
    pospos = (int(j),int(k))
    return pospos

def gamestate(turn, board, players):
    """Handle stats."""
    global resources_mined
    global laser_level
    global droid_level
    global mortar_level
    global player
    global turns
    global enemies
    global player_pos
    global mine_n
    global l_enemy_pos
    global attack_info
    global rest_walks
    if players[0]["name"] == ai_soc.nick:
        time_dis_shit = time.time()
        enem = []
        enemy_pos = []
        l_enemy_pos = []
        enemies = {}
        for i in players:
            #print i["name"]
            if i["name"] == ai_soc.nick:
               player_pos = parse_pos(i["position"])
               #print player_pos
            else:
                if i["health"] > 0:
                    enemy_j, enemy_k= i["position"].split(", ")
                    enemy_pos = (int(enemy_j), int(enemy_k))
                    if board["data"][enemy_pos[0]][enemy_pos[1]] != "S":
                        l_enemy_pos.append(enemy_pos)
                    enemies[i["name"]] = i
        turns = 0
        pos = Position(board, player_pos)
        new_pos = player_pos
        player = players[0]
        player["position"] = player_pos
        print "------------------------"
        print "Relturn:", turn
        for _ in range(3):
            #Upgrade
            if resources_mined:
                upgrade_weps()

            hgsf = []
            # if attack_info:
            #     print "Avoiding"
            #     hgsf = avoid_enemy_attack(board["data"],attack_info)
            #     print "Avoided with: ", hgsf
            #     SkyTrans.send_move(hgsf)
            #     new_pos = next_move(new_pos, hgsf)
            #     turns += 1
            #     attack_info = []
            if turns >= 3: break
            if pos.main != "S":
                #Attack
                if enemy_pos:
                    attack_player(enemy_pos, board["data"], new_pos, l_enemy_pos)
                if turns >= 3: break
                if pos.main in resources_to_mine:
                    if pos.main != "C" and droid_level != 3 or \
                        pos.main != "E" and mortar_level != 3 or \
                        pos.main != "R" and laser_level != 3:
                        while True:
                            SkyTrans.mine()
                            turns += 1
                            mine_n += 1
                            resources_mined[pos.main] += 1
                            if mine_n >= 2:
                                mine_n = 0
                                break
                            if turns >= 3:
                                break
                        if turns >= 3:
                            break
                if turns >= 3: break
            if resources_mined:
                upgrade_weps()
            if turns >= 3: break
            #walks
            walks = node_walks(board["data"], new_pos, enemy=l_enemy_pos)
            if not walks:
                try:
                    walks = node_walks(board["data"], new_pos, enemy=[], nodes=l_enemy_pos)
                except Exception, e:
                    pass
            if turns >= 3: break
            if walks:
                SkyTrans.send_move(walks[0])
                new_pos = next_move(new_pos, walks[0])
                turns += 1
            else:
                walk_random = random_next_move(board["data"], player_pos)
                SkyTrans.send_move(walk_random)
                new_pos = next_move(new_pos, walk_random)
                turns += 1
            pos = Position(board, new_pos)
            rest_walks = []
            walks.pop(0)
            rest_walks = walks
            if turns >= 3: break
        print "Time: ", time.time() - time_dis_shit

def gamestart(*args):
    """Handles the game start."""
    global choose_weps
    global resources_to_mine
    res_on_map = {}
    wep_list = {"E": "mortar", "C": "droid", "R": "laser"}
    for i in args[1]["data"]:
        for j in i:
            if j not in res_on_map and j not in ["V","G","O","S"]:
                res_on_map[j] = 0
            if j not in ["V","G","O","S"]:
                res_on_map[j] += 1
    wep_1 = max(res_on_map.iteritems(), key=operator.itemgetter(1))[0]
    res_on_map.pop(wep_1)
    wep_2 = max(res_on_map.iteritems(), key=operator.itemgetter(1))[0]
    choose_weps.append(wep_list[wep_1])
    choose_weps.append(wep_list[wep_2])
    SkyTrans = SkyportTransmitter(ai_soc.send)
    SkyTrans.send_loadout(choose_weps[0], choose_weps[1])
    if "droid" in choose_weps:
        resources_to_mine.append("C")
    if "mortar" in choose_weps:
        resources_to_mine.append("E")
    if "laser" in choose_weps:
        resources_to_mine.append("R")


#    {"message":"subtitle","text":"LaserGoat got killed by Tard"}
#    {"message":"action","stop":"11, 6","start":"5, 6","direction":"left-down","from":"Tard","type":"laser"}

def action(*args):
    """Handles the action."""
    global attack_info
    #reset if dead
    if args[0] == "subtitle" and ai_soc.nick+" got killed by " in args[2]["text"]:
        global rest_walks
        rest_walks = []

        global l_enemy_pos
        l_enemy_pos = []

        global attack_info
        attack_info = {}

        global mine_n
        mine_n = 0

        global player_pos
        player_pos = 0

        global laser_level
        laser_level = 0

        global mortar_level
        mortar_level = 0

        global droid_level
        droid_level = 0

        global resources_mined
        resources_mined = {
            "E": 0, 
            "R": 0, 
            "C": 0
        }
    try:
        if args[0] in ["laser", "mortar", "droid"]:
            if args[2]["message"] == "action" and parse_pos(args[2]["stop"]) == player_pos:
                attack_info["from"] = args[1]
                attack_info["to"] = player_pos
                attack_info["wep"] = args[0]
                attack_info["direction"] = args[2]["direction"]
                attack_info["pos"] = parse_pos(args[2]["start"])
                if enemies[args[1]]["primary-weapon"]["name"] == args[0]:
                    wep_lvl = enemies[args[1]]["primary-weapon"]["level"]
                elif enemies[args[1]]["secondary-weapon"]["name"] == args[0]:
                    wep_lvl = enemies[args[1]]["secondary-weapon"]["level"]
                attack_info["wep_lvl"] = wep_lvl
    except Exception, e:
        pass
    return

            


def endturn(*args):
    """Handle the end of turns."""
    pass 



#####################################
#AI_CODE


def upgrade_weps():
    global mortar_level
    global laser_level
    global droid_level
    global turns
    if turns >= 3: return
    if resources_mined["E"] >= (4 + mortar_level) and "mortar" in choose_weps:
        print "Upgraded mortar!"
        SkyTrans.upgrade("mortar")
        resources_mined["E"] = 0
        mortar_level += 1
        turns += 1
    if turns >= 3: return
    if resources_mined["R"] >= (4 + laser_level) and "laser" in choose_weps:
        print "Upgraded laser!"
        resources_mined["R"] = 0
        SkyTrans.upgrade("laser")
        laser_level += 1
        turns += 1
    if turns >= 3: return
    if resources_mined["C"] >= (4 + droid_level) and "droid" in choose_weps:
        print "Upgraded droid!"
        SkyTrans.upgrade("droid")
        droid_level += 1
        resources_mined["C"] = 0
        turns += 1
    return



def node_walks(board, new_pos, enemy=[], nodes=None):
    moves = []
    queue = []
    if not nodes:
        nodes = []
        for x in range(16):
            for y in range(16):
                if board[x][y] in resources_to_mine:
                    nodes.append((x,y))
    if nodes:
        for new_node in nodes:
            try:
                AS = AStar(board, new_pos, new_node, ["V", "S", "O"], enemy=enemy)
                AS.process()
                n = AS.convert()
                if len(n) > 0 and n not in moves:
                    moves.append(n)
            except AttributeError, e:
                pass
        try:
            queue = sorted(moves, key=len)[0]
        except Exception, e:
            queue = []
    return queue


def enemy_walks(board, new_pos, enemy_pos):
    global choose_weps
    weps = {}
    if "mortar" in choose_weps:
        mortar_possibilities = []
        for enem_pos in enemy_pos:
            AS = AStar(board, new_pos, enem_pos, ["O"])
            AS.process()
            n = AS.convert()
            if len(n) <= (2 + mortar_level):
                aim_j = enem_pos[0] - new_pos[0]
                aim_k = enem_pos[1] - new_pos[1]
                mortar_possibilities.append((aim_j,aim_k))
        if len(mortar_possibilities) >= 2:
            hp = []
            pos = []
            for i in enemies.values():
                hp.append(i["health"])
                pos.append(parse_pos(i["position"]))
            aim_j, aim_k = mortar_possibilities[hp.index(min(hp))]
            weps["mortar"] = [aim_j, aim_k]
        elif mortar_possibilities:
            aim_j, aim_k = mortar_possibilities[0]
            weps["mortar"] = [aim_j, aim_k]
            
    if "laser" in choose_weps:
        laser_possibilities = []
        for enem_pos in enemy_pos:
            AS = AStar(board, new_pos, enem_pos, ["O"])
            AS.process()
            n = AS.convert()
            if len(set(n)) == 1 and len(n) <= (5 + laser_level):
                laser_possibilities.append(n[0])
        if len(laser_possibilities) >= 2:
            hp = []
            pos = []
            for i in enemies.values():
                hp.append(i["health"])
            minimm_pos = laser_possibilities[hp.index(min(hp))]
            weps["laser"] = minimm_pos
        elif laser_possibilities:
            weps["laser"] = laser_possibilities[0]

    if "droid" in choose_weps:
        droid_possibilities = []
        for enem_pos in enemy_pos:
            AS = AStar(board, new_pos, enem_pos, ["O", "V"])
            AS.process()
            n = AS.convert()
            if len(n) <= (4+droid_level):
                droid_possibilities.append(n)
        if len(droid_possibilities) >= 2:
            hp = []
            pos = []
            for i in enemies.values():
                hp.append(i["health"])
                pos.append(parse_pos(i["position"]))
            minimm_pos = droid_possibilities[hp.index(min(hp))]
            weps["droid"] = minimm_pos
        elif droid_possibilities:
            weps["droid"] = droid_possibilities[0]
    return weps


def random_next_move(board, player_pos):
    nnmove = ["left-up","right-up","up","down","left-down","right-down"]
    possible_moves_2 = []
    for i in nnmove:
        avail_j, avail_k = next_move(player_pos,i)
        if board[avail_j][avail_k] not in ["V", "S", "O"]:
            possible_moves_2.append(i)    
    wwww = random.choice(possible_moves_2)
    return wwww

def next_move(player_pos, l):
    if l == "left-up":
        ret = (player_pos[0],player_pos[1]-1)
    elif l == "right-up":
        ret = (player_pos[0]-1,player_pos[1])
    elif l == "up":
        ret = (player_pos[0]-1,player_pos[1]-1)
    elif l == "left-down":
        ret = (player_pos[0]+1,player_pos[1])
    elif l == "down":
        ret = (player_pos[0]+1,player_pos[1]+1)
    elif l == "right-down":
        ret = (player_pos[0],player_pos[1]+1)
    return ret

def avoid_enemy_attack(board, enemy):
    moves = ["left-up", "right-up", "up", "left-down", "down", "right-down"]
    #enemy_walks(board["data"], new_pos, enemy_pos)
    #{"message":"action","stop":"11, 6","start":"5, 6","direction":"left-down","from":"Tard","type":"laser"}
    opposites = {
            "up": "down",
            "down": "up",
            "left-up":"right-down",
            "right-up": "left-down",
            "left-up": "right-down",
            "left-down": "right-down"}
    possible_moves_with_attack = []
    possible_moves = []
    for i in moves:
        j,k = next_move(player["position"], i)
        if board[j][k] not in ["V", "S", "O"] and (j,k) not in l_enemy_pos and i != opposites[enemy["direction"]]:
            if enem:
                possible_moves_with_attack.append(i)
            else:
                possible_moves.append(i)
    if possible_moves_with_attack:
        ww = random.choice(possible_moves_with_attack)
    elif rest_walks:
        ww = rest_walks[0]
    else:
        ww = random.choice(possible_moves)
    return ww


class Damager(object):

    def __init__(self, damage, level, aoe=None):
        self.damage = damage
        self.areaDmg = aoe
        self.level = level

    def dmg(self):
        return self.damage[self.level] if len(self.damage) >= self.level else None

    def aoe(self):
        return self.areaDmg

        
def attack_player(enemy_pos, board, new_pos, l_enemy_pos):
    global turns
    wep_dmgs = {}
    enem = enemy_walks(board, new_pos, l_enemy_pos)
    if enem:
        if "laser" in enem:
            lazer = Damager([16, 18, 22], laser_level)
            wep_dmgs["laser"] = lazer.dmg()
        if "mortar" in enem:
            mortar = Damager([20, 20, 25], mortar_level, 18)
            wep_dmgs["mortar"] = mortar.dmg()
        if "droid" in enem:
            droid = Damager([22, 24, 26], droid_level, 10)
            wep_dmgs["droid"] = droid.dmg()
        ch_wep = max(wep_dmgs.iteritems(), key=operator.itemgetter(1))[0]
        if ch_wep == "laser":
            SkyTrans.attack_laser(enem["laser"])
            turns += 5
            return
        if ch_wep == "mortar":
            SkyTrans.attack_mortar(enem["mortar"][0], enem["mortar"][1])
            turns += 5
            return
        if ch_wep == "droid":
            SkyTrans.attack_droid(enem["droid"])
            turns += 5
            return
    return



