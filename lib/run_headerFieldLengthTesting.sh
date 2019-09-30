#!/bin/bash

source ./dctcp-ns2/settings.sh
mkdir ./out_headerFieldLengthTesting

./lib/headerFieldLengthTesting/simulation.py

echo "Simulations completed! "
echo "Please navigate to ./out_headerFieldLengthTesting directory to investigate report files"

echo "Each report is single line with the following format:
        'mean_rtt 95%ile_rtt 99%ile_rtt std_rtt ...
        ... mean_tot_thp median_tot_thp std_tot_thp ...
        ... mean_sfct 95%ile_sfct 99%ile_sfct std_sfct...
        ... mean_mfct 95%ile_mfct 99%ile_mfct std_mfct...
        ... mean_lfct 95%ile_lfct 99%ile_lfct std_lfct'"

