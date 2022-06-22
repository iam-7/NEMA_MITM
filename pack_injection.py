import socket
from scapy.all import *
from NMEA import *


class Packet:
    def __init__(self, src, dst, dport):
        self.src = src
        self.dst = dst
        self.dport
        self.pkt = None

    def create_packet(self):
        l3 = IP(src = self.src, dst = self.dst)
        l4 = UDP()        
        return

    def create_payload():
        return


