#!/usr/bin/env python2
from src.skyport import SkyportTransmitter, SkyportReceiver
from src.stuff import *
from src.soc import ai_soc
import sys
import socket


def ai_start(ip=None, port=None):
    SkyRec = SkyportReceiver()
    SkyRec.handler_handshake_successful = init
    SkyRec.handler_error = error
    SkyRec.handler_gamestate = gamestate
    SkyRec.handler_gamestart = gamestart
    SkyRec.handler_action = action
    SkyRec.handler_endturn = endturn
    ai_soc.send_stuff = SkyRec.parse_line
    ai_soc.init(ip=ip, port=port)
    while True:
        ai_soc.run()


if __name__ == '__main__':
    cmd = sys.argv
    if len(cmd) == 3:
        ip = cmd[1]
        try:
            port = int(cmd[2])
        except Exception, e:
            print "Are you 100% sure you typed a port now?"
            exit()
        ai_start(ip=ip, port=port)
    else:
        ai_start()








