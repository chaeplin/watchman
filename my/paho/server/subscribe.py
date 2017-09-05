#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# /etc/rc.local 
# sleep 60 && su - pi -c "screen -dm -S mqtt /home/pi/mqtt/s.py"

import io, os, sys
import time
import socket
import json
import requests
import paho.mqtt.client as mqtt
import threading

webhook_url = 'https://hooks.slack.com/services/xxx/xxx/xxx'

class threading_sendslack(threading.Thread):

    def __init__(self, msgtoslack, evtime):
        threading.Thread.__init__(self)
        self.msgtoslack = msgtoslack
        self.evtime = evtime

    def run(self):
        slack_data = { "text": self.msgtoslack + ' - ' + str(self.evtime) }
        print(slack_data)
        try:
            response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
            if response.status_code != 200:
                print('slack post failed')

        except:
            pass

def start_slackpost(msgtoslack, evtime):
    spost = threading_sendslack(msgtoslack, evtime)
    spost.start()


def sendslack(msgtoslack, evtime):
    slack_data = { "text": msgtoslack + ' - ' + str(evtime) }

    print(slack_data)
    response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
         raise ValueError('Request to slack returned an error %s, the response is:\n%s' % (response.status_code, response.text))

def on_connect(client, userdata, flags, rc):
    print ("Connected with result code "+str(rc))
    client.subscribe(subscribetopic, qos=0)
#    client.subscribe("$SYS/#", qos=0)

def on_message(client, userdata, msg):
#    print (msg.topic+" "+str(msg.payload))
#    result = json.loads(msg.payload.decode("utf-8"))

    print(now(), msg.topic, msg.payload)
    try:   
        result = json.loads(msg.payload.decode("utf-8"))
    #   print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))

    #    use redis to store last status of client to filter out same msg
        host_status = result.get('msg', None)
        if host_status == 'down' or host_status == 'up':
            start_slackpost((result.get('hostname') + ' is ' + host_status), now())
            #sendslack((result.get('hostname') + ' is ' + host_status), now())

    except:
        pass

def now():
    return int(time.time())


if __name__ == "__main__":

    hostname = socket.gethostname()

    mqtt_clientid = hostname + '_some_randome_fixed_string_0'

    subscribetopic = 'system_updown/#'

    client = mqtt.Client(client_id=mqtt_clientid)
    client.on_connect = on_connect    
    client.on_message = on_message

    client.connect('127.0.0.1', port=1883, keepalive=10)

    try:
        client.loop_forever()

    except Exception as e:
        client.disconnect()        
        print(e.args[0])
        sys.exit()

    except KeyboardInterrupt:
        client.disconnect()
        sys.exit(1)

