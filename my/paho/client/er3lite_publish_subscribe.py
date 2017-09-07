#!/usr/bin/env python
# -*- coding: utf-8 -*-

# er3list --> python 2 and paho-mqtt

import io, os, sys
import time
import socket
import json
import psutil
import paho.mqtt.client as mqtt

def get_load_average():
    try:
        raw_average = os.getloadavg()
        load_average = { '1min': raw_average[0], '5min': raw_average[1], '15min': raw_average[2] }

        return load_average

    except:
        return None

def get_phy_memory():
    try:
        raw_phymem = psutil.phymem_usage()
        phymem_usage = raw_phymem.percent
    
        return phymem_usage

    except:
        return None

def get_swap_memory():
    try:
        raw_swapmem_ = psutil.virtmem_usage()
        swap_usage = raw_swapmem_.percent
    
        return swap_usage

    except:
        return None

def get_disk_usage():
    try:
        raw_disk = psutil.disk_usage('/')
        disk_usage = raw_disk.percent

        return disk_usage

    except:
        return None

def get_network_usage():
    global net_check_first, bytes_sent, bytes_recv, packets_sent, packets_recv
    try:
        raw_net = psutil.network_io_counters(pernic=True).get('eth0')

        if not net_check_first:
            net_usage = {
                'bytes_sent': (raw_net.bytes_sent - bytes_sent)/60,
                'bytes_recv': (raw_net.bytes_recv - bytes_recv)/60,
                'packets_sent': (raw_net.packets_sent - packets_sent)/60,
                'packets_recv': (raw_net.packets_recv - packets_recv)/60
                }    

            bytes_sent = raw_net.bytes_sent
            bytes_recv = raw_net.bytes_recv
            packets_sent = raw_net.packets_sent
            packets_recv = raw_net.packets_recv

            return net_usage

        else:
            bytes_sent = raw_net.bytes_sent
            bytes_recv = raw_net.bytes_recv
            packets_sent = raw_net.packets_sent
            packets_recv = raw_net.packets_recv

            net_check_first = False
 
            return None

    except:
        return None

def get_users():
    try:
        raw_users = psutil.get_users()
        usercnt = len(raw_users)

        return usercnt

    except:
        return None

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

    hostname = 'er3lite'

    mqtt_clientid = hostname + '_some_randome_fixed_string_1'

    willtopic = 'system_updown/' + hostname
    subscribetopic = 'overload/#'
    reporttopic = 'report/' + hostname

    bytes_sent = 0
    bytes_recv = 0
    packets_sent = 0
    packets_recv = 0
    net_check_first = True


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

                loadavg = get_load_average()
                pmemp = get_phy_memory()
                smemp =get_swap_memory()
                disk = get_disk_usage()
                netusage = get_network_usage()
                users = get_users()
                
                report = {
                    'hostname': hostname,
                    'timestamp': now(),
                    'loadavg': loadavg,
                    'pmemp': pmemp,
                    'smemp': smemp,
                    'diskp': disk,
                    'netusage': netusage,
                    'users': users
                    }
                
                client.publish(reporttopic, payload=json.dumps(report), qos=0, retain=True)
                
                time.sleep(1)

            else:
                time.sleep(0.5)
   
    except Exception as e:
        print(e.args[0])
        sys.exit()
 
    except KeyboardInterrupt:
        sys.exit()

