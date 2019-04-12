#!/usr/bin/env python

"""
Controls the NS-2 simulation runs
"""

import os, sys, re
import numpy as np
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#from matplotlib.backends.backend_pdf import PdfPages

def plot_rtt(algo_name, repro_dir):
    fmat = r"(?P<time>[\d.]*) (?P<rtt>[\d.]*)"

    in_file = repro_dir+algo_name+'.rtt.out'
    out_file = repro_dir+algo_name+'.rtt.png'
    cdf_file = repro_dir+algo_name+'.rttCDF.png'

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
    plt.plot(time,rtt,linestyle='-', marker='', label=algo_name)
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
    plt.xlim(0,300)
    plt.xlabel('RTT (usec)')
    plt.title('CDF of RTT for '+algo_name+' experiment')
    plt.plot(sorted_data, yvals, linestyle='-', marker='', label=algo_name)
    plt.savefig(cdf_file)
    print "Saved plot: ", cdf_file

def plot_throughput(algo_name, num_clients, repro_dir):
    
    nam_file = repro_dir+algo_name+'.nam'
    out_file = repro_dir+algo_name+'_thp.png'
    granularity = 0.001
    clock = 0
    sum_bytes = []
    time = []

    num_nodes = num_clients + 2 # First 2 nodes are TOR and the Server
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
    plt.plot(time,throughputs[0],linestyle='-', marker='', label='TOR Switch')
    for i in range(2,num_nodes):
	node_name = 'client_{}'.format(i)
        plt.plot(time,throughputs[i],linestyle='-', marker='', label=node_name)
    plt.yscale('log')
    plt.ylabel('Throughput (bps)')
    plt.xlabel('Time (sec)')
    plt.title('Throughput for '+algo_name+' experiment')
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
    plt.grid()
    plt.savefig(out_file, bbox_inches="tight")
    print "Saved plot: ", out_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dctcp', action='store_true', help="Simulates DCTCP with the setup proposed in Timely paper")
    parser.add_argument('--vegas', action='store_true', help="Simulates VEGAS as a reference for the Timely implementation")
    parser.add_argument('--timely', action='store_true', help="Simulates Timely with the setup proposed in Timely paper")
    args = parser.parse_args()
    
    num_clients = 10
    repro_dir = './reproduction_out/'

    if (args.dctcp):
	congestion_alg = 'dctcp'
        os.system('ns ./lib/reproduction.tcl {0} {1} {2}'.format(congestion_alg, repro_dir, num_clients))
	print("DCTCP Simulation Done!")
        plot_rtt(congestion_alg, repro_dir)
	plot_throughput(congestion_alg, num_clients, repro_dir)

    if (args.vegas):
	congestion_alg = 'vegas'
        os.system('ns ./lib/reproduction.tcl {0} {1} {2}'.format(congestion_alg, repro_dir, num_clients))
	print("Vegas Simulation Done!")
        plot_rtt(congestion_alg, repro_dir)
	plot_throughput(congestion_alg, num_clients, repro_dir)

    if (args.timely):
	congestion_alg = 'timely'
        os.system('ns ./lib/reproduction.tcl {0} {1} {2}'.format(congestion_alg, repro_dir, num_clients))
	print("Timely Simulation Done!")
        plot_rtt(congestion_alg, repro_dir)
	plot_throughput(congestion_alg, num_clients, repro_dir)

if __name__ == "__main__":
    main()
