#!/bin/bash

source ./dctcp-ns2/settings.sh
./lib/topology4_sim.py --dctcp --timely --hope_max --hope_squ
#./lib/topology4_sim.py --timely --hope_max 

echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
#sudo python -m SimpleHTTPServer 80

