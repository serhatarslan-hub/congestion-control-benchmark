
# May, 2019
# Author: Serhat Arslan, Stanford University

#  This script simulates a multi-Level topology where
# congestion takes place in multiple hops.

if {$argc != 2} {
    puts "wrong number of arguments, expected 2, got $argc"
    exit 0
}

set congestion_alg [lindex $argv 0]
set out_dir [lindex $argv 1]

set out_rtt_file $out_dir$congestion_alg.rtt.out
set rttFile [open $out_rtt_file w]
set out_q_file $out_dir$congestion_alg.queue.out

# Number of connections at the crowded node
set n_conn 3

# samp_int (sec)
set samp_int 0.0001
# q_size (pkts)
set q_size 200
set short_q_size 100
# link_cap (Mbps)
set link_cap 10Gb
# link_delay (ms)
set link_delay 5us
# tcp_window (pkts)
set tcp_window 10000000
# run_time (sec)
set run_time 0.5
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
set timely_t_high 0.0005
set timely_additiveInc 30000000.0
set timely_decreaseFac 0.7
set timely_HAI_thresh 5
set timely_rate 300000000.0

##### Switch Parameters ####
set drop_prio_ false
set deque_prio_ false

#Create a simulator object
set ns [new Simulator]
$ns color 1 Red
$ns color 2 Blue
$ns color 3 Green

#Open the Trace files
set tracefile [open $out_dir$congestion_alg.tr w]
$ns trace-all $tracefile

#Open the NAM trace file
set nf [open $out_dir$congestion_alg.nam w]
$ns namtrace-all $nf

# Create TOR_switch, server, and client nodes
set my_src [$ns node]
$ns at 0.0 "$my_src label \"Source\""

for {set i 0} {$i < 3} {incr i} {
    set switch($i) [$ns node]
}

set my_dst [$ns node]
$ns at 0.0 "$my_dst label \"Destination\""

for {set i 0} {$i < 4} {incr i} {
    set others($i) [$ns node]
}

# Queue options
Queue set limit_ $q_size

Queue/DropTail set mean_pktsize_ [expr $pktSize+40]
Queue/DropTail set drop_prio_ $drop_prio_
Queue/DropTail set deque_prio_ $deque_prio_

#Queue/RED set bytes_ false
#Queue/RED set queue_in_bytes_ true
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

# Create links between the nodes
$ns duplex-link $my_src $switch(0) $link_cap $link_delay $queue_type
$ns duplex-link $switch(0) $switch(1) $link_cap $link_delay $queue_type
$ns duplex-link $switch(1) $switch(2) $link_cap $link_delay $queue_type
$ns duplex-link $switch(2) $my_dst $link_cap $link_delay $queue_type

$ns duplex-link $switch(0) $others(0) $link_cap $link_delay $queue_type
$ns duplex-link $switch(1) $others(1) $link_cap $link_delay $queue_type
$ns duplex-link $switch(1) $others(2) $link_cap $link_delay $queue_type
$ns duplex-link $switch(2) $others(3) $link_cap $link_delay $queue_type

