#!/bin/bash

source ./dctcp-ns2/settings.sh
./lib/hope_vs_bits_sim.py

echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
#sudo python -m SimpleHTTPServer 80

