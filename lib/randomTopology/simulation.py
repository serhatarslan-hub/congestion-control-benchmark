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
import datetime, time

sys.path.append(os.path.expandvars('$DCTCP_NS2/bin/'))
import benchmark_tools

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dctcp', action='store_true', help="Simulates DCTCP in a random topology")
    parser.add_argument('--timely', action='store_true', help="Simulates Timely in a random topology")
    parser.add_argument('--hope_sum', action='store_true', help="Simulates Hope-Sum in a random topology")
    parser.add_argument('--hope_max', action='store_true', help="Simulates Hope-Max in a random topology")
    parser.add_argument('--hope_maxq', action='store_true', help="Simulates Hope-Maxq in a random topology")
    parser.add_argument('--hope_maxqd', action='store_true', help="Simulates Hope-Maxqd in a random topology")
    parser.add_argument('--hope_maxe', action='store_true', help="Simulates Hope-Maxe in a random topology")
    parser.add_argument('--hope_maxed', action='store_true', help="Simulates Hope-Maxed in a random topology")
    parser.add_argument('--hope_sumq', action='store_true', help="Simulates Hope-Sumq in a random topology")
    parser.add_argument('--hope_sumqd', action='store_true', help="Simulates Hope-Sumqd in a random topology")
    parser.add_argument('--hope_sume', action='store_true', help="Simulates Hope-Sume in a random topology")
    parser.add_argument('--hope_sumed', action='store_true', help="Simulates Hope-Sumed in a random topology")
    parser.add_argument('--hope_squ', action='store_true', help="Simulates Hope-Squ in a random topology")
    parser.add_argument('--hope_squq', action='store_true', help="Simulates Hope-Squq in a random topology")
    args = parser.parse_args()
    
    num_clients = 200
    connPerClient = 1
    setup_dir = './lib/randomTopology/setup.tcl'
    
    now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    print("Current Time: %s"%str(now))

    out_dir = './out_randomTopology/%s/'%now
    while True:
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
		break
	else:
	    time.sleep(1)
	    now = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
	    out_dir = './out_randomTopology/%s/'%now

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
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		dctcp_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		dctcp_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		dctcp_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, dctcp_cdf, dctcp_thp, dctcp_fct)
    if (args.timely):
		congestion_alg = 'timely'
		print("Timely Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		timely_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		timely_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		timely_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, timely_cdf, timely_thp, timely_fct)
    if (args.hope_sum):
		congestion_alg = 'hope_sum'
		print("Hope-Sum Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeSum_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeSum_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeSum_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeSum_cdf, hopeSum_thp, hopeSum_fct)
    if (args.hope_max):
		congestion_alg = 'hope_max'
		print("Hope-Max Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeMax_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeMax_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeMax_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeMax_cdf, hopeMax_thp, hopeMax_fct)
    if (args.hope_maxq):
		congestion_alg = 'hope_maxq'
		print("Hope-Maxq Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeMaxq_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeMaxq_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeMaxq_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeMaxq_cdf, hopeMaxq_thp, hopeMaxq_fct)
    if (args.hope_maxqd):
		congestion_alg = 'hope_maxqd'
		print("Hope-Maxqd Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeMaxqd_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeMaxqd_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeMaxqd_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeMaxqd_cdf, hopeMaxqd_thp, hopeMaxqd_fct)
    if (args.hope_maxe):
		congestion_alg = 'hope_maxe'
		print("Hope-Maxe Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeMaxe_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeMaxe_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeMaxe_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeMaxe_cdf, hopeMaxe_thp, hopeMaxe_fct)
    if (args.hope_maxed):
		congestion_alg = 'hope_maxed'
		print("Hope-Maxed Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeMaxed_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeMaxed_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeMaxed_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeMaxed_cdf, hopeMaxed_thp, hopeMaxed_fct)
    if (args.hope_sumq):
		congestion_alg = 'hope_sumq'
		print("Hope-Sumq Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeSumq_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeSumq_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeSumq_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeSumq_cdf, hopeSumq_thp, hopeSumq_fct)
    if (args.hope_sumqd):
		congestion_alg = 'hope_sumqd'
		print("Hope-Sumqd Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeSumqd_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeSumqd_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeSumqd_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeSumqd_cdf, hopeSumqd_thp, hopeSumqd_fct)
    if (args.hope_sume):
		congestion_alg = 'hope_sume'
		print("Hope-Sume Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeSume_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeSume_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeSume_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeSume_cdf, hopeSume_thp, hopeSume_fct)
    if (args.hope_sumed):
		congestion_alg = 'hope_sumed'
		print("Hope-Sumed Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeSumed_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeSumed_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeSumed_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeSumed_cdf, hopeSumed_thp, hopeSumed_fct)
    if (args.hope_squ):
		congestion_alg = 'hope_squ'
		print("Hope-Squ Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeSqu_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeSqu_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeSqu_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeSqu_cdf, hopeSqu_thp, hopeSqu_fct)
    if (args.hope_squq):
		congestion_alg = 'hope_squq'
		print("Hope-Squq Simulation Running...")
		os.system('ns {0} {1} {2} {3} {4}'.format(setup_dir, congestion_alg, out_dir, num_clients, connPerClient))
		hopeSquq_cdf = benchmark_tools.plot_rtt(congestion_alg, out_dir, nplot=10, report_only=True)
		hopeSquq_thp = benchmark_tools.plot_throughput(congestion_alg, num_clients, \
													out_dir, connPerClient, report_only=True)
		hopeSquq_fct = benchmark_tools.get_fct(congestion_alg, num_clients, out_dir, connPerClient)
		benchmark_tools.gen_report(congestion_alg, out_dir, hopeSquq_cdf, hopeSquq_thp, hopeSquq_fct)

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
    
    output_files = os.listdir(out_dir)
    for item in output_files:
        if item.endswith(".tr") or item.endswith(".out"):
            os.remove(os.path.join(out_dir, item))

if __name__ == "__main__":
    main()
