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

sys.path.append(os.path.expandvars('$DCTCP_NS2/bin/'))
import benchmark_tools

def main():
	
	bits = [1,2,4,8,16,0]   
	num_clients = 192
	num_TORs = 8
	num_leafs = 4
	num_servers = 0
	if (num_clients % num_TORs != 0 or num_TORs % num_leafs != 0):
		print('ERROR: Please provide number of clients and number of TORs that are evenly distributable through number of leafs.')
		return

	out_dir = './out_hope_vs_bits/'
	algorithm = 'hope_maxq_'
	
	results = {}
	for bit in bits:
		results[bit] = {}
		results[bit]['cdf'] = None
		results[bit]['thp'] = None
		results[bit]['fct'] = None

	for bit in bits:
		cong_alg = algorithm+str(bit)
		print("Hope-Maxq Simulation Running for %d bits..."%bit)
		os.system('ns ./lib/hope_vs_bits.tcl {0} {1} {2} {3} {4} {5}'.format(cong_alg, bit, out_dir, num_clients, num_TORs, num_leafs))
		results[bit]['cdf'] = benchmark_tools.plot_rtt(cong_alg, out_dir, log_plot=False, nplot=num_clients/2, report_only=False)
		results[bit]['thp'] = benchmark_tools.plot_throughput(cong_alg, num_clients, out_dir, report_only=False)
		results[bit]['fct'] = benchmark_tools.get_fct(cong_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(cong_alg, out_dir)
		benchmark_tools.gen_report(cong_alg, out_dir, \
									results[bit]['cdf'], results[bit]['thp'], results[bit]['fct'])
	cong_alg = algorithm
	benchmark_tools.plot_allResults(cong_alg, out_dir, results, log_plot=False)

if __name__ == "__main__":
	main()
