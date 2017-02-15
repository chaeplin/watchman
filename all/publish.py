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
        load_average = {
                    '1min': raw_average[0], 
                    '5min': raw_average[1], 
                    '15min': raw_average[2]
                    }
        return load_average

    except:
        return None

def get_cpu_percent():
    try:
        raw_percent = psutil.cpu_times_percent(interval=1, percpu=False)
        cpu_percent = {
                    'user': raw_percent.user,
                    'nice': raw_percent.nice,
                    'system': raw_percent.system,
                    'idle': raw_percent.idle,
                    'iowait': raw_percent.iowait,
                    'irq': raw_percent.irq,
                    'softirq': raw_percent.softirq,
                    'steal': raw_percent.steal,
                    'guest': raw_percent.guest,
                    'guest_nice': raw_percent.guest_nice
                    }

        return cpu_percent
 
    except:
        return None

def get_virtual_memory():
    try:
        raw_vmem = psutil.virtual_memory()
        vmem_usage = {
                    'total': raw_vmem.total,
                    'available': raw_vmem.available,
                    'percent': raw_vmem.percent,
                    'used': raw_vmem.used,
                    'free': raw_vmem.free,
                    'active': raw_vmem.active,
                    'inactive': raw_vmem.inactive,
                    'buffers': raw_vmem.buffers,
                    'cached': raw_vmem.cached,
                    'shared': raw_vmem.shared
                }

    
        return vmem_usage

    except:
        return None

def get_swap_memory():
    try:
        raw_swap = psutil.swap_memory()
        swap_usage = {
                    'total': raw_swap.total,
                    'used': raw_swap.used,
                    'free': raw_swap.free,
                    'percent': raw_swap.percent,
                    'sin': raw_swap.sin,
                    'sout': raw_swap.sout
                }

        return swap_usage

    except:
        return None

def get_disk_usage():
    try:
        disk = {}
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    continue
            raw_usage = psutil.disk_usage(part.mountpoint)
            usage = {
                    'total': raw_usage.total,
                    'used': raw_usage.used,
                    'free': raw_usage.free,
                    'percent': raw_usage.percent
                }

            disk[part.mountpoint] = usage

        return disk

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
                swap = get_swap_memory()
                disk = get_disk_usage()
                plist = get_process_list()
                
                report = {
                    'hostname': hostname,
                    'timestamp': epoch,
                    'loadavg': loadavg,
                    'cpu': cpu,
                    'vmem': vmem,
                    'swap': swap,
                    'disk': disk,
                    'plist': plist
                    }
                
                
                #print(json.dumps(report, sort_keys=True, indent=4, separators=(',', ': ')))
    
                client.publish("host/" + hostname, json.dumps(report), 0, True)
                
                time.sleep(1)

            else:
                time.sleep(0.8)
    
   
    except Exception as e:
        print(e.args[0])
        sys.exit()
 
    except KeyboardInterrupt:
        sys.exit(1)

