
# May, 2019
# Author: Serhat Arslan, Stanford University

#  This script simulates a multi-Level topology where
# congestion takes place in multiple hops.

if {$argc != 4} {
    puts "wrong number of arguments, expected 4, got $argc"
    exit 0
}

set congestion_alg [lindex $argv 0]
set out_dir [lindex $argv 1]

set out_rtt_file $out_dir$congestion_alg.rtt.out
set rtt_file [open $out_rtt_file w]

set num_clients [lindex $argv 2]

set num_conn_per_client [lindex $argv 3]
set num_layers 5

#Create a simulator object
set ns [new Simulator]

#Open the Trace files
set tracefile [open $out_dir$congestion_alg.tr w]
$ns trace-all $tracefile

##Open the NAM trace file
#set nf [open $out_dir$congestion_alg.nam w]
#$ns namtrace-all $nf

# samp_int (sec)
set samp_int 0.0001
# q_size (pkts)
set q_size 200
# link_cap (Mbps)
set link_cap(0) 1Gb
set link_cap(1) 5Gb
set link_cap(2) 10Gb
set link_cap(3) 20Gb
set link_cap(4) 40Gb
# link_delay (ms) #Randomized below
set link_delay 50us 
# tcp_window (pkts)
set tcp_window 10000000
# run_time (sec)
set run_time 0.3
# pktSize (bytes)
set pktSize 1460

#### DCTCP Parameters ####
# DCTCP_K (pkts)
set DCTCP_K 80
# DCTCP_g (0 < g < 1)
set DCTCP_g 0.0625
# ackRatio
set ackRatio 1

#### Timely/Hope Parameters ####
set timely_ewma_alpha 0.3
set timely_t_low 0
set timely_t_high 0.015
#set timely_additiveInc 30000000.0
set timely_additiveInc 10000000.0
set timely_decreaseFac 0.8
set timely_HAI_thresh 5
set timely_rate 100000000.0

##### Switch Parameters ####
set drop_prio_ false
set deque_prio_ false

# Queue options
Queue set limit_ $q_size

Queue/DropTail set mean_pktsize_ [expr $pktSize+40]
Queue/DropTail set drop_prio_ $drop_prio_
Queue/DropTail set deque_prio_ $deque_prio_

Queue/RED set mean_pktsize_ $pktSize
Queue/RED set setbit_ true
Queue/RED set gentle_ false
Queue/RED set q_weight_ 1.0
Queue/RED set mark_p_ 1.0
Queue/RED set thresh_ $DCTCP_K
Queue/RED set maxthresh_ $DCTCP_K
Queue/RED set drop_prio_ $drop_prio_
Queue/RED set deque_prio_ $deque_prio_

if {[string compare $congestion_alg "dctcp"] == 0} { 
    set queue_type RED
} else {
    set queue_type DropTail
}

#### Generate the random topology ####
set rng_topo [new RNG]
$rng_topo seed 0

set RV_switches [new RandomVariable/Uniform]
#$RV_switches set min_ 0.02
#$RV_switches set max_ 0.06
$RV_switches set min_ 0.20
$RV_switches set max_ 0.40
$RV_switches use-rng $rng_topo

set num_nodes(0) $num_clients
for {set i 1} {$i < $num_layers} {incr i} {
    set prev_layer $num_nodes([expr $i-1])
    #set num_nodes($i) [expr int([$RV_switches value]*exp($i-0.2)*$prev_layer)+1]
    set num_nodes($i) [expr int([$RV_switches value]*$prev_layer)+1]
    puts "-There will be $num_nodes($i) nodes on level $i"
}

# Create all nodes
for {set i 0} {$i < $num_layers} {incr i} {
    for {set j 0} {$j < $num_nodes($i)} {incr j} {
	set nodes($i,$j) [$ns node]
    }
}

# Create links between the nodeswith random delay
set RV_delays [new RandomVariable/Uniform]
$RV_delays set min_ 5
$RV_delays set max_ 500
$RV_delays use-rng $rng_topo
set dly_unit us
set RV_caps [new RandomVariable/Uniform]
$RV_caps set min_ 0
$RV_caps set max_ 0.999999
$RV_caps use-rng $rng_topo

for {set i 0} {$i < [expr $num_layers-1]} {incr i} {
    set RV_links [new RandomVariable/Uniform]
    $RV_links set min_ 0
    $RV_links set max_ [expr $num_nodes([expr $i+1])-0.000001]
    $RV_links use-rng $rng_topo

    for {set j 0} {$j < $num_nodes($i)} {incr j} {
		set link_to [expr int([$RV_links value])]
		set delay [expr int([$RV_delays value])]
		set link_delay $delay$dly_unit
		set link_capacity [expr int($num_layers*[$RV_caps value])]
		set link_capacity $link_cap($link_capacity)
		$ns duplex-link $nodes($i,$j) $nodes([expr $i+1],$link_to) $link_capacity $link_delay $queue_type
    }
}
# Last layer shall be fully connected to each other
set last_level [expr $num_layers-1]
for {set i 0} {$i < $num_nodes($last_level)} {incr i} {
    for {set j [expr $i+1]} {$j < $num_nodes($last_level)} {incr j} {
    	set delay [expr int([$RV_delays value])]
		set link_delay $delay$dly_unit
		set link_capacity [expr int($num_layers*[$RV_caps value])]
		set link_capacity $link_cap($link_capacity)
		$ns duplex-link $nodes($last_level,$i) $nodes($last_level,$j) $link_capacity $link_delay $queue_type
    }
}

