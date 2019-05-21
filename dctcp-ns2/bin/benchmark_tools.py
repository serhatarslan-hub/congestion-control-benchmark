#!/usr/bin/env python

import os, sys, re
import numpy as np
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
from random import sample


def plot_rtt(algo_name, out_dir, log_plot=True, nplot=20):
    """
    Plots connection RTTs from nplot sampled connections.

    Returns CDF plot data across ALL flows to be used for overlay plot.
    """
    in_file = out_dir+algo_name+'.rtt.out'
    out_file = out_dir+algo_name+'.rtt.png'
    cdf_file = out_dir+algo_name+'.rttCDF.png'

    rtts = defaultdict(lambda: ([])) 

    with open(in_file, "r") as f:
        for line in f:
            time, fid, rtt = line.split()
            t = float(time)
            f = int(fid)
            r = float(rtt)
            rtts[f].append((t, r))

    # List of var-length 2d arrays
    rtts = [np.array(rtts[f]) for f in sorted(rtts.keys())]

    # Get all RTTs for later
    all_rtts = np.array([rtt[1] for flow in rtts for rtt in flow])

    # Just pick a subset of nplot
    plot_rtts = sample(rtts, nplot)

    plt.figure()
    for data in plot_rtts:
        mean = np.mean(data[:, 1])
        std = np.std(data[:, 1])

        smooth = 10
        y = data[:, 1]
        y = np.convolve(y, np.ones((smooth,))/smooth, mode='same')
        label = r"($\mu$=" + ("%d, SD=%d)" % (round(mean), round(std)))
        plt.plot(data[:, 0], y, linestyle='-', marker='', label=label)
    if log_plot:
        plt.yscale('log')
    plt.ylim([0,300])
    plt.ylabel('RTT (usec)')
    plt.xlabel('Time (sec)')
    plt.title('RTT for '+algo_name+' experiment')
    plt.grid()
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
    plt.savefig(out_file, bbox_inches="tight")
    print("Saved plot: %s" % out_file)
    plt.close()

    # Compute the CDF
    sorted_data = np.sort(all_rtts)
    yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
    plt.figure()
    #plt.xlim(0,300)
    #plt.xscale('log')
    plt.xlabel('RTT (usec)')
    plt.title('CDF of RTT for '+algo_name+' experiment')
    plt.plot(sorted_data, yvals, '.', label=algo_name)
    plt.savefig(cdf_file)
    print "Saved plot: ", cdf_file
    plt.close()

    return sorted_data, yvals


def plot_allRTTcdf(out_dir, log_plot=True, dctcp=None, vegas=None, timely=None,
                   hopeSum=None, hopeMax=None, \
                   hopeMaxq=None, hopeMaxqd=None, hopeMaxe=None, hopeMaxed=None, \
                   hopeSumq=None, hopeSumqd=None, hopeSume=None, hopeSumed=None, \
                   hopeSqu=None, hopeSquq=None):
    """
    Plot the given CDFs on the same figure for easier comparison
    """    
    allCDF_file = out_dir+'All.rttCDF_benchmark.png'
    plt.figure()
    plt.xlabel('RTT (usec)')
    plt.title('CDF of RTT for benchmarked congestion control algorithms')

    if dctcp is not None:
        plt.plot(dctcp[0], dctcp[1], '--', label='DCTCP')
    if vegas is not None:
        plt.plot(vegas[0], vegas[1], ':', label='Vegas')
    if timely is not None:
        plt.plot(timely[0], timely[1], '-', label='Timely')
    if hopeSum is not None:
        plt.plot(hopeSum[0], hopeSum[1], '-', label='Hope-Sum')
    if hopeMax is not None:
        plt.plot(hopeMax[0], hopeMax[1], '-', label='Hope-Max')
    if hopeMaxq is not None:
        plt.plot(hopeMaxq[0], hopeMaxq[1], '-', label='Hope-Maxq')
    if hopeMaxqd is not None:
        plt.plot(hopeMaxqd[0], hopeMaxqd[1], '-', label='Hope-Maxqd')
    if hopeMaxe is not None:
        plt.plot(hopeMaxe[0], hopeMaxe[1], '-', label='Hope-Maxe')
    if hopeMaxed is not None:
        plt.plot(hopeMaxed[0], hopeMaxed[1], '-', label='Hope-Maxed')
    if hopeSumq is not None:
        plt.plot(hopeSumq[0], hopeSumq[1], '-.', label='Hope-Sumq')
    if hopeSumqd is not None:
        plt.plot(hopeSumqd[0], hopeSumqd[1], '-.', label='Hope-Sumqd')
    if hopeSume is not None:
        plt.plot(hopeSume[0], hopeSume[1], '-.', label='Hope-Sume')
    if hopeSumed is not None:
        plt.plot(hopeSumed[0], hopeSumed[1], '-.', label='Hope-Sumed')
    if hopeSqu is not None:
        plt.plot(hopeSqu[0], hopeSqu[1], '-', label='Hope-Squ')
    if hopeSquq is not None:
        plt.plot(hopeSquq[0], hopeSquq[1], '-', label='Hope-Squq')

    plt.legend(loc='lower right')
    if(log_plot):
        plt.xscale('log')
    #plt.xlim(0,700)
    plt.savefig(allCDF_file)
    print "Saved plot: ", allCDF_file
    plt.close()


