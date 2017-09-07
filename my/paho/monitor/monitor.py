#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io, os, sys
import time
import socket
import json
import requests
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print ("Connected with result code "+str(rc))
    client.subscribe(subscribetopic, qos=0)

def on_message(client, userdata, msg):
#    print(now(), msg.topic, msg.payload)
    result = json.loads(msg.payload.decode("utf-8"))
    print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))    

def now():
    return int(time.time())


if __name__ == "__main__":

    hostname = socket.gethostname()

    mqtt_clientid = hostname + '_some_randome_fixed_string_0'

    subscribetopic = 'report/#'

    client = mqtt.Client(client_id=mqtt_clientid)
    client.on_connect = on_connect    
    client.on_message = on_message

    client.connect('172.17.1.1', port=1883, keepalive=10)

    try:
        client.loop_forever()

    except Exception as e:
        client.disconnect()        
        print(e.args[0])
        sys.exit()

    except KeyboardInterrupt:
        client.disconnect()
        sys.exit(1)


