
Benchmarking With Congestion Control Algorithms
=====================

This benchmark uses the public repository 
[sibanez12/dctcp-ns2](https://github.com/sibanez12/dctcp-ns2) to start 
by reproducing DCTCP behavior in the simulations. It also offers 
[Timely Congestion Control](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p537.pdf) 
implementation.

In addition, queue occupancy stamping feature (HOPE framework) is added to 
IP packet switches to experiment with the effectiveness of queue occupancy 
knowledge (the exact measure of congestion in the network) on congestion control. 
Sumary of our work and findings are presented in our report, [Moving Beyond Proxy
Signals for Datacenter Congestion Control](https://web.stanford.edu/~sarslan/files/MovingBeyondProxySignalsforDatacenterCongestionControl.pdf).

The repository is especially organized for easy reproduction. 
The simulations are designed to be reproduced on a machine running Ubuntu 14.04. 
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

4. Reproduce the Timely results (this will take about 5 minutes):
`$ cd ..`
`$ ./lib/run_timelyReproduction.sh`

5. Navigate to `http://localhost` on a browser and click on 
**Timely Reproduction Results (Dumbbell Topology)** to see output figures.

Additional Notes
----------------

You can simulate different scenarios that are already presented in the repository to 
experiment on different topologies and different congestion control configurations 
by running `$ ./lib/run_[scenario_name].sh`. The details about those scenarios are 
provided below:

| **Scenario** | **Details** | **Topology** |
|---|---|---|
| *timelyReproduction* | Reproduces small scale experiments presented in Timely paper. | Dumbell Topology with 10 clents, and a server |
| *topology2* | Runs DCTCP, Timely and Hope Framework on a 2 level dumbbell topology. | see `./lib/topology2/20Hosts2Leafs1Server.png` |
| *topology3* | Runs DCTCP, Timely and Hope Framework on a small scale data-center topology. | see `./lib./topology3/32Hosts4Leafs4Servers.png` |
| *topology4* | Runs DCTCP, Timely and Hope Framework on a 3-level CLOS topology as a better simulation for a datacenter environment. | see `./lib/topology4/192HostsCLOS.png` |
| *skinnyTopology* | Simulates a 6 hop path with many cross flows. Used to show how delay can can be misleading in the presence of non-bottleneck queues. | see `./lib/skinnyTopology/skinnyTopology.png` |
| *randomTopology* | Simulates 3-level CLOS topologies with random number of clients and switches. Used to investigate the effect of topology on congestion control algorithms. | random |
| *headerFieldLengthTesting* | Simulates queue occupancy stamping with different header lengths on the packet. Used to show that 4 to 8 bits is more than enough to carry useful information on queues. | same as *topology4* |

Understanding How Our Simulations Work
--------------------------------------

Due to the capabilities of NS-2, the simulations are designed on layers of scpripts. 
It is enough to run only the shell script. The other layers are called automatically
in a nested fashion. The layers can be described as follows:

1. `./lib/run_[scenario_name].sh`
    - Sets the required environment variables.
    - Allows user to determine which congestion control algorithms to use.
    - Runs the corresponding python script.
    - Starts a web server for easy investigation on results.
2. `./lib/[scenario_name]/simulation.py`
    - Runs the simulation script with correct arguments.
    - Consolidates outputs.
    - Generates figures of the simulation results.
3. `./lib/[scenario_name]/setup.tcl`
    - The actual simulation script.
    - Tells NS about the topology, timeline, and applications in the simulation.
    - Generates outputs.
    
The main modified ns files for this repository include the list below. Please feel free to 
have a look and change the code as you'd like. However, remember to redo the step 3 of
*Installation and Reproduction Steps* section.  

`$ cd ./dctcp-ns2/ns-2/ns-allinone-2.34/ns-2.34/`
+ `/common/agent.cc`, `/common/agent.h`
+ `/common/ip.cc`, `/common/ip.h`
+ `/queue/drop_tail.cc`
+ `/queue/queue.h`
+ `/tcp/tcp-sink.cc`
+ `/tcp/tcp-vegas.cc`
+ `/tcp/tcp.h`
+ `/tcl/lib/ns-default.tcl`

What is HOPE?
-------------

HOPE (Hop-by-hop Obstructions Provided to End-hosts) is a framework where each switch 
stamps the queue occupancy information onto every packet. When the server gets the packet,
the queue occupancy information is piggybacked to the client via the acknowledgement packet.

The client collects this information and processes to decide how to change the tranmission 
rate. In our implementation, we used Timely's gradient based approach for desicion process,
but we do not claim that it is the best use of the queue occupancy information.

Before the queue occupancy information is given to the control algoritm, it needs to be 
preprocessed, so that all information boils down to a single measure. For this purpose,
we use several variants to apply on the queue occupancy vector. Those variants are 
summarized with the following formulation:

`hope_[function][data]`, i.e. hope_maxq

+ Function:
    - *Sum* : Sums all the queue occupancies along the path. Equivalent to RTT.
    - *Max* : Takes the hisghest level occupancy, i.e. bottleneck, only into consideration
    - *Squ* : Takes square of each queue occupancy, sum them up, and calculate the square root. Gives more emphasis on longer queues but does't ignore others.
+ Data:
    - default : Time between arrival and departure of the packet
    - *-q* : queue occupancy at arrival (in packets)
    - *-qd* : queue occupancy at departure (in packets)
    - *-e* : empty buffer size at arrival (in packets)
    - *-ed* : empty buffer size at departure (in packets)