def plot_rate(algo_name, num_clients, out_dir, conn_per_client=1, nplot=4):
    """
    Plots a sample of the output rates for the given connections to reproduce
    Figure 13 of the TIMELY paper.

    Assumes that connection IDs are numbered
    {0, ..., num_clients*conn_per_client-1} client-by-client.
    """
    nflows = num_clients*conn_per_client

    rate_file = out_dir+algo_name+'.rate.out'
    out_file = out_dir+algo_name+'.rate.png'

    rates = defaultdict(lambda: ([])) 

    with open(rate_file, "r") as f:
        for line in f:
            time, fid, rate = line.split()
            t = float(time)
            f = int(fid)
            r = float(rate) / 1000000.0  # in mbps
            rates[f].append((t, r))

    rates = [np.array(rates[f]) for f in range(nflows)]
    rates = [r for r in rates if r.shape[0] > 0]
    print("Plotting rates. %d of %d flows had rates set" % (len(rates), nflows))

    # Just pick a subset of nplot
    plot_rates = sample(rates, nplot)

    plt.figure()
    for data in plot_rates:
        mean = np.mean(data[:, 1])
        std = np.std(data[:, 1])

        smooth = 10
        y = data[:, 1]
        y = np.convolve(y, np.ones((smooth,))/smooth, mode='same')
        label = r"($\mu$=" + ("%d, SD=%d)" % (round(mean), round(std)))
        plt.plot(data[:, 0], y, linestyle='-', marker='', label=label)

    plt.ylim([0,1100])
    plt.ylabel('Rate (Mbps)')
    plt.xlabel('Time (sec)')
    plt.title('Queue size for '+algo_name+' experiment')
    plt.grid()
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
    plt.savefig(out_file, bbox_inches="tight")
    print("Saved plot: %s" % out_file)
    plt.close()


def plot_throughput(algo_name, num_clients, out_dir, conn_per_client=1):
    """
    Plots the throughput for the first num_clients clients, assuming
    each client serves conn_per_client connections.

    Assumes client IDs are in range {0, 1, ...} and that connection IDs are
    numbered {0, ..., num_clients*conn_per_client-1} client-by-client.
    """
    tr_file = out_dir+algo_name+'.tr'
    out_file = out_dir+algo_name+'.thp.png'
    granularity = 0.001
    clock = 0

    thp_sums = np.zeros((num_clients, conn_per_client))
    seqs = np.zeros((num_clients, conn_per_client))
    throughputs = []  # becomes [time x num_clients x conn_per_client]
    times = []

    # Parse the trace file per schema explained here:
    # https://ns2blogger.blogspot.com/p/the-file-written-by-application-or-by.html
    with open(tr_file, 'r') as f:
        for line in f:
            event, time, from_node, to_node, pkt_type, pkt_size, flags, fid, \
                src_addr, dst_addr, seq_num, pkt_id = line.split()

            # Given time, source node, and flow ID
            t = float(time)
            s = int(from_node)
            f = int(fid)

            # Consider dequeued packets that fit our spec only
            if event == '-' and pkt_type == 'tcp' \
                and s < num_clients and f < num_clients*conn_per_client:
                # Let f only be the residual
                f -= s*conn_per_client

                # Only counting non-retransmissions
                if int(seq_num) > seqs[s, f]:
                    thp_sums[s, f] += int(pkt_size)
                    seqs[s, f] = int(seq_num)
                
                # Compute throughout in a sliding window of size granularity
                if t-clock >= granularity:
                    times.append(t)
                    throughputs.append(thp_sums * 8 / (t-clock) / 1000000)
                    clock += granularity

                    # Zero out
                    thp_sums.fill(0)
    # Last step
    throughputs.append(thp_sums * 8 / (t-clock) / 1000000)
    times.append(t)

    # Aggregate
    times = np.array(times)
    throughputs = np.array(throughputs)
    total_thp = np.sum(throughputs, axis=(1, 2))

    # Plot individual throughputs
    plt.figure()
    for i in range(num_clients):
        for j in range(conn_per_client):
            node_name = ('Client%d_connection_%d' % (i, j))
            plt.plot(times, throughputs[:, i, j], linestyle='-', marker='', label=node_name)

    # Plot total
    plt.plot(times,total_thp,linestyle='-', marker='', label='Total')
        
    plt.yscale('log')
    plt.ylabel('Throughput (Mbps)')
    plt.xlabel('Time (sec)')
    plt.title('Throughput for '+algo_name+' experiment')
    #plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
    plt.ylim([0,750])
    plt.grid()
    plt.savefig(out_file, bbox_inches="tight")
    print("Saved plot: %s" % out_file)
    plt.close()

    return times, total_thp

