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
    parser.add_argument('--timely', action='store_true', help="Simulates Timely in the 2-level congestion scenario")
    parser.add_argument('--hope_max', action='store_true', help="Simulates Hope-Max in the 2-level congestion scenario")
    parser.add_argument('--hope_sum', action='store_true', help="Simulates Hope-Sum in the 2-level congestion scenario")
    args = parser.parse_args()
    
    num_clients = 20
    num_leafs = 2
    if (num_clients % num_leafs != 0):
	print('ERROR: Please provide number of clients that is multiple of number of leafs.')
	return

    out_dir = './out_complexCongestion/'

    if (args.timely):
	congestion_alg = 'timely'
        os.system('ns ./lib/complexCongestion.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
	print("Timely Simulation Done!")
        timely_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	timely_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.hope_max):
	congestion_alg = 'hope_max'
        os.system('ns ./lib/complexCongestion.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
	print("Hope-Max Simulation Done!")
        hopeMax_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	hopeMax_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.hope_sum):
	congestion_alg = 'hope_sum'
        os.system('ns ./lib/complexCongestion.tcl {0} {1} {2} {3}'.format(congestion_alg, out_dir, num_clients, num_leafs))
	print("Hope-Sum Simulation Done!")
        hopeSum_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	hopeSum_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir, num_leafs)
	benchmark_tools.plot_queue(congestion_alg, out_dir)

    benchmark_tools.plot_allRTTcdf(out_dir, timely_cdf, hopeMax_cdf, hopeSum_cdf)
    benchmark_tools.plot_allTotalThp(out_dir, timely_thp, hopeMax_thp, hopeSum_thp)

if __name__ == "__main__":
    main()
