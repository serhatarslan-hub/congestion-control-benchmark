#!/bin/bash

source ./dctcp-ns2/settings.sh
./lib/complexCongestion_sim.py --hope_max --hope_sum --timely

echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
sudo python -m SimpleHTTPServer 80
