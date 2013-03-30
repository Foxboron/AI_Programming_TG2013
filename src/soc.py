#!/usr/bin/env python2

import socket
from time import sleep
import random

class soc(object):
    """Socket code bitches!"""
    send_stuff = None
    def __init__(self, server=None, port=None):
        self.server = "0.0.0.0"
        self.port = 54321
        self.s = None
        self.nick = ""
        self.error = ""


    def init(self, ip=None, port=None):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if ip and port:
                self.s.connect((ip, port))
            else:
                self.s.connect((self.server, self.port))
        except Exception, e:
            print e
            print "Retrying..."
            sleep(3)
            self.init()
        nick_list = ["fox", "rev", "lol", "bot", "fucktard", "goat", "lasergoat", "kjeppjageren"]
        self.nick = "kjeppjageren" #random.choice(nick_list)
        st = '{"message": "connect", "revision": 1, "name": %s}' % self.nick
        self.send(st)

    def run(self):
        rec = self.s.recv(4096)
        if rec:
            if "error" in rec:
                self.error = rec
            self.send_stuff(rec)

    def send(self, msg):
        try:
            if self.s == None:
                return
            print msg
            self.s.sendall(msg+"\n")
        except Exception, e:
            print e

ai_soc = soc()