# Create random generator for TCP connections
set rng_conn [new RNG]
$rng_conn seed 0

# Parameters for random variables to connection choice
set RV_host [new RandomVariable/Uniform]
$RV_host set min_ 0
$RV_host set max_ [expr $num_clients-0.000001]
$RV_host use-rng $rng_conn

# HOST options
Agent/TCP set window_ $tcp_window
Agent/TCP set windowInit_ 2
Agent/TCP set packetSize_ $pktSize
Agent/TCP/FullTcp set segsize_ $pktSize

# DCTCP settings
if {[string compare $congestion_alg "dctcp"] == 0} {
    Agent/TCP set ecn_ 1
    Agent/TCP set old_ecn_ 1
    Agent/TCP/FullTcp set spa_thresh_ 0
    Agent/TCP set slow_start_restart_ true
    Agent/TCP set windowOption_ 0
    Agent/TCP set tcpTick_ 0.000001
    #Agent/TCP set minrto_ $min_rto
    #Agent/TCP set maxrto_ 2

    Agent/TCP/FullTcp set nodelay_ true; # disable Nagle
    Agent/TCP/FullTcp set segsperack_ $ackRatio;
    Agent/TCP/FullTcp set interval_ 0.000006

    Agent/TCP set ecnhat_ true
    Agent/TCPSink set ecnhat_ true
    Agent/TCP set ecnhat_g_ $DCTCP_g;

    for {set i 0} {$i < $num_clients} {incr i} {
        for {set j 0} {$j < $num_conn_per_client} {incr j} {
            set conn_idx [expr $i*$num_conn_per_client+$j] 
            set dst($conn_idx) [expr (int([$RV_host value]))] 

            if {$i == $dst($conn_idx)} {
        	if {$i == 0} {
            	    set dst($conn_idx) [expr $dst($conn_idx)+1]
        	} else {
            	    set dst($conn_idx) [expr $dst($conn_idx)-1]
        	}
            }    
    
            set tcp($conn_idx) [new Agent/TCP/FullTcp]
            set sink($conn_idx) [new Agent/TCP/FullTcp]
            $ns attach-agent $nodes(0,$i) $tcp($conn_idx)
            $ns attach-agent $nodes(0,$dst($conn_idx)) $sink($conn_idx)
            $tcp($conn_idx) set fid_ [expr $conn_idx]
            $sink($conn_idx) set fid_ [expr $conn_idx]
            $ns connect $tcp($conn_idx) $sink($conn_idx)
            # set up TCP-level connections
            $sink($conn_idx) listen
        }
    }
    for {set i 0} {$i < $num_clients} {incr i} {
        for {set j 0} {$j < $num_conn_per_client} {incr j} {
            set conn_idx [expr $i*$num_conn_per_client+$j]

            # set up FTP connections
            set ftp($conn_idx) [$tcp($conn_idx) attach-source FTP]
            $ftp($conn_idx) set type_ FTP 
        }
    }
    # The following procedure is called whenever a packet is received 
    Agent/TCP/FullTcp instproc recv {rtt_t} {
    	global ns rtt_file       
     	$self instvar fid_
        
        set now [$ns now]
        set rtt [$self set rtt_]
        puts $rtt_file "$now $fid_ $rtt"
    }

} else {
    for {set i 0} {$i < $num_clients} {incr i} {
        for {set j 0} {$j < $num_conn_per_client} {incr j} {
            set conn_idx [expr $i*$num_conn_per_client+$j]
            set dst($conn_idx) [expr (int([$RV_host value]))]  

            if {$i == $dst($conn_idx)} {
         	if {$i == 0} {
            	    set dst($conn_idx) [expr $dst($conn_idx)+1]
        	} else {
            	    set dst($conn_idx) [expr $dst($conn_idx)-1]
        	}
            }      
    
            set tcp($conn_idx) [new Agent/TCP/Vegas]
            set sink($conn_idx) [new Agent/TCPSink]
            $ns attach-agent $nodes(0,$i) $tcp($conn_idx)
            $ns attach-agent $nodes(0,$dst($conn_idx)) $sink($conn_idx)
            $tcp($conn_idx) set fid_ [expr $conn_idx]
            $sink($conn_idx) set fid_ [expr $conn_idx]
            $ns connect $tcp($conn_idx) $sink($conn_idx)

            $tcp($conn_idx) set timely_packetSize_ [expr $pktSize+40]
            $tcp($conn_idx) set timely_ewma_alpha_ $timely_ewma_alpha
            $tcp($conn_idx) set timely_t_low_ $timely_t_low
            $tcp($conn_idx) set timely_t_high_ $timely_t_high
            $tcp($conn_idx) set timely_additiveInc_ $timely_additiveInc
            $tcp($conn_idx) set timely_decreaseFac_ $timely_decreaseFac
            $tcp($conn_idx) set timely_HAI_thresh_ $timely_HAI_thresh
            $tcp($conn_idx) set timely_rate_ $timely_rate
            $tcp($conn_idx) set rttNoise_ 0
        }
    }

    if {[string compare $congestion_alg "vegas"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set timely_ 0
                $tcp($conn_idx) set hope_type_ 0
            }
        }
    } elseif {[string compare $congestion_alg "timely"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set timely_ 1
                $tcp($conn_idx) set hope_type_ 0
            }
        }
    } elseif {[string compare $congestion_alg "hope_sum"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 2
                $tcp($conn_idx) set hope_collector_ 0
            }
        }
    } elseif {[string compare $congestion_alg "hope_max"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 1
                $tcp($conn_idx) set hope_collector_ 0
            }
        }
    } elseif {[string compare $congestion_alg "hope_maxq"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 1
                $tcp($conn_idx) set hope_collector_ 1
            }
        }
    } elseif {[string compare $congestion_alg "hope_maxqd"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 1
                $tcp($conn_idx) set hope_collector_ 2
            }
        }
    } elseif {[string compare $congestion_alg "hope_maxe"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 1
                $tcp($conn_idx) set hope_collector_ 3
                $tcp($conn_idx) set timely_t_low_ -10
            }
        }
    } elseif {[string compare $congestion_alg "hope_maxed"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 1
                $tcp($conn_idx) set hope_collector_ 4
                $tcp($conn_idx) set timely_t_low_ -10
            }
        }
    } elseif {[string compare $congestion_alg "hope_sumq"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 2
                $tcp($conn_idx) set hope_collector_ 1
            }
        }
    } elseif {[string compare $congestion_alg "hope_sumqd"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 2
                $tcp($conn_idx) set hope_collector_ 2
            }
        }
    } elseif {[string compare $congestion_alg "hope_sume"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 2
                $tcp($conn_idx) set hope_collector_ 3
                $tcp($conn_idx) set timely_t_low_ -10
            }
        }
    } elseif {[string compare $congestion_alg "hope_sumed"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 2
                $tcp($conn_idx) set hope_collector_ 4
                $tcp($conn_idx) set timely_t_low_ -10
            }
        }
    } elseif {[string compare $congestion_alg "hope_squ"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 3
                $tcp($conn_idx) set hope_collector_ 0
            }
        }
    } elseif {[string compare $congestion_alg "hope_squq"] == 0} {    
        for {set i 0} {$i < $num_clients} {incr i} {
            for {set j 0} {$j < $num_conn_per_client} {incr j} {
                set conn_idx [expr $i*$num_conn_per_client+$j]        

                $tcp($conn_idx) set hope_type_ 3
                $tcp($conn_idx) set hope_collector_ 1
            }
        }
    }

    for {set i 0} {$i < $num_clients} {incr i} {
        for {set j 0} {$j < $num_conn_per_client} {incr j} {
            set conn_idx [expr $i*$num_conn_per_client+$j]

            # set up FTP connections
            set ftp($conn_idx) [$tcp($conn_idx) attach-source FTP]
            $ftp($conn_idx) set type_ FTP 

        }
    }
    Agent/TCP/Vegas instproc recv {rtt_t cong_signal_t nonbn_q_t timely_rate_t} {
        global ns rtt_file
        $self instvar fid_

        set now [$ns now]
        set rtt [expr $rtt_t * 1000000.0]
        puts $rtt_file "$now $fid_ $rtt"
    }
}

