#!/bin/bash

source ./dctcp-ns2/settings.sh
./lib/reproduction_sim.py --timely --dctcp 
#--vegas
echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
sudo python -m SimpleHTTPServer 80