def plot_allTotalThp(out_dir, dctcp=None, vegas=None, timely=None, hopeSum=None, hopeMax=None, \
                        hopeMaxq=None, hopeMaxqd=None, hopeMaxe=None, hopeMaxed=None, \
                        hopeSumq=None, hopeSumqd=None, hopeSume=None, hopeSumed=None, \
                        hopeSqu=None, hopeSquq=None):
    """
    Plot the given throughputs in the same figure for easier comparison
    """
    allThp_file = out_dir+'All.thp_benchmark.png'
    plt.figure()
    plt.ylabel('Throughput (Mbps)')
    plt.xlabel('Time (sec)')
    plt.title('Total throughputs for benchmarked congestion control algorithms')

    if dctcp is not None:
        plt.plot(dctcp[0][:-2], dctcp[1][:-2], '-', label='DCTCP')
    if vegas is not None:
        plt.plot(vegas[0][:-2], vegas[1][:-2], ':', label='Vegas')
    if timely is not None:
        plt.plot(timely[0][:-2], timely[1][:-2], '-', label='Timely')
    if hopeSum is not None:
        plt.plot(hopeSum[0][:-2], hopeSum[1][:-2], '-', label='Hope-Sum')
    if hopeMax is not None:
        plt.plot(hopeMax[0][:-2], hopeMax[1][:-2], '-', label='Hope-Max')
    if hopeMaxq is not None:
        plt.plot(hopeMaxq[0][:-2], hopeMaxq[1][:-2], '-', label='Hope-Maxq')
    if hopeMaxqd is not None:
        plt.plot(hopeMaxqd[0][:-2], hopeMaxqd[1][:-2], '-', label='Hope-Maxqd')
    if hopeMaxe is not None:
        plt.plot(hopeMaxe[0][:-2], hopeMaxe[1][:-2], '-', label='Hope-Maxe')
    if hopeMaxed is not None:
        plt.plot(hopeMaxed[0][:-2], hopeMaxed[1][:-2], '-', label='Hope-Maxed')
    if hopeSumq is not None:
        plt.plot(hopeSumq[0][:-2], hopeSumq[1][:-2], '-.', label='Hope-Sumq')
    if hopeSumqd is not None:
        plt.plot(hopeSumqd[0][:-2], hopeSumqd[1][:-2], '-.', label='Hope-Sumqd')
    if hopeSume is not None:
        plt.plot(hopeSume[0][:-2], hopeSume[1][:-2], '-.', label='Hope-Sume')
    if hopeSumed is not None:
        plt.plot(hopeSumed[0][:-2], hopeSumed[1][:-2], '-.', label='Hope-Sumed')
    if hopeSqu is not None:
        plt.plot(hopeSqu[0][:-2], hopeSqu[1][:-2], '-', label='Hope-Squ')
    if hopeSquq is not None:
        plt.plot(hopeSquq[0][:-2], hopeSquq[1][:-2], '-', label='Hope-Squq')

    plt.legend(loc='lower right')
    plt.savefig(allThp_file)
    print "Saved plot: ", allThp_file
    plt.close()

