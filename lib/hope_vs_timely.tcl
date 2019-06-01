
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
set rtt_file [open $out_rtt_file w]
set out_q_file $out_dir$congestion_alg.queue.out

# Number of switches along the skinny path
set n_switch 6
set last_sw [expr $n_switch-1]
# Number of connections at the crowded node
set n_crowd 6
set second_crowd [expr int($n_crowd/2)]

# samp_int (sec)
set samp_int 0.0001
# q_size (pkts)
set q_size 200
# link_cap (Mbps)
set link_cap 10Gb
set other_link_cap 10Gb
# link_delay (ms)
set link_delay 5us
set other_link_delay 17.4us
# tcp_window (pkts)
set tcp_window 10000000
# run_time (sec)
set run_time 0.1
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
set timely_t_low 0.00012
set timely_t_high 0.0005
set timely_additiveInc 20000000.0
set timely_decreaseFac 0.6
set timely_HAI_thresh 5
set timely_rate 2000000000.0
set hope_bits 0

##### Switch Parameters ####
set drop_prio_ false
set deque_prio_ false

#Create a simulator object
set ns [new Simulator]
$ns color 0 Red
$ns color 2 Green
$ns color 3 Black
$ns color 4 Blue
$ns color 5 Orange
$ns color 6 Brown
$ns color 7 Green
$ns color 8 Black
$ns color 9 Blue
$ns color 10 Orange
$ns color 11 Brown
$ns color 12 Green
$ns color 13 Black
$ns color 14 Blue
$ns color 15 Orange
$ns color 16 Brown


#Open the Trace files
set tracefile [open $out_dir$congestion_alg.tr w]
$ns trace-all $tracefile

#Open the NAM trace file
set nf [open $out_dir$congestion_alg.nam w]
$ns namtrace-all $nf

# Create TOR_switch, server, and client nodes
set my_src [$ns node]
$ns at 0.0 "$my_src label \"Source\""

for {set i 0} {$i < $n_switch} {incr i} {
    set switch($i) [$ns node]
}

set my_dst [$ns node]
$ns at 0.0 "$my_dst label \"Destination\""

