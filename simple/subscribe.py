#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import json
import os

import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print ("Connected with result code "+str(rc))
    #client.subscribe('host/#', 0)
    client.subscribe([("host/#", 0), ("raid/#", 0)])

def on_message(client, userdata, msg):
    #print (msg.topic+" "+str(msg.payload))
    result = json.loads(msg.payload.decode("utf-8"))
    #print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))

    ip    = result.get('ipaddress')
    check   = result.get('timestamp')

    if msg.topic.startswith( 'host' ):
        onemin  = result.get('loadavg').get('1min')
        print("%s\t%s\t%s" % (ip, check, onemin))

    if msg.topic.startswith( 'raid' ):
        physical_status = result.get('raid').get('physical_status')
        print("%s\t%s\t%s" % (ip, check, physical_status))


if __name__ == "__main__":

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect('127.0.0.1', 1883, 10)
    
    try:
        client.loop_forever()
    
    except KeyboardInterrupt:
        sys.exit(1)