def plot_queue(algo_name, out_dir):
    fmat = r"(?P<time>[\d.]*) (?P<from_node>[\d]*) (?P<to_node>[\d]*) (?P<q_size_B>[\d.]*) (?P<q_size_p>[\d.]*) (?P<arr_p>[\d.]*) (?P<dep_p>[\d.]*) (?P<drop_p>[\d.]*) (?P<arr_B>[\d.]*) (?P<dep_B>[\d.]*) (?P<drop_B>[\d.]*)"
    """
    Parse the sampled queue size output file and plot the queue size over time
    """
    in_file = out_dir+algo_name+'.queue.out'
    out_file = out_dir+algo_name+'.queue.png'

    dst_nodes = []
    times = []
    q_sizes = []

    #time = []
    #q_size = []
    with open(in_file) as f:
        for line in f:
            result = re.search(fmat, line)
            if result is not None:
                to_node = int(result.groupdict()['to_node'])
                t = float(result.groupdict()['time'])
                s = float(result.groupdict()['q_size_p'])
                if to_node in dst_nodes:
                    idx = dst_nodes.index(to_node)
                    times[idx].append(t)
                    q_sizes[idx].append(s)
                else:
                    dst_nodes.append(to_node)
                    times.append([t])
                    q_sizes.append([s])
                #time.append(t)
                #q_size.append(s)
    
    plt.figure()
    for i in range(len(dst_nodes)):
        queue_name = 'Queue Client_{}'.format(dst_nodes[i])
        plt.plot(times[i],q_sizes[i],linestyle='-', marker='', label=queue_name)
    #plt.plot(time,q_size,linestyle='-', marker='', label='Queue in packets')
    plt.yscale('log')
    plt.ylabel('Queue (packets)')
    plt.xlabel('Time (sec)')
    #plt.legend(loc='lower right')
    plt.title('Queue size for '+algo_name+' experiment')
    plt.grid()
    plt.savefig(out_file, bbox_inches="tight")
    print("Saved plot: %s" % out_file)
    plt.close()

def get_fct(algo_name, num_clients, out_dir):
    """
    Get Flow Completion Times of flows
    """
    tr_file = out_dir+algo_name+'.tr'
    s_flow_size = 50
    m_flow_size = 500
    l_flow_size = 1500

    start_times = []
    s_fct = []  # Short Flow Completion Time
    m_fct = []  # Mid-Length Flow Completion Time
    l_fct = []  # Long Flow Completion Time

    for i in range(num_clients):
        start_times.append(0.0)
        s_fct.append(0.0)
        m_fct.append(0.0)
        l_fct.append(0.0)

    with open(tr_file) as f:
        for line in f:
            split_line = line.split()
            
            if split_line[0] == '+' \
                  and split_line[4] == 'tcp' \
                  and int(split_line[2]) < num_clients:

                t = float(split_line[1])
                s = int(split_line[2]) #source node
                seq = int(split_line[10]) #Sequence number

                if  seq == 0 and start_times[s] == 0:
                    start_times[s] = t
                elif (seq == s_flow_size+1 or seq == s_flow_size*1460+1) \
                         and s_fct[s] == 0:
                    s_fct[s] = t - start_times[s]
                elif (seq == m_flow_size+1 or seq == m_flow_size*1460+1) \
                         and m_fct[s] == 0:
                    m_fct[s] = t - start_times[s]
                elif (seq == l_flow_size+1 or seq == l_flow_size*1460+1) \
                         and l_fct[s] == 0:
                    l_fct[s] = t - start_times[s]

    for i in range(num_clients-1,-1,-1):
        # Remove uncompleted flows
        if s_fct[i] == 0:
            del s_fct[i]
        if m_fct[i] == 0:
            del m_fct[i]
        if l_fct[i] == 0:
            del l_fct[i]
    if s_fct == []:
        # Return 0 when no flow completed
        s_fct = [0]
    if m_fct == []:
        # Return 0 when no flow completed
        m_fct = [0]
    if l_fct == []:
        # Return 0 when no flow completed
        l_fct = [0]

    return s_fct, m_fct, l_fct

