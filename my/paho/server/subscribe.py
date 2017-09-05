#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# /etc/rc.local 
# sleep 60 && su - pi -c "screen -dm -S mqtt /home/pi/mqtt/subscribe.py"

import io, os, sys
import time
import socket
import json
import requests
import paho.mqtt.client as mqtt
import threading
from collections import deque

webhook_url = 'https://hooks.slack.com/services/xxx/xxx/xxx'

class threading_sendslack(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if len(q) > 0:
                mm = '\n'.join(q)
                q.clear()

                slack_data = { "text": mm }

                try:
                    response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
                    if response.status_code != 200:
                        print('slack post failed')

                except:
                    pass

                time.sleep(1)

def start_slackpost():
    spost = threading_sendslack()
    spost.start()

def on_connect(client, userdata, flags, rc):
    print ("Connected with result code "+str(rc))
    client.subscribe(subscribetopic, qos=0)

def on_message(client, userdata, msg):
    print(now(), msg.topic, msg.payload)
    try:   
        result = json.loads(msg.payload.decode("utf-8"))

        host_status = result.get('msg', None)
        host_name   = result.get('hostname', None)

        slack_msg = host_name + ' : ' + host_status + ' - ' + str(now())
        if now() - start_time < 3:
            return

        if host_status == 'down' or host_status == 'up':
            if slack_msg_list.get(host_name, None) != None:
                old_status = slack_msg_list.get(host_name).get('host_status', None)
                if old_status != host_status:
                    slack_msg_list[host_name] = { 'host_status': host_status }
                    q.append(slack_msg)

            else:
                slack_msg_list[host_name] = { 'host_status': host_status }
                q.append(slack_msg)

    except:
        pass


def now():
    return int(time.time())


if __name__ == "__main__":


    q  = deque(maxlen=100)
    slack_msg_list = {}
    start_time = now()

    start_slackpost()

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
