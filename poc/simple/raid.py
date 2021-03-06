#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io, os, sys
import time
import socket
import re
import simplejson as json
import paho.mqtt.client as mqtt
from subprocess import Popen, PIPE, STDOUT
from collections import Counter


def get_raid_status():
    try:
        cmd = '/usr/sbin/hpssacli ctrl all show config'
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.readlines()

        print(output)
    
        logicaldrive  = []
        physicaldrive = []
        
        logicaldrive_status  = []
        physicaldrive_status = []
        
        for x in output:
            line = x.strip().decode("utf-8")
            
            if line.startswith( 'logicaldrive' ): logicaldrive.append(line)
            if line.startswith( 'physicaldrive' ): physicaldrive.append(line)
        
        for y in logicaldrive:
        
            match_logicaldrive = re.search(
                    '^logicaldrive (.*) \((.*), (.*), (.*)\)$',
                    y)
        
            logicaldrive_status.append(match_logicaldrive.group(4))
            
        
        for z in physicaldrive:
            match_physicaldrive = re.search(
                    '^physicaldrive (.*) \((.*), (.*), (.*), (.*)\)$',
                    z)
        
            physicaldrive_status.append(match_physicaldrive.group(5))
        
        
        logical_all  = dict(Counter(logicaldrive_status))
        physical_all = dict(Counter(physicaldrive_status))
    

        len_of_logicaldrive  = len(logicaldrive)
        len_of_physicaldrive = len(physicaldrive_status)

        raid_status = False
        if (logical_all.get('OK', None) == len_of_logicaldrive) and \
           (physical_all.get('OK', None) == len_of_physicaldrive):
            raid_status = True

        return raid_status

    except:
        return None


def on_connect(client, userdata, flags, rc):
    print ("Connected with result code "+str(rc))



if __name__ == "__main__":

    ipaddress = '10.10.10.10'

    assert (len(ipaddress)) > 0, 'configure private address'

    client = mqtt.Client()
    client.on_connect = on_connect    

    client.connect('127.0.0.1', 1883, 10)
    client.loop_start()

    try:
        while True:

            epoch = int(time.time())
            if epoch % 10 == 0:
                hostname = socket.gethostname()
                raidstatus = get_raid_status()

                report = {
                    'hostname': hostname,
                    'ip': ipaddress,
                    'timestamp': epoch,
                    'israidok': raidstatus
                }

                print(json.dumps(report, sort_keys=True, indent=4, separators=(',', ': ')))
                client.publish("raid/" + ipaddress, json.dumps(report), 0, True)

                time.sleep(1)

            else:
                time.sleep(0.8)

    except Exception as e:
        print(e.args[0])
        sys.exit()
 
    except KeyboardInterrupt:
        sys.exit(1)


