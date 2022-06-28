from datetime import datetime, timezone
from xml.sax.xmlreader import AttributesNSImpl
import pynmea2
from pyais import *
from Attributes import attributes

class NMEA():

    def __init__(self, sentence = None, data = None, talker = None, sentence_type = None):
        self.sentence = sentence
        self.data = data
        self.payload_data = None
        self.talker = talker
        self.sentence_type = sentence_type

    def decode(self):

        self.data = dict()

        if self.sentence.startswith('!AIVDM') or self.sentence.startswith('!AIVDO'):
            self.talker = self.sentence.split(',')[0][1:]
            self.sentence_type = 'AIS'
            self.data = decode(self.sentence).asdict()
        else:
            payload = pynmea2.parse(self.sentence)
            self.payload_data = vars(payload)
            
            self.talker = self.payload_data['talker']
            self.sentence_type = self.payload_data['sentence_type']
            
            # print(self.sentence_type)
            # print(attributes[self.sentence_type])

            for key, value in zip(attributes[self.sentence_type], self.payload_data['data']):
                self.data[key] = value
        
    
    def encode(self):
        if self.sentence_type == 'AIS':
            self.sentence = encode_dict(self.data, talker_id=self.talker)[0]

        elif self.sentence_type == 'GGA':
            self.sentence = pynmea2.GGA(self.talker, self.sentence_type, (self.data.values()))
        
        elif self.sentence_type == 'GSA':
            self.sentence = pynmea2.GSA(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'RMC':
            self.sentence = pynmea2.RMC(self.talker, self.sentence_type, (self.data.values()))
        
        elif self.sentence_type == 'VHW':
            self.sentence = pynmea2.VHW(self.talker, self.sentence_type, (self.data.values()))
        
        elif self.sentence_type == 'VTG':
            self.sentence = pynmea2.VTG(self.talker, self.sentence_type, (self.data.values()))
        
        elif self.sentence_type == 'HDT':
            self.sentence = pynmea2.HDT(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'GLL':
            self.sentence = pynmea2.GLL(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'ZDA':
            self.sentence = pynmea2.ZDA(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'MWD':
            self.sentence = pynmea2.MWD(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'MWV':
            self.sentence = pynmea2.MWV(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'MTW':
            self.data = pynmea2.MTW(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'DPT':
            self.sentence = pynmea2.DPT(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'DBT':
            self.sentence = pynmea2.DBT(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'DBS':
            self.sentence = pynmea2.DBS(self.talker, self.sentence_type, (self.data.values()))

        elif self.sentence_type == 'RPM':
            self.sentence = pynmea2.RPM(self.talker, self.sentence_type, (self.data.values()))

    def modify_attr(self, key, value):
        if key not in self.data:
            print(f"[-] Key '{key}' does not exist in '{self.sentence_type}', Please check supported attributes for the sentence type")
            return
        
        self.data[key] = value
        self.encode()
    
class AIS:
    def __init__(self, sentence= None, data=None, talker = None):
        #self.description = "AIS NMEA sentance handler"
        self.sentence = sentence
        self.data = decode(sentence).asdict() if sentence else data
        self.talker = talker
        
    def encode(self):
        return

    def alter_field(self, field_name, field_value):
        self.ais_dict[field_name] = field_value
        self.modified_sentence = encode_dict(self.ais_dict, talker_id="AIVDM")

class NMEA_GGA:
    def __init__(self, talker = None, data = None, sentence = None):

        self.talker = talker
        self.data = data
        self.chksum = None
        self.sentence = sentence
        self.payload = None

    def calc_chksum(self):
        calc_chksum = 0
        for s in self.payload:
            calc_chksum ^= ord(s)

        self.chksum = format(calc_chksum, 'X')

        return self.chksum

    def encode(self):
        prefix = self.talker + "GGA,"
        data = ""
        for values in self.data.values():
            data += str(values) + ","
        data = data[:-1]    
        self.payload = prefix + data
        self.calc_chksum()
        self.sentence = "$" + self.payload + "*" + self.chksum

        self.sentence
    
    def decode(self):
        
        if self.sentence:
            payload_data = self.sentence.split(",")
            self.data["time"] = payload_data[1]
            self.data["latitude"] = payload_data[2]
            self.data["ns"] = payload_data[3]
            self.data["longitude"] = payload_data[4]
            self.data["ew"] = payload_data[5]
            self.data["quality"] = payload_data[6]
            self.data["numberSatellites"] = payload_data[7]
            self.data["hdop"] = payload_data[8]
            self.data["altitude"] = payload_data[9]
            self.data["altitudeUnit"] = payload_data[10]
            self.data["geoidalSeparation"] = payload_data[11]
            self.data["geoidalSeparationUnit"] = payload_data[12]
            self.data["differentialAge"] = payload_data[13]
            self.data["differentialStationId"] = payload_data[14]
            self.chksum = payload_data[15].strip("*")
            
        
if __name__ == '__main__':

    data = b"!AIVDM,1,1,,A,13HOI:0P0000VOHLCnHQKwvL05Ip,0*23"

    ais = AIS(sentence = data)
    print(ais.data)
    talker = "GP"
    # data = {
    # "time": "083122.540",#datetime.utcnow().strftime("%H%M%S.%f").rstrip("0"),
    # "latitude": "3705.414",
    # "ns" : "N",
    # "longitude": "07514.063" ,
    # "ew" : "W",
    # "quality": 1,
    # "numberSatellites": 12,
    # "hdop": 1.0,
    # "altitude": 0.0,
    # "altitudeUnit": "M",
    # "geoidalSeparation": 0.0,
    # "geoidalSeparationUnit": "M",
    # "differentialAge": "",
    # "differentialStationId": "",
    # }
    # nmeagga = NMEA_GGA(talker, data)
    # nmeagga.encode()
    # print(nmeagga.sentence)

    # data_set = ["$GPGGA,083122.540,3705.414,N,07514.063,W,1,12,1.0,0.0,M,0.0,M,,*75",
    # "$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30"
    # ,"$GPRMC,083122.540,A,3705.414,N,07514.063,W,139839.8,100.1,180622,000.0,W*5F"]
    # for sentence in data_set:
    #     nmea = NMEA(sentence = sentence)
    #     nmea.decode()
    #     print(nmea.data)
    #     print()
    #     #nmea.modify_attr(Attributes.altitude, '10.0')
    #     #nmea.encode()
    #     print(nmea.sentence)
    #     print()
    #     print("-------------------------------------------------------------------------")
    
    # talker = 'GP'
    # sentence_type = 'RMC'
    # data = {'time': '083122.540', 'status': 'A', 'lat': '3705.414', 'lat_dir': 'N', 'lon': '07514.063', 'lon_dir': 'W', 'spd_over_grnd': '139839.8', 'true_course': '100.1', 'date': '180622', 'mag_variation': '000.0', 'mag_variation_dir': 'W'}
    # nmea = NMEA(data=data, sentence_type= sentence_type, talker=talker)
    # nmea.encode()
    # print(nmea.data)
    # print(nmea.sentence)



# def calc_chksum(sentence):
#     sentence = sentence.strip('\n')
#     nmea_data, chksum = sentence.split('*', 1)
#     calc_chksum = 0
#     for s in nmea_data:
#         calc_chksum ^= ord(s)

#     return nmea_data, chksum, hex(calc_chksum)

# data = ["GPGGA,002153.000,3342.6618,N,11751.3858,W,1,10,1.2,27.0,M,-34.2,M,,0000*5E"]

# for row in data:
#     nmea_data, chksum, calc_sum = calc_chksum(row)