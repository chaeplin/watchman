#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# /etc/rc.local 
# sleep 60 && su - pi -c "screen -dm -S mqtt /home/pi/mqtt/p.py"

import io, os, sys
import time
import socket
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print ("Connected with result code "+str(rc))
    client.publish(willtopic, payload=json.dumps(willreset), qos=0, retain=True)
    client.subscribe(subscribetopic, qos=0)

def on_message(client, userdata, msg):
    print (msg.topic+" "+str(msg.payload))
    #result = json.loads(msg.payload.decode("utf-8"))
    #print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))

def now():
    return int(time.time())

if __name__ == "__main__":

    hostname = socket.gethostname()

    mqtt_clientid = hostname + '_some_randome_fixed_string_1'

    willtopic = 'system_updown/' + hostname
    subscribetopic = 'overload/#'

    willmsg   = {
            'hostname': hostname,
            'timestamp': now(),
            'msg': 'down'
        }    

    willreset = {
            'hostname': hostname,
            'timestamp': now(),
            'msg': 'up'
        }
    

    client = mqtt.Client(client_id=mqtt_clientid)
    client.on_connect = on_connect    
    client.on_message = on_message
    client.will_set(willtopic, payload=json.dumps(willmsg), qos=0, retain=True)

    client.connect('172.17.1.1', port=1883, keepalive=90)
    client.loop_start()

    try:
        while True:

            epoch = int(time.time())
            if now() % 60 == 0:

                #client.publish()
                
                time.sleep(1)

            else:
                time.sleep(0.5)
   
    except Exception as e:
        print(e.args[0])
        sys.exit()
 
    except KeyboardInterrupt:
        sys.exit()