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

sys.path.append(os.path.expandvars('$BENCHMARK_NS2/bin/'))
import benchmark_tools

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dctcp', action='store_true', help="Simulates DCTCP in the 2-level congestion scenario")
    parser.add_argument('--timely', action='store_true', help="Simulates Timely in the 2-level congestion scenario")
    parser.add_argument('--hope_sum', action='store_true', help="Simulates Hope-Sum in the 2-level congestion scenario")
    parser.add_argument('--hope_max', action='store_true', help="Simulates Hope-Max in the 2-level congestion scenario")
    parser.add_argument('--hope_maxq', action='store_true', help="Simulates Hope-Maxq in the 2-level congestion scenario")
    parser.add_argument('--hope_maxqd', action='store_true', help="Simulates Hope-Maxqd in the 2-level congestion scenario")
    parser.add_argument('--hope_maxe', action='store_true', help="Simulates Hope-Maxe in the 2-level congestion scenario")
    parser.add_argument('--hope_maxed', action='store_true', help="Simulates Hope-Maxed in the 2-level congestion scenario")
    args = parser.parse_args()
    
    num_clients = 20
    num_leafs = 2
    if (num_clients % num_leafs != 0):
	print('ERROR: Please provide number of clients that is multiple of number of leafs.')
	return

    out_dir = './out_topology2/'

    dctcp_cdf = None
    dctcp_thp = None
    timely_cdf = None
    timely_thp = None
    hopeSum_cdf = None
    hopeSum_thp = None
    hopeMax_cdf = None
    hopeMax_thp = None
    hopeMaxq_cdf = None
    hopeMaxq_thp = None
    hopeMaxqd_cdf = None
    hopeMaxqd_thp = None
    hopeMaxe_cdf = None
    hopeMaxe_thp = None
    hopeMaxed_cdf = None
    hopeMaxed_thp = None

    if (args.dctcp):
	congestion_alg = 'dctcp'
	print("DCTCP Simulation Running...")
        os.system('ns ./lib/topology2.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
        dctcp_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	dctcp_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.timely):
	congestion_alg = 'timely'
	print("Timely Simulation Running...")
        os.system('ns ./lib/topology2.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
        timely_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	timely_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.hope_sum):
	congestion_alg = 'hope_sum'
	print("Hope-Sum Simulation Running...")
        os.system('ns ./lib/topology2.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
        hopeSum_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	hopeSum_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.hope_max):
	congestion_alg = 'hope_max'
	print("Hope-Max Simulation Running...")
        os.system('ns ./lib/topology2.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
        hopeMax_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	hopeMax_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.hope_maxq):
	congestion_alg = 'hope_maxq'
	print("Hope-Maxq Simulation Running...")
        os.system('ns ./lib/topology2.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
        hopeMaxq_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	hopeMaxq_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.hope_maxqd):
	congestion_alg = 'hope_maxqd'
	print("Hope-Maxqd Simulation Running...")
        os.system('ns ./lib/complexCongestion.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
        hopeMaxqd_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	hopeMaxqd_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.hope_maxe):
	congestion_alg = 'hope_maxe'
	print("Hope-Maxe Simulation Running...")
        os.system('ns ./lib/topology2.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
        hopeMaxe_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	hopeMaxe_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.hope_maxed):
	congestion_alg = 'hope_maxed'
	print("Hope-Maxed Simulation Running...")
        os.system('ns ./lib/topology2.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
        hopeMaxed_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	hopeMaxed_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)

    benchmark_tools.plot_allRTTcdf(out_dir, dctcp=dctcp_cdf, timely=timely_cdf, hopeMax=hopeMax_cdf, hopeSum=hopeSum_cdf, \
				hopeMaxq=hopeMaxq_cdf, hopeMaxqd=hopeMaxqd_cdf, hopeMaxe=hopeMaxe_cdf, hopeMaxed=hopeMaxed_cdf)
    benchmark_tools.plot_allTotalThp(out_dir, dctcp=dctcp_thp, timely=timely_thp, hopeMax=hopeMax_thp, hopeSum=hopeSum_thp, \
				hopeMaxq=hopeMaxq_thp, hopeMaxqd=hopeMaxqd_thp, hopeMaxe=hopeMaxe_thp, hopeMaxed=hopeMaxed_thp)

if __name__ == "__main__":
    main()
