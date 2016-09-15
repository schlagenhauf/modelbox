#!/usr/bin/env python2

import socket

##
# @brief This class manages the communication with clients that want to send
# visualization data. Protocol is "<fieldname>\0<fieldvalue>"
class Net:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        self.sock.bind((ip, port))

    def start(self):
        while True:
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            dsplit = data.split('\0')
            print "Client (%s) sent: field: %s, value %s" % (addr, dsplit[0], dsplit[1])

if __name__=='__main__':
    n = Net('localhost', 1234)
    n.start()