def plot_allFCT(out_dir, dctcp=None, vegas=None, timely=None, hopeSum=None, hopeMax=None, \
                hopeMaxq=None, hopeMaxqd=None, hopeMaxe=None, hopeMaxed=None, \
                hopeSumq=None, hopeSumqd=None, hopeSume=None, hopeSumed=None, \
                hopeSqu=None, hopeSquq=None):
    """
    Plot the given flow completion times in the same figure for easier comparison
    """
    f_sizes = ['Short', 'Mid-Length', 'Long']    
    allFCT_file = out_dir+'All.fct_benchmark.png'

    plt.figure()
    plt.subplot(len(f_sizes),1,1)
    plt.title('CDF of Flow Completion Times')

    for i in range(len(f_sizes)):
        plt.subplot(len(f_sizes),1,i+1)
        plt.ylabel("%s Flows"%f_sizes[i])
    plt.xlabel('Time(sec)')

    if dctcp is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(dctcp[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='DCTCP')
    if vegas is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(vegas[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Vegas')
    if timely is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(timely[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Timely')
    if hopeSum is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeSum[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Sum')
    if hopeMax is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeMax[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Max')
    if hopeMaxq is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeMaxq[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Maxq')
    if hopeMaxqd is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeMaxqd[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Maxqd')
    if hopeMaxe is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeMaxe[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Maxe')
    if hopeMaxed is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeMaxed[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Maxed')
    if hopeSumq is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeSumq[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Sumq')
    if hopeSumqd is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeSumqd[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Sumqd')
    if hopeSume is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeSume[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Sume')
    if hopeSumed is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeSumed[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Sumed')
    if hopeSqu is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeSqu[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Squ')
    if hopeSquq is not None:
        # Compute the CDF for all sizes
        for i in range(len(f_sizes)):
            sorted_data = np.sort(hopeSquq[i])
            yvals = np.arange(len(sorted_data))/float(len(sorted_data)-1)
            plt.subplot(len(f_sizes),1,i+1)
            plt.plot(sorted_data, yvals, '-', label='Hope-Squq')

    for i in range(len(f_sizes)):
        plt.subplot(len(f_sizes),1,i+1)
        plt.legend(loc='lower right')

    plt.savefig(allFCT_file)
    print "Saved plot: ", allFCT_file
    plt.close()

def print_1ClientFCT(out_dir, dctcp=None, vegas=None, timely=None, hopeSum=None, hopeMax=None, \
                     hopeMaxq=None, hopeMaxqd=None, hopeMaxe=None, hopeMaxed=None, \
                     hopeSumq=None, hopeSumqd=None, hopeSume=None, hopeSumed=None, \
                     hopeSqu=None, hopeSquq=None):
    """
    Report the given flow completion times of algorithms for 1 client simulations
    """
    f_sizes = ['Short', 'Mid-Length', 'Long']    
    allFCT_file = out_dir+'All.fct_benchmark.txt'

    report = "\n****** Flow Completion Times ******\n"
    report += "{:>12} ".format("Algorithm")
    for size in f_sizes:
        report += "| {0: >16} ".format(size+' Flows')
    report += "\n"

    if dctcp is not None:
        report += "{:>12} ".format("DCTCP")
        for i in range(len(f_sizes)):
            size = dctcp[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if vegas is not None:
        report += "{:>12} ".format("Vegas")
        for i in range(len(f_sizes)):
            size = vegas[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if timely is not None:
        report += "{:>12} ".format("Timely")
        for i in range(len(f_sizes)):
            size = timely[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeSum is not None:
        report += "{:>12} ".format("Hope-Sum")
        for i in range(len(f_sizes)):
            size = hopeSum[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeMax is not None:
        report += "{:>12} ".format("Hope-Max")
        for i in range(len(f_sizes)):
            size = hopeMax[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeMaxq is not None:
        report += "{:>12} ".format("Hope-Maxq")
        for i in range(len(f_sizes)):
            size = hopeMaxq[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeMaxqd is not None:
        report += "{:>12} ".format("Hope-Maxqd")
        for i in range(len(f_sizes)):
            size = hopeMaxqd[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeMaxe is not None:
        report += "{:>12} ".format("Hope-Maxe")
        for i in range(len(f_sizes)):
            size = hopeMaxe[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeMaxed is not None:
        report += "{:>12} ".format("Hope-Maxed")
        for i in range(len(f_sizes)):
            size = hopeMaxed[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeSumq is not None:
        report += "{:>12} ".format("Hope-Sumq")
        for i in range(len(f_sizes)):
            size = hopeSumq[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeSumqd is not None:
        report += "{:>12} ".format("Hope-Sumqd")
        for i in range(len(f_sizes)):
            size = hopeSumqd[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeSume is not None:
        report += "{:>12} ".format("Hope-Sume")
        for i in range(len(f_sizes)):
            size = hopeSume[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeSumed is not None:
        report += "{:>12} ".format("Hope-Sumed")
        for i in range(len(f_sizes)):
            size = hopeSumed[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeSqu is not None:
        report += "{:>12} ".format("Hope-Squ")
        for i in range(len(f_sizes)):
            size = hopeSqu[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"
    if hopeSquq is not None:
        report += "{:>12} ".format("Hope-Squq")
        for i in range(len(f_sizes)):
            size = hopeSquq[i][0]*1000
            report += "| {0: >16} ".format(size)
        report += "\n"

    report += "*All the times are given in miliseconds.\n\n"

    print(report)
    with open(allFCT_file,"w") as fo:
        fo.write(report) 

    print("Saved report to %s" % allFCT_file)