for {set i 0} {$i < $n_switch} {incr i} {
    set others($i) [$ns node]
}
for {set i 1} {$i < $last_sw} {incr i} {
    set indx [expr $last_sw+$i]
    set others($indx) [$ns node]
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
for {set i 0} {$i < $last_sw} {incr i} {
    set next_sw [expr $i+1]
    $ns duplex-link $switch($i) $switch($next_sw) $link_cap $link_delay $queue_type
}
$ns duplex-link $switch($last_sw) $my_dst $link_cap $link_delay $queue_type

for {set i 0} {$i < $n_switch} {incr i} {
    $ns duplex-link $switch($i) $others($i) $other_link_cap $other_link_delay $queue_type
}
for {set i 1} {$i < $last_sw} {incr i} {
    set indx [expr $last_sw+$i]
    $ns duplex-link $switch($i) $others($indx) $other_link_cap $other_link_delay $queue_type
}

#Monitor the queue for link. (for NAM)
for {set i 0} {$i < $last_sw} {incr i} {
    set next_sw [expr $i+1]
    $ns duplex-link-op $switch($i) $switch($next_sw) queuePos 0.5
}

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
    $my_tcp set fid_ 0
    $my_sink listen
    
    # set up FTP connections
    set my_ftp [$my_tcp attach-source FTP]
    $my_ftp set type_ FTP
    
    # The following procedure is called whenever a packet is received 
    Agent/TCP/FullTcp instproc recv {rtt_t} {
		global ns rtt_file 
		$self instvar fid_      
	
		$self instvar node_
		if {[$node_ id] == 0 } {
	    	set now [$ns now]
	    	set rtt [$self set rtt_]
	
	    	puts $rtt_file "$now $fid_ $rtt"
		}
    }

} else {
    set my_tcp [new Agent/TCP/Vegas]
    set my_sink [new Agent/TCPSink]
    $ns attach-agent $my_src $my_tcp
    $ns attach-agent $my_dst $my_sink
    $ns connect $my_tcp $my_sink
    $my_tcp set fid_ 0

    if {[string compare $congestion_alg "vegas"] == 0} {    
        set timely 0
		set hope_type 0
		set hope_collector 0
    } elseif {[string compare $congestion_alg "timely"] == 0} { 
		set timely 1
		set hope_type 0 
		set hope_collector 0  
    } elseif {[string compare $congestion_alg "hope_sum"] == 0} {
		set timely 0
		set hope_type 2 
		set hope_collector 0    
    } elseif {[string compare $congestion_alg "hope_max"] == 0} { 
		set timely 0   
		set hope_type 1 
		set hope_collector 0 
    } elseif {[string compare $congestion_alg "hope_maxq"] == 0} {
		set timely 0    
		set hope_type 1 
		set hope_collector 1 
    } elseif {[string compare $congestion_alg "hope_maxqd"] == 0} { 
		set timely 0   
		set hope_type 1 
		set hope_collector 2 
    } elseif {[string compare $congestion_alg "hope_maxe"] == 0} { 
		set timely 0
		set hope_type 1 
		set hope_collector 3  
		set timely_t_low -10  
    } elseif {[string compare $congestion_alg "hope_maxed"] == 0} {
		set timely 0 
		set hope_type 1 
		set hope_collector 4  
		set timely_t_low -10   
    } elseif {[string compare $congestion_alg "hope_sumq"] == 0} { 
		set timely 0
		set hope_type 2 
		set hope_collector 1    
    } elseif {[string compare $congestion_alg "hope_sumqd"] == 0} {
		set timely 0
		set hope_type 2 
		set hope_collector 2     
    } elseif {[string compare $congestion_alg "hope_sume"] == 0} {
		set timely 0
		set hope_type 2 
		set hope_collector 3  
		set timely_t_low -10    
    } elseif {[string compare $congestion_alg "hope_sumed"] == 0} {
		set timely 0
		set hope_type 2 
		set hope_collector 4  
		set timely_t_low -10    
    } elseif {[string compare $congestion_alg "hope_squ"] == 0} {
		set timely 0 
		set hope_type 3 
		set hope_collector 0   
    } elseif {[string compare $congestion_alg "hope_squq"] == 0} {
		set timely 0
		set hope_type 3 
		set hope_collector 1    
    }

    $my_tcp set timely_packetSize_ [expr $pktSize+40]
    $my_tcp set timely_ewma_alpha_ $timely_ewma_alpha
    $my_tcp set timely_t_low_ $timely_t_low
    $my_tcp set timely_t_high_ $timely_t_high
    $my_tcp set timely_additiveInc_ $timely_additiveInc
    $my_tcp set timely_decreaseFac_ $timely_decreaseFac
    $my_tcp set rttNoise_ 0
    $my_tcp set timely_HAI_thresh_ $timely_HAI_thresh
    $my_tcp set timely_rate_ $timely_rate
    $my_tcp set timely_ $timely
    $my_tcp set hope_type_ $hope_type
    $my_tcp set hope_collector_ $hope_collector
    $my_tcp set hope_bits_ $hope_bits 

    # set up FTP connections
    set my_ftp [$my_tcp attach-source FTP]
    $my_ftp set type_ FTP
    
}

