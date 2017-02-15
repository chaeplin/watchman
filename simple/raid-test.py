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


def get_raid_status(seq=False):
    try:

        output1 = [b'\n', b'Smart Array P440ar in Slot 0 (Embedded)   (sn: PDNLH0BRH403FE)\n', b'\n', b'\n', b'   Port Name: 1I\n', b'\n', b'   Port Name: 2I\n', b'\n', b'   Internal Drive Cage at Port 1I, Box 1, OK\n', b'\n', b'   Internal Drive Cage at Port 2I, Box 0, OK\n', b'   array A (SATA, Unused Space: 0  MB)\n', b'\n', b'\n', b'      logicaldrive 1 (1.8 TB, RAID 1+0, OK)\n', b'\n', b'      physicaldrive 1I:1:1 (port 1I:box 1:bay 1, SATA, 1 TB, OK)\n', b'      physicaldrive 1I:1:2 (port 1I:box 1:bay 2, SATA, 1 TB, OK)\n', b'      physicaldrive 1I:1:3 (port 1I:box 1:bay 3, SATA, 1 TB, OK)\n', b'      physicaldrive 1I:1:4 (port 1I:box 1:bay 4, SATA, 1 TB, OK)\n', b'\n']   


        output2 = [b'\n', b'Smart Array P440ar in Slot 0 (Embedded)   (sn: PDNLH0BRH403FE)\n', b'\n', b'\n', b'   Port Name: 1I\n', b'\n', b'   Port Name: 2I\n', b'\n', b'   Internal Drive Cage at Port 1I, Box 1, OK\n', b'\n', b'   Internal Drive Cage at Port 2I, Box 0, OK\n', b'   array A (SATA, Unused Space: 0  MB)\n', b'\n', b'\n', b'      logicaldrive 1 (1.8 TB, RAID 1+0, OK)\n', b'\n', b'      physicaldrive 1I:1:1 (port 1I:box 1:bay 1, SATA, 1 TB, OK)\n', b'      physicaldrive 1I:1:2 (port 1I:box 1:bay 2, SATA, 1 TB, OK)\n', b'      physicaldrive 1I:1:3 (port 1I:box 1:bay 3, SATA, 1 TB, OK)\n', b'      physicaldrive 1I:1:4 (port 1I:box 1:bay 4, SATA, 1 TB, FAIL)\n', b'\n']   


        if seq:
            output = output2
        else:
            output = output1
 
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
                if epoch % 30 == 0:
                    raidstatus = get_raid_status()
                else:
                    raidstatus = get_raid_status(True)

                report = {
                    'hostname': hostname,
                    'ip': ipaddress,
                    'timestamp': epoch,
                    'israidok': raidstatus
                }

                print(json.dumps(report, sort_keys=True, indent=4, separators=(',', ': ')))
                client.publish("raid/" + hostname, json.dumps(report), 0, True)

                time.sleep(1)

            else:
                time.sleep(0.8)

    except Exception as e:
        print(e.args[0])
        sys.exit()
 
    except KeyboardInterrupt:
        sys.exit(1)



