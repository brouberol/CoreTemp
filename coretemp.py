#!/usr/bin/env python

import subprocess
import collections
import datetime
import time
import matplotlib.pyplot as plt

from math import ceil

NB_PROBES = 30

def probe_temperature():
    """ Return the CPU and GPU temperature, in degrees centigrade (Celcius) """
    cmd = "inxi -s | grep Sensors | awk '{print $6,$10}'" # Get CPU/GPU temperatures 
    # INFO : inxi is a shell command sending back all sorts of informations: disk usage, cpu clock, sensors information, etc
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    temp, error = p.communicate()
    cpu_temp, gpu_temp = [int(float(x[:-1])) for x in temp.replace('\n','').split(' ')] # remove the 'C' (celcius)
    return cpu_temp, gpu_temp

def probe_for_duration(hour=0, minute=0, second=0):
    """ Probe the CPU/GPU temperature for the input duration 
    Returns 2 OrderedDict with keys: time of the measurement and 
    values: temperature

    """
    duration = datetime.time(hour=hour, minute=minute, second=second)
    duration_in_seconds = (3600*hour) + (60 * minute) + second
    sleep_time_in_seconds = ceil(float(duration_in_seconds) / NB_PROBES) # sleep time between 2 measurments
    
    # Init
    nb_probes = 0
    cpu_temps = collections.OrderedDict()
    gpu_temps = collections.OrderedDict()
    
    # Measurements
    while nb_probes < NB_PROBES:
        current_time = time.asctime().split(' ')[4] # Get measurement time. We split because we're only interested in the HH:MM:SS signal
        cpu_temp, gpu_temp =  probe_temperature()
        cpu_temps[current_time] = cpu_temp
        gpu_temps[current_time] = gpu_temp
        
        nb_probes += 1
        time.sleep(sleep_time_in_seconds) # wait until next measurement
        
    return cpu_temps, gpu_temps

def plot_temperatures(cpu_temps, gpu_temps):
    """ Plot CPU/GPU temperature evolution over time """
    # Plot structure
    fig = plt.figure(figsize=(16,10))
    plt.grid()
    x = range(len(cpu_temps))

    cpu_avg = sum([t for t in cpu_temps.values()])/float(len([t for t in cpu_temps.values()]))
    gpu_avg = sum([t for t in gpu_temps.values()])/float(len([t for t in gpu_temps.values()]))
    cpu_avg_plot = plt.axhline(y=cpu_avg, xmin=0, xmax=len(cpu_temps), color='r', linestyle='--')
    gpu_avg_plot = plt.axhline(y=gpu_avg, xmin=0, xmax=len(gpu_temps), color='b', linestyle='--')
    cpu_plot = plt.plot(x, cpu_temps.values(), 'ro-')
    gpu_plot = plt.plot(x, gpu_temps.values(), 'bo-')
    locs, labels = plt.xticks(x, cpu_temps.keys())
    plt.ylim(ymin = min([temp for temp in cpu_temps.values() + gpu_temps.values()]) - 1,
             ymax = max([temp for temp in cpu_temps.values() + gpu_temps.values()]) + 3)
    plt.xlim(xmin=-1, xmax=len(x))
    fig.autofmt_xdate() 
    plt.ylabel("Temperature (in Celcius)")
    plt.legend([gpu_plot, gpu_avg_plot, cpu_plot, cpu_avg_plot], 
               ["GPU temperature", "Average GPU temperature : %.1fC" %(gpu_avg), "CPU", "Average CPU temperature : %.1fC" %(cpu_avg)],
               loc = "best")
    plt.suptitle("Evolution of the CPU/GPU temperature\nbetween %s and %s" %(cpu_temps.keys()[0], cpu_temps.keys()[-1]), fontsize=20)
    plt.savefig("CPU_GPU_temperature.png")

if __name__ == '__main__': 
    
    cpu, gpu = probe_for_duration(hour=0, minute=15, second=0)
    plot_temperatures(cpu, gpu)
