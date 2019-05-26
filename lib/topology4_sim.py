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
	parser = argparse.ArgumentParser()
	parser.add_argument('--dctcp', action='store_true', help="Simulates DCTCP in the topology-4 congestion scenario")
	parser.add_argument('--timely', action='store_true', help="Simulates Timely in the topology-4 congestion scenario")
	parser.add_argument('--hope_sum', action='store_true', help="Simulates Hope-Sum in the topology-4 congestion scenario")
	parser.add_argument('--hope_max', action='store_true', help="Simulates Hope-Max in the topology-4 congestion scenario")
	parser.add_argument('--hope_maxq', action='store_true', help="Simulates Hope-Maxq in the topology-4 congestion scenario")
	parser.add_argument('--hope_maxqd', action='store_true', help="Simulates Hope-Maxqd in the topology-4 congestion scenario")
	parser.add_argument('--hope_maxe', action='store_true', help="Simulates Hope-Maxe in the topology-4 congestion scenario")
	parser.add_argument('--hope_maxed', action='store_true', help="Simulates Hope-Maxed in the topology-4 congestion scenario")
	parser.add_argument('--hope_sumq', action='store_true', help="Simulates Hope-Sumq in the topology-4 congestion scenario")
	parser.add_argument('--hope_sumqd', action='store_true', help="Simulates Hope-Sumqd in the topology-4 congestion scenario")
	parser.add_argument('--hope_sume', action='store_true', help="Simulates Hope-Sume in the topology-4 congestion scenario")
	parser.add_argument('--hope_sumed', action='store_true', help="Simulates Hope-Sumed in the topology-4 congestion scenario")
	parser.add_argument('--hope_squ', action='store_true', help="Simulates Hope-Squ in the topology-4 congestion scenario")
	parser.add_argument('--hope_squq', action='store_true', help="Simulates Hope-Squq in the topology-4 congestion scenario")
	args = parser.parse_args()
    
	num_clients = 192
	num_TORs = 8
	num_leafs = 4
	num_servers = 0
	if (num_clients % num_TORs != 0 or num_TORs % num_leafs != 0):
		print('ERROR: Please provide number of clients and number of TORs that are evenly distributable through number of leafs.')
		return

	out_dir = './out_topology4/'

	dctcp_cdf = None
	dctcp_thp = None
	dctcp_fct = None
	timely_cdf = None
	timely_thp = None
	timely_fct = None
	hopeSum_cdf = None
	hopeSum_thp = None
	hopeSum_fct = None
	hopeMax_cdf = None
	hopeMax_thp = None
	hopeMax_fct = None
	hopeMaxq_cdf = None
	hopeMaxq_thp = None
	hopeMaxq_fct = None
	hopeMaxqd_cdf = None
	hopeMaxqd_thp = None
	hopeMaxqd_fct = None
	hopeMaxe_cdf = None
	hopeMaxe_thp = None
	hopeMaxe_fct = None
	hopeMaxed_cdf = None
	hopeMaxed_thp = None
	hopeMaxed_fct = None
	hopeSumq_cdf = None
	hopeSumq_thp = None
	hopeSumq_fct = None
	hopeSumqd_cdf = None
	hopeSumqd_thp = None
	hopeSumqd_fct = None
	hopeSume_cdf = None
	hopeSume_thp = None
	hopeSume_fct = None
	hopeSumed_cdf = None
	hopeSumed_thp = None
	hopeSumed_fct = None
	hopeSqu_cdf = None
	hopeSqu_thp = None
	hopeSqu_fct = None
	hopeSquq_cdf = None
	hopeSquq_thp = None
	hopeSquq_fct = None

	if (args.dctcp):
		congestion_alg = 'dctcp'
		print("DCTCP Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		dctcp_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		dctcp_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		dctcp_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.timely):
		congestion_alg = 'timely'
		print("Timely Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		timely_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		timely_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		timely_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_sum):
		congestion_alg = 'hope_sum'
		print("Hope-Sum Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeSum_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeSum_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeSum_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_max):
		congestion_alg = 'hope_max'
		print("Hope-Max Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeMax_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeMax_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeMax_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_maxq):
		congestion_alg = 'hope_maxq'
		print("Hope-Maxq Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeMaxq_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeMaxq_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeMaxq_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_maxqd):
		congestion_alg = 'hope_maxqd'
		print("Hope-Maxqd Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeMaxqd_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeMaxqd_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeMaxqd_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_maxe):
		congestion_alg = 'hope_maxe'
		print("Hope-Maxe Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeMaxe_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeMaxe_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeMaxe_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_maxed):
		congestion_alg = 'hope_maxed'
		print("Hope-Maxed Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeMaxed_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeMaxed_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeMaxed_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_sumq):
		congestion_alg = 'hope_sumq'
		print("Hope-Sumq Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeSumq_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeSumq_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeSumq_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_sumqd):
		congestion_alg = 'hope_sumqd'
		print("Hope-Sumqd Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeSumqd_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeSumqd_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeSumqd_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_sume):
		congestion_alg = 'hope_sume'
		print("Hope-Sume Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeSume_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeSume_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeSume_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_sumed):
		congestion_alg = 'hope_sumed'
		print("Hope-Sumed Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeSumed_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeSumed_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeSumed_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_squ):
		congestion_alg = 'hope_squ'
		print("Hope-Squ Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeSqu_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeSqu_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeSqu_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)
	if (args.hope_squq):
		congestion_alg = 'hope_squq'
		print("Hope-Squq Simulation Running...")
		os.system('ns ./lib/topology4.tcl {0} {1} {2} {3} {4}'.format(congestion_alg, out_dir, num_clients, num_TORs, num_leafs))
		hopeSquq_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, log_plot=False, nplot=num_clients-1)
		hopeSquq_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, out_dir)
		hopeSquq_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir)
		benchmark_tools.plot_queue(congestion_alg, out_dir)

	benchmark_tools.plot_allRTTcdf(out_dir, dctcp=dctcp_cdf, timely=timely_cdf, \
									hopeMax=hopeMax_cdf, hopeSum=hopeSum_cdf, \
									hopeMaxq=hopeMaxq_cdf, hopeMaxqd=hopeMaxqd_cdf, \
									hopeMaxe=hopeMaxe_cdf, hopeMaxed=hopeMaxed_cdf, \
									hopeSumq=hopeSumq_cdf, hopeSumqd=hopeSumqd_cdf, \
									hopeSume=hopeSume_cdf, hopeSumed=hopeSumed_cdf, \
									hopeSqu=hopeSqu_cdf, hopeSquq=hopeSquq_cdf)
	benchmark_tools.plot_allTotalThp(out_dir, dctcp=dctcp_thp, timely=timely_thp, \
									hopeMax=hopeMax_thp, hopeSum=hopeSum_thp, \
									hopeMaxq=hopeMaxq_thp, hopeMaxqd=hopeMaxqd_thp, \
									hopeMaxe=hopeMaxe_thp, hopeMaxed=hopeMaxed_thp, \
									hopeSumq=hopeSumq_thp, hopeSumqd=hopeSumqd_thp, \
									hopeSume=hopeSume_thp, hopeSumed=hopeSumed_thp, \
									hopeSqu=hopeSqu_thp, hopeSquq=hopeSquq_thp)
	benchmark_tools.plot_allFCT(out_dir, dctcp=dctcp_fct, timely=timely_fct, \
									hopeMax=hopeMax_fct, hopeSum=hopeSum_fct, \
									hopeMaxq=hopeMaxq_fct, hopeMaxqd=hopeMaxqd_fct, \
									hopeMaxe=hopeMaxe_fct, hopeMaxed=hopeMaxed_fct, \
									hopeSumq=hopeSumq_fct, hopeSumqd=hopeSumqd_fct, \
									hopeSume=hopeSume_fct, hopeSumed=hopeSumed_fct, \
									hopeSqu=hopeSqu_fct, hopeSquq=hopeSquq_fct)

if __name__ == "__main__":
	main()
