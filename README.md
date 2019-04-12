
Benchmarking Between Congestion Control Algorithms
=====================

This benchmark uses the public repository of sibanez12/dctcp-ns2 
(https://github.com/sibanez12/dctcp-ns2) to start by reproducing DCTCP
behavior in the simulations.

The results are designed to be reproduced on a machine running Ubuntu 14.04. 
It is recommended to run the simulations on a Google Compute Engine instance 
to ensure maximum consistency and reproducibility. Below are the instructions
to reproduce:

(Optional) Google Compute Engine Instance Setup
-----------------------------------------------

This method requires that you have a Google Cloud account and associated 
billing account (or free trial) set up.

1. Navigate to your [Google Cloud Console](https://console.cloud.google.com) 
and click "Compute Engine > Images" on the left hand side.

2. Search for the ubuntu-1404 image and select it. Click "CREATE INSTANCE".

3. Choose a name for your instance (e.g. dctcp-ns2). Choose your desired zone 
to host your instance. Choose 4 vCPUs as the machine type. Make sure to check
the box to allow HTTP traffic. Click "Create".

Installation and Reproduction Steps:
------------------------------------

1. Install git and make: 
`$ sudo apt-get -y install git make`

2. Clone the repository:
`$ git clone https://github.com/serhatarslan-hub/congestion_benchmark.git`

3. Install the dependencies (this will take about 8 minutes):
`$ cd congestion_benchmark/dctcp-ns2 && make`

4. Reproduce the results (this will take about 5 minutes):
`$ cd ..`
`$ ./run_timelyReproduction.sh`


Additional Notes
----------------

You can use the benchmark_sim.py script to run individual congestion algorithms,
but you will need to source the settings.sh script first. 

Run, `$ ./dctcp-ns2/run_sim.py --help` for usage information.

