#!/bin/bash

source ./dctcp-ns2/settings.sh
mkdir ./out_topology2

./lib/topology2/simulation.py --dctcp --timely --hope_sum --hope_max --hope_maxq --hope_maxqd --hope_maxe --hope_maxed --hope_sumq --hope_sumqd --hope_sume --hope_sumed

echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
sudo python -m SimpleHTTPServer 80

