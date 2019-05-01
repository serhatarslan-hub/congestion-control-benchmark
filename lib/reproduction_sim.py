#!/usr/bin/env python

"""
Controls the NS-2 Reproduction simulation runs
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
    parser.add_argument('--dctcp', action='store_true', help="Simulates DCTCP with the setup proposed in Timely paper")
    parser.add_argument('--vegas', action='store_true', help="Simulates VEGAS as a reference for the Timely implementation")
    parser.add_argument('--timely', action='store_true', help="Simulates Timely with the setup proposed in Timely paper")
    args = parser.parse_args()
    
    num_clients = 10
    out_dir = './out_reproduction/'

    if (args.dctcp):
	congestion_alg = 'dctcp'
        os.system('ns ./lib/reproduction.tcl {0} {1} {2}'.format(congestion_alg, out_dir, num_clients))
	print("DCTCP Simulation Done!")
        dctcp_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	dctcp_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.vegas):
	congestion_alg = 'vegas'
        os.system('ns ./lib/reproduction.tcl {0} {1} {2}'.format(congestion_alg, out_dir, num_clients))
	print("Vegas Simulation Done!")
        vegas_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	vegas_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
	benchmark_tools.plot_queue(congestion_alg, out_dir)
    if (args.timely):
	congestion_alg = 'timely'
        os.system('ns ./lib/reproduction.tcl {0} {1} {2}'.format(congestion_alg, out_dir, num_clients))
	print("Timely Simulation Done!")
        timely_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir)
	timely_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
	benchmark_tools.plot_queue(congestion_alg, out_dir)

    benchmark_tools.plot_allRTTcdf(out_dir, dctcp=dctcp_cdf, vegas=vegas_cdf, timely=timely_cdf)
    benchmark_tools.plot_allTotalThp(out_dir, dctcp=dctcp_thp, vegas=vegas_thp, timely=timely_thp)

if __name__ == "__main__":
    main()
