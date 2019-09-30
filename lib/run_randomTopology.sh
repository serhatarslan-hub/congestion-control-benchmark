#!/bin/bash

source ./dctcp-ns2/settings.sh
mkdir ./out_randomTopology

for i in $(seq 1 $1)
do
	echo "____Simulation $i / $1"
	./lib/randomTopology/simulation.py --timely --hope_max --hope_squ
done

echo "Simulations Completed! For aggregate results, run ./lib/consolidate_results.py"
echo "Please navigate to ./out_randomTopology directory to investigate results"

