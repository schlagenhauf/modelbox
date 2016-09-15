#!/usr/bin/env python2

import socket
import time
import math

class Client:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        self.ip = ip
        self.port = port


    def send(self, data):
        # do some packing here
        msg = data[0] + "\0" + data[1]
        self.sock.sendto(msg, (self.ip, self.port))


if __name__=='__main__':
    client = Client('localhost',1234)

    # send some model properties
    i = 0
    while True:
        value = str(math.sin(i))
        i += 0.1
        data = ("cube_rot_x", value)
        client.send(data)
        time.sleep(1)
