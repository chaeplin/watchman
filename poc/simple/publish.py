#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io, os, sys
import time
import socket
import simplejson as json
import psutil
import paho.mqtt.client as mqtt

def get_load_average():
    try:
        raw_average = os.getloadavg()
        load_average = { '1min': raw_average[0], '5min': raw_average[1], '15min': raw_average[2] }

        return load_average

    except:
        return None

def get_cpu_percent():
    try:
        raw_percent = psutil.cpu_times_percent(interval=1, percpu=False)
        cpu_percent = round(100 - raw_percent.idle, 1)

        return cpu_percent
 
    except:
        return None


def get_virtual_memory():
    try:
        raw_vmem = psutil.virtual_memory()
        vmem_usage = raw_vmem.percent
    
        return vmem_usage

    except:
        return None

def get_disk_usage():
    try:
        raw_disk = psutil.disk_usage('/')
        disk_usage = raw_disk.percent

        return disk_usage

    except:
        return None

def get_process_list():
    try:
        process = []
        for p in psutil.process_iter():
            info = p.as_dict(attrs=["pid", "cmdline", "username", "memory_percent", "cpu_percent"])
            info["cmdline"] = " ".join(info["cmdline"]).strip()

            if len(info.get('cmdline', None)) > 0:
                process.append(info)


        return process

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
            if epoch % 5 == 0:
                hostname = socket.gethostname()
                
                loadavg = get_load_average()
                cpu = get_cpu_percent()
                vmem = get_virtual_memory()
                disk = get_disk_usage()
                plist = get_process_list()
                
                report = {
                    'hostname': hostname,
                    'ip': ipaddress,
                    'timestamp': epoch,
                    'loadavg': loadavg,
                    'cpu': cpu,
                    'vmem': vmem,
                    'disk': disk,
                    'plist': plist
                    }
                
                
                print(json.dumps(report, sort_keys=True, indent=4, separators=(',', ': ')))
    
                client.publish("host/" + ipaddress, json.dumps(report), 0, True)
                
                time.sleep(1)

            else:
                time.sleep(0.8)
    
   
    except Exception as e:
        print(e.args[0])
        sys.exit()
 
    except KeyboardInterrupt:
        sys.exit(1)


