from pprint import pprint
from NMEA import NMEA
import json

config_data = json.load(open('mitm_config.json', 'r'))

data_set = [
# "$GPRMC,090919.634,A,3500.0,S,13830.0,E,5.0,15.0,220622,,,*03",
# "$IIVHW,15.0,T,15.0,M,5.0,N,9.3,K*5A",
# "$GPVTG,15.0,T,15.0,M,5.0,N,9.3,K*41",
# "$IIHDT,15.0,T*16",
# "$GPGLL,3500.0,S,13830.0,E,090919.634,A*2F",
"$GPGGA,090919.634,3500.0,S,13830.0,E,1,4,1.5,2.0,M,,,,*26",
# "$GPGSA,A,3,8,11,15,22,,,,,,,,,1.5,1.5,1.5*0A",
# "$GPZDA,090919.634,22,06,2022,-04,00*72",
# "!AIVDO,1,1,,A,17PaewhP0jar0;1cv@h0UPNV0000,0*5A",
# "!AIVDM,1,1,,A,17PaewhP0jar0;1cv@h0UPNV0000,0*58",
# "!AIVDM,1,1,,A,13HOI:0P0000VOHLCnHQKwvL05Ip,0*23",
# "!AIVDM,1,1,,A,133sVfPP00PD>hRMDH@jNOvN20S8,0*7F",
# "!AIVDM,1,1,,B,100h00PP0@PHFV`Mg5gTH?vNPUIp,0*3B",
# "$WIMWD,285.0,T,285.0,M,11.0,N,5.7,M*68",
# "$WIMWV,294.4,R,12.1,N,A*1A",
# "$IIMTW,7.5,C*21",
# "$SDDPT,8.0,0.3*5C",
# "$SDDBT,26.2,f,8.0,M,4.4,F*38",
#     #"$SDDBK,26.2,f,8.0,M,4.4,F*27",
# "$SDDBS,26.2,f,8.0,M,4.4,F*3F",
# # "!AIVDO,2,1,9,A,57Paewh00001<To7;?@plD5<Tl0000000000000U1@:551c992TnA3QF,0*6A",
# # "!AIVDO,2,2,9,A,@00000000000002,2*5D",
# # "!AIVDM,2,1,9,A,57Paewh00001<To7;?@plD5<Tl0000000000000U1@:551c992TnA3QF,0*68",
# # "!AIVDM,2,2,9,A,@00000000000002,2*5F",
# "$IIRPM,E,1,0,10.5,A*7C",
# "$IIRPM,E,2,0,10.5,A*7F"
]

data = '!AIVDM,1,1,,A,13HOI:0P0000VOHLCnHQKwvL05Ip,0*23'
print(len(data))

nmea = NMEA(sentence= data)
nmea.decode()
pprint(nmea.data)

targets = list(config_data.keys())

for data in data_set:
    
    sentence_type = data.split(",")[0][1:]
    if sentence_type in targets:
        nmea_obj = NMEA(sentence = data)
        nmea_obj.decode()
        # pprint(nmea_obj.data)
        print(nmea_obj.sentence)
        
        for item in list(config_data[sentence_type]['attributes']):
            if item['incremental']:
                print(type(nmea_obj.data[item['key']]))
                nmea_obj.modify_attr(item['key'], str(float(nmea_obj.data[item['key']]) + item['value']))
            
            else:
                nmea_obj.modify_attr(item['key'], item['value'])
        
        print(nmea_obj.sentence)
        print(type(str(nmea_obj.sentence)))

