#!/usr/bin/env python

"""
Controls the NS-2 simulation runs
"""

import os, sys, re, json
import numpy as np
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

"""
Author: Serhat Arslan
Date: May 2019

This script uses the consolidate function defined below
to get results of many simulations into an aggregate report.

Run this script from the main folder of the repository. You
may change the path to output folder which contains the folders 
for each simulation result, from the main() function below. 
"""

def consolidate(report_dir, algorithms):
	"""
	Reads all the simulation reports inside the report_dir 
	folder and generates a single report that summarizes all
	
	It assumes that the simulation reports are under their 
	unique folder inside report_dir.
	It also assumes that reports to be consolidated are for 
	the algorithms whose names are given in the algorithms list.
	"""
	output_file = report_dir+'consolidatedReport.json'
	
	print("\n__Starting consolidation...")
	
	allData = {}
	final_report = {}
	
	extension = '.report'
	for i in range(len(algorithms)):
		algorithms[i] = algorithms[i]+extension
		allData[algorithms[i]] = defaultdict(lambda: ([]))
		final_report[algorithms[i]] = {}
	
	root, _, _ = os.walk(report_dir)
	n_folders = len(root[1])
	cnt = 0.0
	
	print("%d simulation folders are found.\n"%n_folders)
	
	for folder in root[1]:
		print("*** {}%\t getting results from {}...".format(cnt/n_folders*100,folder))
		cnt += 1
		
		output_files = os.listdir(os.path.join(report_dir,folder))
		for item in output_files:
			if item in algorithms:
				file_name = os.path.join(report_dir,folder,item)
				with open(file_name, "r") as f:
					for line in f:
						mean_rtt, perc95_rtt, perc99_rtt, std_rtt, \
							mean_thp, median_thp, std_thp, \
							mean_sfct, perc95_sfct, perc99_sfct, std_sfct, \
							mean_mfct, perc95_mfct, perc99_mfct, std_mfct, \
							mean_lfct, perc95_lfct, perc99_lfct, std_lfct = line.split()
						
						allData[item]['rtt_mean'].append(float(mean_rtt))
						allData[item]['rtt_perc95'].append(float(perc95_rtt))
						allData[item]['rtt_perc99'].append(float(perc99_rtt))
						allData[item]['rtt_std'].append(float(std_rtt))
						
						allData[item]['thp_mean'].append(float(mean_thp))
						allData[item]['thp_median'].append(float(median_thp))
						allData[item]['thp_std'].append(float(std_thp))
						
						allData[item]['sfct_mean'].append(float(mean_sfct))
						allData[item]['sfct_perc95'].append(float(perc95_sfct))
						allData[item]['sfct_perc99'].append(float(perc99_sfct))
						allData[item]['sfct_std'].append(float(std_sfct))
						
						allData[item]['mfct_mean'].append(float(mean_mfct))
						allData[item]['mfct_perc95'].append(float(perc95_mfct))
						allData[item]['mfct_perc99'].append(float(perc99_mfct))
						allData[item]['mfct_std'].append(float(std_mfct))
						
						allData[item]['lfct_mean'].append(float(mean_lfct))
						allData[item]['lfct_perc95'].append(float(perc95_lfct))
						allData[item]['lfct_perc99'].append(float(perc99_lfct))
						allData[item]['lfct_std'].append(float(std_lfct))
					
	for algorithm in allData.keys():
		for measurement in allData[algorithm].keys():
			allData[algorithm][measurement] = np.array(allData[algorithm][measurement])
			final_report[algorithm][measurement] = np.mean(allData[algorithm][measurement])
	
	print("\n__Consolidation completed...")	
	#print(json.dumps(final_report, indent = 4))
	
	with open(output_file, 'w') as fp:
		json.dump(final_report, fp, sort_keys=True, indent=4)
	print("Consolidated report is saved as %s"%output_file)

def main():
	
	report_dir = './out_randomTopology/'
	algorithms = ['timely','hope_max']
	
	consolidate(report_dir, algorithms)

if __name__ == "__main__":
    main()