#Monitor the queue for link. (for NAM)
$ns duplex-link-op $switch(0) $switch(1) queuePos 0.5
$ns duplex-link-op $switch(1) $switch(2) queuePos 0.5
$ns duplex-link-op $switch(2) $my_dst queuePos 0.5

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

    set my_tcp [new Agent/TCP/FullTcp]
    set my_sink [new Agent/TCP/FullTcp]
    $ns attach-agent $my_src $my_tcp
    $ns attach-agent $my_dst $my_sink
    $ns connect $my_tcp $my_sink
    $my_tcp set fid_ 1
    $my_sink listen
    
    # set up FTP connections
    set my_ftp [$my_tcp attach-source FTP]
    $my_ftp set type_ FTP
    
    # The following procedure is called whenever a packet is received 
    Agent/TCP/FullTcp instproc recv {rtt_t} {
	global ns rttFile       
	
	$self instvar node_
	if {[$node_ id] == 0 } {
	    set now [$ns now]
	    set rtt [$self set rtt_]
	
	    puts $rttFile "$now $rtt"
	}
    }

} else {
    set my_tcp [new Agent/TCP/Vegas]
    set my_sink [new Agent/TCPSink]
    $ns attach-agent $my_src $my_tcp
    $ns attach-agent $my_dst $my_sink
    $ns connect $my_tcp $my_sink
    $my_tcp set fid_ 1

    $my_tcp set timely_packetSize_ [expr $pktSize+40]
    $my_tcp set timely_ewma_alpha_ $timely_ewma_alpha
    $my_tcp set timely_t_low_ $timely_t_low
    $my_tcp set timely_t_high_ $timely_t_high
    $my_tcp set timely_additiveInc_ $timely_additiveInc
    $my_tcp set timely_decreaseFac_ $timely_decreaseFac
    $my_tcp set timely_HAI_thresh_ $timely_HAI_thresh
    $my_tcp set timely_rate_ $timely_rate

    if {[string compare $congestion_alg "vegas"] == 0} {    
        $my_tcp set timely_ 0
	$my_tcp set hope_type_ 0
    } elseif {[string compare $congestion_alg "timely"] == 0} { 
	$my_tcp set timely_ 1
	$my_tcp set hope_type_ 0   
    } elseif {[string compare $congestion_alg "hope_sum"] == 0} {
	$my_tcp set hope_type_ 2 
	$my_tcp set hope_collector_ 0    
    } elseif {[string compare $congestion_alg "hope_max"] == 0} {    
	$my_tcp set hope_type_ 1 
	$my_tcp set hope_collector_ 0 
    } elseif {[string compare $congestion_alg "hope_maxq"] == 0} {    
	$my_tcp set hope_type_ 1 
	$my_tcp set hope_collector_ 1 
    } elseif {[string compare $congestion_alg "hope_maxqd"] == 0} {    
	$my_tcp set hope_type_ 1 
	$my_tcp set hope_collector_ 2 
    } elseif {[string compare $congestion_alg "hope_maxe"] == 0} { 
	$my_tcp set hope_type_ 1 
	$my_tcp set hope_collector_ 3  
	$my_tcp set timely_t_low_ -10  
    } elseif {[string compare $congestion_alg "hope_maxed"] == 0} { 
	$my_tcp set hope_type_ 1 
	$my_tcp set hope_collector_ 4  
	$my_tcp set timely_t_low_ -10   
    } elseif {[string compare $congestion_alg "hope_sumq"] == 0} { 
	$my_tcp set hope_type_ 2 
	$my_tcp set hope_collector_ 1    
    } elseif {[string compare $congestion_alg "hope_sumqd"] == 0} {
	$my_tcp set hope_type_ 2 
	$my_tcp set hope_collector_ 2     
    } elseif {[string compare $congestion_alg "hope_sume"] == 0} {
	$my_tcp set hope_type_ 2 
	$my_tcp set hope_collector_ 3  
	$my_tcp set timely_t_low_ -10    
    } elseif {[string compare $congestion_alg "hope_sumed"] == 0} {
	$my_tcp set hope_type_ 2 
	$my_tcp set hope_collector_ 4  
	$my_tcp set timely_t_low_ -10    
    } elseif {[string compare $congestion_alg "hope_squ"] == 0} { 
	$my_tcp set hope_type_ 3 
	$my_tcp set hope_collector_ 0   
    } elseif {[string compare $congestion_alg "hope_squq"] == 0} {
	$my_tcp set hope_type_ 3 
	$my_tcp set hope_collector_ 1    
    }

    # set up FTP connections
    set my_ftp [$my_tcp attach-source FTP]
    $my_ftp set type_ FTP
    
    Agent/TCP/Vegas instproc recv {rtt_t cong_signal_t hop_cnt_t} {
	global ns rttFile       
	
	$self instvar node_
	if {[$node_ id] == 0 } {
	    set now [$ns now]
	    set rtt [expr $rtt_t*1000000.0]
	
	    puts $rttFile "$now $rtt"
	}
    }
}

# Connect "others"
set other_tcp(0) [new Agent/TCP/Vegas]
$ns attach-agent $others(0) $other_tcp(0)
set other_sink(0) [new Agent/TCPSink]
$ns attach-agent $others(1) $other_sink(0)
$ns connect $other_tcp(0) $other_sink(0)
$other_tcp(0) set fid_ 2
set other_ftp(0) [new Application/FTP]
$other_ftp(0) attach-agent $other_tcp(0)
$other_ftp(0) set type_ FTP

#set other_udp [new Agent/UDP]
#$ns attach-agent $others(2) $other_udp
#set other_null [new Agent/Null]
#$ns attach-agent $others(3) $other_null
#$ns connect $other_udp $other_null
#set other_cbr [new Application/Traffic/CBR]
#$other_cbr attach-agent $other_udp
#$other_cbr set type_ CBR
#$other_cbr set packetSize_ $pktSize
#$other_cbr set rate_ 0.7Gb
#$other_cbr set random_ false
for {set i 1} {$i <= $n_conn} {incr i} {
    set other_tcp($i) [new Agent/TCP/Vegas]
    $ns attach-agent $others(2) $other_tcp($i)
    set other_sink($i) [new Agent/TCPSink]
    $ns attach-agent $others(3) $other_sink($i)
    $ns connect $other_tcp($i) $other_sink($i)
    $other_tcp($i) set fid_ [expr $i+2]
    set other_ftp($i) [new Application/FTP]
    $other_ftp($i) attach-agent $other_tcp($i)
    $other_ftp($i) set type_ FTP
}

# queue monitoring
set qf_size [open $out_q_file w]

set qmon_size [$ns monitor-queue $switch(0) $switch(1) $qf_size $samp_int]
[$ns link $switch(0) $switch(1)] queue-sample-timeout
set qmon_size [$ns monitor-queue $switch(1) $switch(2) $qf_size $samp_int]
[$ns link $switch(1) $switch(2)] queue-sample-timeout

#Schedule events for the FTP agents

#$ns at 0 "$other_ftp start"
#$ns at $run_time "$other_ftp stop"
#$ns at 0 "$other_cbr start"
#$ns at $run_time "$other_cbr stop"

for {set i 0} {$i <= $n_conn} {incr i} {
    $ns at 0 "$other_ftp($i) start"
    $ns at $run_time "$other_ftp($i) stop"
}
$ns at 0.0001 "$my_ftp start"
$ns at $run_time "$my_ftp stop"

#Call the finish procedure after run_time seconds of simulation time
$ns at $run_time "finish"

#Define a 'finish' procedure
proc finish {} {
    global congestion_alg ns tracefile rttFile qf_size out_dir nf
    $ns flush-trace
    # Close the NAM trace file
    close $nf
    close $tracefile
    close $rttFile 
    close $qf_size
    # Execute NAM on the trace file
    exec nam $out_dir$congestion_alg.nam &
    exit 0
}

#Run the simulation
$ns run
