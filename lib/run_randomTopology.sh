#!/bin/bash

source ./dctcp-ns2/settings.sh
for i in $(seq 1 $1)
do
	echo "____Simulation $i / $1"
	./lib/randomTopology_sim.py --timely --hope_max 
	#--hope_squ
done

#echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
#sudo python -m SimpleHTTPServer 80

