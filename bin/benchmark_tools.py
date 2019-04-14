#!/usr/bin/env python

import os, sys, re
import numpy as np
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot_rtt(algo_name, out_dir):
    fmat = r"(?P<time>[\d.]*) (?P<rtt>[\d.]*)"

    in_file = out_dir+algo_name+'.rtt.out'
    out_file = out_dir+algo_name+'.rtt.png'
    cdf_file = out_dir+algo_name+'.rttCDF.png'

    time = []
    rtt = []
    with open(in_file) as f:
        for line in f:
            searchObj = re.search(fmat, line)
            if searchObj is not None:
                t = float(searchObj.groupdict()['time'])
                time.append(t)
                s = float(searchObj.groupdict()['rtt'])
                rtt.append(s)
    plt.figure()
    plt.plot(time,rtt,'.', label=algo_name)
    plt.ylabel('RTT (usec)')
    plt.xlabel('Time (sec)')
    plt.title('RTT for '+algo_name+' experiment')
    plt.grid()
    plt.savefig(out_file)
    print "Saved plot: ", out_file

    # Compute the CDF
    sorted_data = np.sort(rtt)
    yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
    plt.figure()
    #plt.xlim(0,300)
    plt.xlabel('RTT (usec)')
    plt.title('CDF of RTT for '+algo_name+' experiment')
    plt.plot(sorted_data, yvals, '.', label=algo_name)
    plt.savefig(cdf_file)
    print "Saved plot: ", cdf_file

def plot_throughput(algo_name, num_clients, out_dir, num_leafs=1):
    
    nam_file = out_dir+algo_name+'.nam'
    out_file = out_dir+algo_name+'_thp.png'
    granularity = 0.001
    clock = 0
    sum_bytes = []
    time = []

    num_nodes = num_clients + num_leafs + 1
    throughputs = []
    for i in range(num_nodes):
	throughputs.append([])
	sum_bytes.append(0.0)

    with open(nam_file) as f:
        for line in f:
            split_line = line.split()
            if ((split_line[0] == 'r' and split_line[8] == 'tcp')):
                t = float(split_line[2])
		
		if ( t-clock < granularity):
		    s = int(split_line[4]) #source node
		    if ( s != 0 or int(split_line[6]) == 1):
		        sum_bytes[s] += int(split_line[10])
		
		else:
		    time.append(t)
		    clock += granularity
		    
		    for i in range(num_nodes):
			dummy_thp = sum_bytes[i] * 8 /granularity
			throughputs[i].append(dummy_thp)
			sum_bytes[i] = 0.0
		    s = int(split_line[4]) #source node
		    sum_bytes[s] += int(split_line[10])
    time.append(t)
    for i in range(num_nodes):
	dummy_thp = sum_bytes[i] * 8 /granularity
	throughputs[i].append(dummy_thp)

    plt.figure()
    for i in range(num_nodes):
	node_name = 'node_{}'.format(i)
        plt.plot(time,throughputs[i],linestyle='-', marker='', label=node_name)
	#plt.plot(time,throughputs[i],linestyle='-', marker='')
    plt.yscale('log')
    plt.ylabel('Throughput (bps)')
    plt.xlabel('Time (sec)')
    plt.title('Throughput for '+algo_name+' experiment')
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
    plt.grid()
    plt.savefig(out_file, bbox_inches="tight")
    print "Saved plot: ", out_file

"""
Parse the sampled queue size output file and plot the queue size over time
"""
def plot_queue(algo_name, out_dir):
    fmat = r"(?P<time>[\d.]*) (?P<from_node>[\d]*) (?P<to_node>[\d]*) (?P<q_size_B>[\d.]*) (?P<q_size_p>[\d.]*) (?P<arr_p>[\d.]*) (?P<dep_p>[\d.]*) (?P<drop_p>[\d.]*) (?P<arr_B>[\d.]*) (?P<dep_B>[\d.]*) (?P<drop_B>[\d.]*)"

    in_file = out_dir+algo_name+'.queue.out'
    out_file = out_dir+algo_name+'.queue.png'

    time = []
    q_size = []
    with open(in_file) as f:
        for line in f:
            searchObj = re.search(fmat, line)
            if searchObj is not None:
                t = float(searchObj.groupdict()['time'])
                time.append(t)
                s = float(searchObj.groupdict()['q_size_p'])
                q_size.append(s)
    
    plt.figure()
    plt.plot(time,q_size,linestyle='-', marker='', label='Queue in packets')
    plt.yscale('log')
    #plt.xscale('log')
    #plt.xlim(0,0.2)
    plt.ylabel('Queue (packets)')
    plt.xlabel('Time (sec)')
    plt.title('Queue size for '+algo_name+' experiment')
    plt.grid()
    plt.savefig(out_file, bbox_inches="tight")
    print "Saved plot: ", out_file

