#!/bin/bash

source ./dctcp-ns2/settings.sh
mkdir ./out_skinnyTopology

./lib/skinnyTopology/simulation.py --timely --hope_max --hope_squ --timely

echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
sudo python -m SimpleHTTPServer 80