# Create random generator for starting the ftp connections
set rng_time [new RNG]
$rng_time seed 0

# Parameters for random variables to ftp start times
set RV_beg_fin [new RandomVariable/Uniform]
$RV_beg_fin set min_ 0.0001
$RV_beg_fin set max_ [expr $run_time/5]
$RV_beg_fin use-rng $rng_time

#Schedule events for the FTP agents
for {set i 0} {$i < $num_clients} {incr i} {
    for {set j 0} {$j < $num_conn_per_client} {incr j} {
        set conn_idx [expr $i*$num_conn_per_client+$j]        
    
        set startT($conn_idx) [expr [$RV_beg_fin value]]
        $ns at $startT($conn_idx) "$ftp($conn_idx) start"
        #$ns at 0.0001 "$ftp($conn_idx) start"
        set finT($conn_idx) [expr [$RV_beg_fin value]]
        $ns at [expr $run_time - $finT($conn_idx)] "$ftp($conn_idx) stop"
        #$ns at [expr $run_time - 0.001] "$ftp($conn_idx) stop"
    }
}

#Call the finish procedure after run_time seconds of simulation time
$ns at $run_time "finish"

#Define a 'finish' procedure
proc finish {} {
    global congestion_alg ns tracefile rtt_file out_dir
    $ns flush-trace
    # Close the NAM trace file
#    close $nf
    close $tracefile
    close $rtt_file 
    # Execute NAM on the trace file
#    exec nam $out_dir$congestion_alg.nam &
    exit 0
}

#Run the simulation
$ns run