# Connect "others"
for {set i 0} {$i < $last_sw} {incr i} {
    if { $i < [expr $last_sw-2] } {

		set other_tcp($i) [new Agent/TCP/Vegas]
		$ns attach-agent $others($i) $other_tcp($i)
		set other_sink($i) [new Agent/TCPSink]
		$ns attach-agent $others([expr $i+$n_switch]) $other_sink($i)
		$ns connect $other_tcp($i) $other_sink($i)
		$other_tcp($i) set fid_ [expr $i+2]
		set other_ftp($i) [new Application/FTP]
		$other_ftp($i) attach-agent $other_tcp($i)
		$other_ftp($i) set type_ FTP
		#$other_tcp($i) set timely_ 0
		#$other_tcp($i) set hope_type_ 0 

    } elseif { $i < [expr $last_sw-1] } {

		for {set j 0} {$j < $second_crowd} {incr j} {
	    	set indx [expr $i+$j]
    	    set other_tcp($indx) [new Agent/TCP/Vegas]
	    	$ns attach-agent $others($i) $other_tcp($indx)
    	    set other_sink($indx) [new Agent/TCPSink]
    	    $ns attach-agent $others([expr $i+$n_switch]) $other_sink($indx)
    	    $ns connect $other_tcp($indx) $other_sink($indx)
    	    $other_tcp($indx) set fid_ [expr $indx+2]
    	    set other_ftp($indx) [new Application/FTP]
    	    $other_ftp($indx) attach-agent $other_tcp($indx)
    	    $other_ftp($indx) set type_ FTP
	    	#$other_tcp($indx) set timely_ 0
	    	#$other_tcp($indx) set hope_type_ 0

		}

    } else {

		for {set j 0} {$j < $n_crowd} {incr j} {
	    	set indx [expr $second_crowd+$i-1+$j]
    	    set other_tcp($indx) [new Agent/TCP/Vegas]
	    	$ns attach-agent $others($i) $other_tcp($indx)
    	    set other_sink($indx) [new Agent/TCPSink]
    	    $ns attach-agent $others($last_sw) $other_sink($indx)
    	    $ns connect $other_tcp($indx) $other_sink($indx)
    	    $other_tcp($indx) set fid_ [expr $indx+2]
    	    set other_ftp($indx) [new Application/FTP]
    	    $other_ftp($indx) attach-agent $other_tcp($indx)
    	    $other_ftp($indx) set type_ FTP
	    	#$other_tcp($indx) set timely_ 0
	    	#$other_tcp($indx) set hope_type_ 0

		}

    }
}
for {set i 0} {$i < [expr $n_switch+$second_crowd+$n_crowd-3]} {incr i} {
    $other_tcp($i) set timely_packetSize_ [expr $pktSize+40]
    $other_tcp($i) set timely_ewma_alpha_ $timely_ewma_alpha
    $other_tcp($i) set timely_t_low_ $timely_t_low
    $other_tcp($i) set timely_t_high_ $timely_t_high
    $other_tcp($i) set timely_additiveInc_ $timely_additiveInc
    $other_tcp($i) set timely_decreaseFac_ $timely_decreaseFac
    $other_tcp($i) set timely_HAI_thresh_ $timely_HAI_thresh
    $other_tcp($i) set timely_rate_ $timely_rate
    $other_tcp($i) set timely_ $timely
    $other_tcp($i) set hope_type_ $hope_type
    $other_tcp($i) set hope_collector_ $hope_collector 
    $other_tcp($i) set hope_bits_ $hope_bits
}

#set disruptor [new Agent/TCP/Vegas]
#$ns attach-agent $others(0) $disruptor
#set disruptor_sink [new Agent/TCPSink]
#$ns attach-agent $others($n_switch) $disruptor_sink
#$ns connect $disruptor $disruptor_sink
#$disruptor set fid_ [expr $second_crowd+$n_crowd-1+$n_switch]
#set disruptor_ftp [new Application/FTP]
#$disruptor_ftp attach-agent $disruptor
#$disruptor_ftp set type_ FTP
#$disruptor set timely_ 0
#$disruptor set hope_type_ 0
#$ns at [expr $run_time*0.4] "$disruptor_ftp start"
#$ns at [expr $run_time*0.6] "$disruptor_ftp stop"

Agent/TCP/Vegas instproc recv {rtt_t cong_signal_t hopCnt_t timely_rate_t} {
	global ns rtt_file  
	$self instvar fid_     
	
	$self instvar node_
	if {[$node_ id] == 0 } {
	    set now [$ns now]
	    set rtt [expr $rtt_t*1000000.0]
	
	    puts $rtt_file "$now $fid_ $rtt"
	}
}

# queue monitoring
set qf_size [open $out_q_file w]

for {set i 0} {$i < $last_sw} {incr i} {
    set next_sw [expr $i+1]
    set qmon_size [$ns monitor-queue $switch($i) $switch($next_sw) $qf_size $samp_int]
    [$ns link $switch($i) $switch($next_sw)] queue-sample-timeout
}

#Schedule events for the FTP agents

for {set i 0} {$i < [expr $n_switch+$second_crowd+$n_crowd-3]} {incr i} {
    $ns at 0 "$other_ftp($i) start"
    $ns at $run_time "$other_ftp($i) stop"
}
$ns at 0.0000 "$my_ftp start"
$ns at $run_time "$my_ftp stop"

#Call the finish procedure after run_time seconds of simulation time
$ns at $run_time "finish"

#Define a 'finish' procedure
proc finish {} {
    global congestion_alg ns tracefile rtt_file qf_size out_dir nf
    $ns flush-trace
    # Close the NAM trace file
    close $nf
    close $tracefile
    close $rtt_file 
    close $qf_size
    # Execute NAM on the trace file
    exec nam $out_dir$congestion_alg.nam &
    exit 0
}

#Run the simulation
$ns run
