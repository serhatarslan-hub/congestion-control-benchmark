#!/bin/bash

source ./dctcp-ns2/settings.sh
./lib/topology3_sim.py --dctcp --timely --hope_sum --hope_max --hope_maxq --hope_maxqd --hope_maxe --hope_maxed --hope_sumq --hope_sumqd --hope_sume --hope_sumed
#./lib/topology3_sim.py --dctcp --timely

echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
#sudo python -m SimpleHTTPServer 80

