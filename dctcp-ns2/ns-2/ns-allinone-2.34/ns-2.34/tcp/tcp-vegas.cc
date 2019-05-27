/* -*-	Mode:C++; c-basic-offset:8; tab-width:8; indent-tabs-mode:t -*- */

/*
 * tcp-vegas.cc
 * Copyright (C) 1997 by the University of Southern California
 * $Id: tcp-vegas.cc,v 1.37 2005/08/25 18:58:12 johnh Exp $
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License,
 * version 2, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 *
 *
 * The copyright of this module includes the following
 * linking-with-specific-other-licenses addition:
 *
 * In addition, as a special exception, the copyright holders of
 * this module give you permission to combine (via static or
 * dynamic linking) this module with free software programs or
 * libraries that are released under the GNU LGPL and with code
 * included in the standard release of ns-2 under the Apache 2.0
 * license or under otherwise-compatible licenses with advertising
 * requirements (or modified versions of such code, with unchanged
 * license).  You may copy and distribute such a system following the
 * terms of the GNU GPL for this module and the licenses of the
 * other code concerned, provided that you include the source code of
 * that other code when and as the GNU GPL requires distribution of
 * source code.
 *
 * Note that people who make modified versions of this module
 * are not obligated to grant this special exception for their
 * modified versions; it is their choice whether to do so.  The GNU
 * General Public License gives permission to release a modified
 * version without this exception; this exception also makes it
 * possible to release a modified version which carries forward this
 * exception.
 *
 */

/*
 * ns-1 implementation:
 *
 * This is an implementation of U. of Arizona's TCP Vegas. I implemented
 * it based on USC's NetBSD-Vegas.
 *					Ted Kuo
 *					North Carolina St. Univ. and
 *					Networking Software Div, IBM
 *					tkuo@eos.ncsu.edu
 */

#ifndef lint
static const char rcsid[] =
"@(#) $Header: /cvsroot/nsnam/ns-2/tcp/tcp-vegas.cc,v 1.37 2005/08/25 18:58:12 johnh Exp $ (NCSU/IBM)";
#endif

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <cmath>

#include "ip.h"
#include "tcp.h"
#include "flags.h"

#define MIN(x, y) ((x)<(y) ? (x) : (y))


static class VegasTcpClass : public TclClass {
public:
	VegasTcpClass() : TclClass("Agent/TCP/Vegas") {}
	TclObject* create(int, const char*const*) {
		return (new VegasTcpAgent());
	}
} class_vegas;


VegasTcpAgent::VegasTcpAgent() : TcpAgent()
{
	v_sendtime_ = NULL;
	v_transmits_ = NULL;
}

VegasTcpAgent::~VegasTcpAgent()
{
	if (v_sendtime_)
		delete []v_sendtime_;
	if (v_transmits_)
		delete []v_transmits_;
}

void
VegasTcpAgent::delay_bind_init_all()
{
	/* Serhat's implementation of TIMELY */
	delay_bind_init_one("timely_");
	delay_bind_init_one("timely_packetSize_");
	delay_bind_init_one("timely_ewma_alpha_");
	delay_bind_init_one("timely_t_low_");
	delay_bind_init_one("timely_t_high_");
	delay_bind_init_one("timely_additiveInc_");
	delay_bind_init_one("timely_decreaseFac_");
	delay_bind_init_one("timely_HAI_thresh_");
	delay_bind_init_one("timely_rate_");
	/* Serhat's implementation of HOPE */
	delay_bind_init_one("hope_type_");
	delay_bind_init_one("hope_collector_");
	delay_bind_init_one("hope_bits_");
	/* End of TIMELY and HOPE parameters */

	delay_bind_init_one("v_alpha_");
	delay_bind_init_one("v_beta_");
	delay_bind_init_one("v_gamma_");
	delay_bind_init_one("v_rtt_");
	TcpAgent::delay_bind_init_all();
        reset();
}

int
VegasTcpAgent::delay_bind_dispatch(const char *varName, const char *localName, 
				   TclObject *tracer)
{
	/* Serhat's implementation of TIMELY */
	if (delay_bind(varName, localName, "timely_", &timely_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "timely_packetSize_", &timely_packetSize_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "timely_ewma_alpha_", &timely_ewma_alpha_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "timely_t_low_", &timely_t_low_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "timely_t_high_", &timely_t_high_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "timely_additiveInc_", &timely_additiveInc_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "timely_decreaseFac_", &timely_decreaseFac_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "timely_HAI_thresh_", &timely_HAI_thresh_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "timely_rate_", &timely_rate_, tracer)) 
		return TCL_OK;
	/* Serhat's implementation of HOPE */
	if (delay_bind(varName, localName, "hope_type_", &hope_type_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "hope_collector_", &hope_collector_, tracer)) 
		return TCL_OK;
	if (delay_bind(varName, localName, "hope_bits_", &hope_bits_, tracer)) 
		return TCL_OK;
	/* End of TIMELY and HOPE parameters */
	
	/* init vegas var */
        if (delay_bind(varName, localName, "v_alpha_", &v_alpha_, tracer)) 
		return TCL_OK;
        if (delay_bind(varName, localName, "v_beta_", &v_beta_, tracer)) 
		return TCL_OK;
        if (delay_bind(varName, localName, "v_gamma_", &v_gamma_, tracer)) 
		return TCL_OK;
        if (delay_bind(varName, localName, "v_rtt_", &v_rtt_, tracer)) 
		return TCL_OK;
        return TcpAgent::delay_bind_dispatch(varName, localName, tracer);
}

void
VegasTcpAgent::reset()
{
	/* Serhat's implementation of TIMELY */	
	timely_prevRTT_ = 0;	
	timely_lastUpdateTime = 0;	
	timely_avgRTTDiff_ = 0;	
	timely_negGradientCount_ = 0;	
	cong_signal_ = -1;
	/* End of TIMELY parameters */

	t_cwnd_changed_ = 0.;
	firstrecv_ = -1.0;
	v_slowstart_ = 2;
	v_sa_ = 0;
	v_sd_ = 0;
	v_timeout_ = 1000.;
	v_worried_ = 0;
	v_begseq_ = 0;
	v_begtime_ = 0.;
	v_cntRTT_ = 0; v_sumRTT_ = 0.;
	v_baseRTT_ = 1000000000.;
	v_incr_ = 0;
	v_inc_flag_ = 1;

	TcpAgent::reset();
}

void
VegasTcpAgent::recv_newack_helper(Packet *pkt)
{
	newack(pkt);
#if 0
	// like TcpAgent::recv_newack_helper, but without this
	if ( !hdr_flags::access(pkt)->ecnecho() || !ecn_ ) {
	        opencwnd();
	}
#endif
	/* if the connection is done, call finish() */
	if ((highest_ack_ >= curseq_-1) && !closed_) {
		closed_ = 1;
		finish();
	}
}

void
VegasTcpAgent::recv(Packet *pkt, Handler *)
{
	double currentTime = vegastime();
	hdr_tcp *tcph = hdr_tcp::access(pkt);
	hdr_flags *flagh = hdr_flags::access(pkt);

#if 0
	if (pkt->type_ != PT_ACK) {
		Tcl::instance().evalf("%s error \"recieved non-ack\"",
				      name());
		Packet::free(pkt);
		return;
	}
#endif /* 0 */
	++nackpack_;

	if(firstrecv_<0) { // init vegas rtt vars
		firstrecv_ = currentTime;
		v_baseRTT_ = v_rtt_ = firstrecv_;
		v_sa_  = v_rtt_ * 8.;
		v_sd_  = v_rtt_;
		v_timeout_ = ((v_sa_/4.)+v_sd_)/2.;
	}

	if (flagh->ecnecho())
		ecn(tcph->seqno());
	if (tcph->seqno() > last_ack_) {
		if (last_ack_ == 0 && delay_growth_) {
			cwnd_ = initial_window();
		}
		/* check if cwnd has been inflated */
		if(dupacks_ > numdupacks_ &&  cwnd_ > v_newcwnd_) {
			cwnd_ = v_newcwnd_;
			// vegas ssthresh is used only during slow-start
			ssthresh_ = 2;
		}
		int oldack = last_ack_;

		recv_newack_helper(pkt);
			
		/*
		 * begin of once per-rtt actions
		 * 	1. update path fine-grained rtt and baseRTT
		 *  2. decide what to do with cwnd_, inc/dec/unchanged
		 *     based on delta=expect - actual.
		 */
		if(tcph->seqno() >= v_begseq_) {
			double rtt;
			if(v_cntRTT_ > 0)
				rtt = v_sumRTT_ / v_cntRTT_;
			else 
				rtt = currentTime - v_begtime_;
		
			v_sumRTT_ = 0.0;
			v_cntRTT_ = 0;

			// calc # of packets in transit
			int rttLen = t_seqno_ - v_begseq_;
			
			/*
		 	* decide should we incr/decr cwnd_ by how much
		 	*/
			if(rtt>0) {
				/* if there's only one pkt in transit, update 
		 	 	* baseRTT
		 	 	*/
				if(rtt<v_baseRTT_ || rttLen<=1)
					v_baseRTT_ = rtt;

				double expect;   // in pkt/sec
				// actual = (# in transit)/(current rtt) 
				v_actual_ = double(rttLen)/rtt;
				// expect = (current window size)/baseRTT
				expect = double(t_seqno_-last_ack_)/v_baseRTT_;

				// calc actual and expect thruput diff, delta
				int delta=int((expect-v_actual_)*v_baseRTT_+0.5);
				if(cwnd_ < ssthresh_) { // slow-start
					// adj cwnd every other rtt
					v_inc_flag_ = !v_inc_flag_;
					if(!v_inc_flag_)
						v_incr_ = 0;
					else {
				    		if(delta > v_gamma_) {
							// slow-down a bit to ensure
							// the net is not so congested
							ssthresh_ = 2;
							cwnd_-=(cwnd_/8);
							if(cwnd_<2)
								cwnd_ = 2.;
							v_incr_ = 0;
				    		} else 
							v_incr_ = 1;
					}
				} else { // congestion avoidance
					if(delta>v_beta_) {
						/*
						* slow down a bit, retrack
					 	* back to prev. rtt's cwnd
					 	* and dont incr in the nxt rtt
					 	*/
						--cwnd_;
						if(cwnd_<2) cwnd_ = 2;
						v_incr_ = 0;
					} else if(delta<v_alpha_)
						// delta<alpha, faster....
						v_incr_ = 1/cwnd_;
					else // current rate is cool.
						v_incr_ = 0;
				}
			} // end of if(rtt > 0)

			// tag the next packet 
			v_begseq_ = t_seqno_; 
			v_begtime_ = currentTime;
		} // end of once per-rtt section

		/* since we set how much to incr only once per rtt,
		 * need to check if we surpass ssthresh during slow-start
		 * before the rtt is over.
		 */		
		if(v_incr_ == 1 && cwnd_ >= ssthresh_)
			v_incr_ = 0;
		
		/*
		 * incr cwnd unless we havent been able to keep up with it
		 */
		if(v_incr_>0 && (cwnd_-(t_seqno_-last_ack_))<=2)
			cwnd_ = cwnd_+v_incr_;	

		// Add to make Vegas obey maximum congestion window variable.
		if (maxcwnd_ && (int(cwnd_) > maxcwnd_)) {
			cwnd_ = maxcwnd_;
		}

		/*
		 * See if we need to update the fine grained timeout value,
		 * v_timeout_
		 */

		// reset v_sendtime for acked pkts and incr v_transmits_
		double sendTime = v_sendtime_[tcph->seqno()%v_maxwnd_];
		int transmits = v_transmits_[tcph->seqno()% v_maxwnd_];
		int range = tcph->seqno() - oldack;
		for(int k=((oldack+1) %v_maxwnd_); 
			k<=(tcph->seqno()%v_maxwnd_) && range >0 ; 
			k=((k+1) % v_maxwnd_), range--) {
			v_sendtime_[k] = -1.0;
			v_transmits_[k] = 0;
		}
		
		double rtt, n;
		rtt = currentTime - sendTime;
		if((sendTime !=0.) && (transmits==1)) {
			 // update fine-grained timeout value, v_timeout_.
			
			v_sumRTT_ += rtt;
			++v_cntRTT_;
			if(rtt>0) {
				v_rtt_ = rtt;
				if(v_rtt_ < v_baseRTT_)
					v_baseRTT_ = v_rtt_;
				n = v_rtt_ - v_sa_/8;
				v_sa_ += n;
				n = n<0 ? -n : n;
				n -= v_sd_ / 4;
				v_sd_ += n;
				v_timeout_ = ((v_sa_/4)+v_sd_)/2;
				v_timeout_ += (v_timeout_/16);
			}
		} /* End of (sendTime !=0.) && (transmits==1) */

		/* 
		 * check the 1st or 2nd acks after dup ack received 
		 */
		if(v_worried_>0) {
			/*
			 * check if any pkt has been timeout. if so, 
			 * retx it. no need to change cwnd since we
			 * already did.
			 */
			--v_worried_;
			int expired=vegas_expire(pkt);
			if(expired>=0) {
				dupacks_ = numdupacks_;
				output(expired, TCP_REASON_DUPACK);
			} else
				v_worried_ = 0;
		} /* End of (v_worried_>0) */
		
		/* Serhat's implementation of TIMELY and HOPE */
		hdr_ip* iph = hdr_ip::access(pkt);
		int hop_cnt = iph->HOPE_hop_cnt(); 
		//hop_cnt = hop_cnt/2; //Only consider forward path
		double* hop_delay = iph->HOPE_hop_delay();

		if(cong_signal_ == -1) {
			timely_prevRTT_ = -1;
		}	
		cong_signal_ = rtt; //default congestion control algo is Timely	
			
		if(timely_==1 || hope_type_!=0){
			
			double line_rate = 10000000000.0;
			double baseBufferSize = 200.0;	//Use buffer size instead of baseRTT
			double packetSize = 1460;
			double epsilon = 0.000001;	//Threshold to say gradient <= 0
					
			if (hope_type_==1){
				// Max-delay to be used
				double max_delay = -999999.9;
				double dummy;
				for (int i=0; i<hop_cnt; i++){
					dummy = (double)*(hop_delay + i);
					if( hope_bits_ != 0){
						//printf("dummy: %f",dummy);
						// Use quantization for the congestion signal
						double num_interval = pow(2,hope_bits_);
						//printf(" num_interval: %f ",num_interval);
						double max_sgnl = (baseBufferSize*packetSize);
						//printf("| max_sgnl: %f ",max_sgnl);
						double interval = max_sgnl/num_interval;
						//printf("| interval: %f ",interval);
						double cur_interval = (int)(dummy/interval);
						//printf("| cur_interval: %f ",cur_interval);
						dummy = (cur_interval/num_interval)*max_sgnl;
						//printf("| new_dummy: %f\n",dummy);
					}
					if( dummy > max_delay){ max_delay = dummy;}
				}
				if (hope_collector_ == 0){
					cong_signal_ = max_delay;
				} else {
					cong_signal_ = max_delay* 8.0 / line_rate;
				}				
			} else if (hope_type_==2) {
				// Total queueing delay to be used
				double tot_delay = 0.0;
				double dummy;
				for (int i=0; i<hop_cnt; i++){
					dummy = (double)*(hop_delay + i);
					if( hope_bits_ != 0){
						// Use quantization for the congestion signal
						double num_interval = pow(2,hope_bits_);
						double max_sgnl = (baseBufferSize*packetSize);
						double interval = max_sgnl/num_interval;
						double cur_interval = (int)(dummy/interval);
						dummy = (cur_interval/num_interval)*max_sgnl;
					}
					tot_delay += dummy;
				}
				if (hope_collector_ == 0){
					cong_signal_ = tot_delay;
				} else {
					cong_signal_ = tot_delay* 8.0 / line_rate;
				}
			} else if (hope_type_==3) {
				// Squared queueing delay to be used
				double squ_delay = 0.0;
				double dummy;
				for (int i=0; i<hop_cnt; i++){
					dummy = (double)*(hop_delay + i);
					if( hope_bits_ != 0){
						// Use quantization for the congestion signal
						double num_interval = pow(2,hope_bits_);
						double max_sgnl = (baseBufferSize*packetSize);
						double interval = max_sgnl/num_interval;
						double cur_interval = (int)(dummy/interval);
						dummy = (cur_interval/num_interval)*max_sgnl;
					}
					squ_delay += pow(dummy,2);
				}
				squ_delay = sqrt(squ_delay);
				if (hope_collector_ == 0){
					cong_signal_ = squ_delay;
				} else {
					cong_signal_ = squ_delay* 8.0 / line_rate;
				}
			}
			
			
			if(timely_prevRTT_ == -1) {
				timely_prevRTT_ = cong_signal_;
				//timely_lastUpdateTime = currentTime;
			}
			
			double rtt_diff = cong_signal_ - timely_prevRTT_;
		
			if (rtt_diff < 0) {
    				timely_negGradientCount_++;
  			} else {
    				timely_negGradientCount_ = 0;
  			}

			timely_avgRTTDiff_ = ((1 - timely_ewma_alpha_) * timely_avgRTTDiff_) + (timely_ewma_alpha_ * rtt_diff);
			
			//printf("*** cwnd_= %f | avgRTTDiff= %f\n", (double)cwnd_, timely_avgRTTDiff_*1000000);
			//printf("*** rtt= %f | cong_sgnl= %f | prevRTT= %f | rtt_diff= %f | avgRTTDiff= %f | cwnd_= %f\n",rtt*1000000, cong_signal_*1000000, timely_prevRTT_*1000000, rtt_diff*1000000, timely_avgRTTDiff_*1000000, (double)cwnd_);

			double normalized_gradient = timely_avgRTTDiff_ / v_baseRTT_;
			//if (hope_collector_ != 0){
			//	normalized_gradient = timely_avgRTTDiff_ / baseBufferSize;
			//}

			double delta_factor = (currentTime - timely_lastUpdateTime) / v_baseRTT_;
  			delta_factor = (delta_factor<1.0)?delta_factor:1.0;
			delta_factor = (delta_factor>0.0)?delta_factor:0.0;

			double timely_oldRate = timely_rate_;
			//double old_cwnd = (double)cwnd_;
			if (rtt < timely_t_low_) { //additivive increase if rtt < t_low
      				timely_rate_ = timely_rate_ + (timely_additiveInc_ * delta_factor);
				//printf("****Entered rtt < timely_t_low \n");

  			} else if (rtt > timely_t_high_) { //multiplicative decrease if rtt > t_high
      				timely_rate_ =timely_rate_ *(1.0 -(delta_factor *timely_decreaseFac_ *(1.0 -(timely_t_high_ /rtt))));
				//printf("****Entered rtt > timely_t_low \n");

    			} else if (normalized_gradient <= epsilon) { //additive increase if avg gradient <= 0 
      					
        			int N = 1;
        			if (timely_negGradientCount_ >= timely_HAI_thresh_) N = 5;
        			timely_rate_ = timely_rate_ + (double(N) * timely_additiveInc_ * delta_factor);
				//printf("****Entered normalized_gradient <= 0 \n");

      			} else { //multiplicative decrease if avg gradient > 0
        			timely_rate_ = timely_rate_ * (1.0 - (timely_decreaseFac_ * normalized_gradient));
				//printf("****Entered gradient > 0 \n");

 			}
			timely_prevRTT_ = cong_signal_;
			timely_lastUpdateTime = currentTime;

			//derease in rate capped by 0.5 times the old rate
 			timely_rate_ = (timely_rate_<(timely_oldRate * 0.5))?(timely_oldRate * 0.5):timely_rate_;
		
			cwnd_ = timely_rate_ * rtt / double(timely_packetSize_ * 8.0);
			cwnd_ = ((double)cwnd_>1.0)?(double)cwnd_:1.1;

			//printf("*** rtt= %f | cong_sgnl= %f | old_cwnd= %f | old_rate= %f\n",rtt*1000000, cong_signal_*1000000, old_cwnd, timely_oldRate);
			//printf("**cur_time= %f | last_update_time= %f | base_rtt= %f\n", currentTime*1000, timely_lastUpdateTime*1000, v_baseRTT_);		
			//printf("*rtt_diff= %f | avgRTTDiff= %f | gradient= %f ", rtt_diff, timely_avgRTTDiff_, normalized_gradient*1000000000);
			//printf("| delta_factor= %f | new_cwnd = %f | new_rate= %f\n",delta_factor, (double)cwnd_, timely_rate_);
								
		} /* End of Serhat's Timely and Hope implementation */
		
		/* Serhat's implementation of instproc recv for TCL scripts */
		//Tcl::instance().evalf("%s recv %f", this->name(), rtt );
		Tcl::instance().evalf("%s recv %f %f %d %f", this->name(), rtt, cong_signal_, iph->HOPE_hop_cnt(), timely_rate_);
		
   	} else if (tcph->seqno() == last_ack_)  {
		/* check if a timeout should happen */
		++dupacks_; 
		int expired=vegas_expire(pkt);
		if (expired>=0 || dupacks_ == numdupacks_) {
			double sendTime=v_sendtime_[(last_ack_+1) % v_maxwnd_]; 
			int transmits=v_transmits_[(last_ack_+1) % v_maxwnd_];
       	                /* The line below, for "bug_fix_" true, avoids
                        * problems with multiple fast retransmits after
			* a retransmit timeout.
                        */
			if ( !bug_fix_ || (highest_ack_ > recover_) || \
			    ( last_cwnd_action_ != CWND_ACTION_TIMEOUT)) {
				int win = window();
				last_cwnd_action_ = CWND_ACTION_DUPACK;
				recover_ = maxseq_;
				/* check for timeout after recv a new ack */
				v_worried_ = MIN(2, t_seqno_ - last_ack_ );
		
				/* v_rto expon. backoff */
				if(transmits > 1) 
					v_timeout_ *=2.; 
				else
					v_timeout_ += (v_timeout_/8.);
				/*
				 * if cwnd hasnt changed since the pkt was sent
				 * we need to decr it.
				 */
				if(t_cwnd_changed_ < sendTime ) {
					if(win<=3)
						win=2;
					else if(transmits > 1)
						win >>=1;
					else 
						win -= (win>>2);

					// record cwnd_
					v_newcwnd_ = double(win);
					// inflate cwnd_
					cwnd_ = v_newcwnd_ + dupacks_;
					t_cwnd_changed_ = currentTime;
				} 

				// update coarser grained rto
				reset_rtx_timer(1);
				if(expired>=0) 
					output(expired, TCP_REASON_DUPACK);
				else
					output(last_ack_ + 1, TCP_REASON_DUPACK);
					 
				if(transmits==1) 
					dupacks_ = numdupacks_;
                        }
		} else if (dupacks_ > numdupacks_) 
			++cwnd_;
	}
	Packet::free(pkt);

#if 0
	if (trace_)
		plot();
#endif /* 0 */

	/*
	 * Try to send more data
	 */
	if (dupacks_ == 0 || dupacks_ > numdupacks_ - 1)
		send_much(0, 0, maxburst_);

}

void
VegasTcpAgent::timeout(int tno)
{
	if (tno == TCP_TIMER_RTX) {
		if (highest_ack_ == maxseq_ && !slow_start_restart_) {
			/*
			 * TCP option:
			 * If no outstanding data, then don't do anything.
			 *
			 * Note:  in the USC implementation,
			 * slow_start_restart_ == 0.
			 * I don't know what the U. Arizona implementation
			 * defaults to.
			 */
			return;
		};
		dupacks_ = 0;
		recover_ = maxseq_;
		last_cwnd_action_ = CWND_ACTION_TIMEOUT;
		reset_rtx_timer(0);
		++nrexmit_;
		slowdown(CLOSE_CWND_RESTART|CLOSE_SSTHRESH_HALF);
		cwnd_ = double(v_slowstart_);
		v_newcwnd_ = 0;
		t_cwnd_changed_ = vegastime();
		send_much(0, TCP_REASON_TIMEOUT);
	} else {
		/* delayed-sent timer, with random overhead to avoid
		 * phase effect. */
		send_much(1, TCP_REASON_TIMEOUT);
	};
}

void
VegasTcpAgent::output(int seqno, int reason)
{
	Packet* p = allocpkt();
	hdr_tcp *tcph = hdr_tcp::access(p);
	/* Serhat's implementation of HOPE */
	hdr_ip* iph = hdr_ip::access(p);
	iph->HOPE_hop_data() = hope_collector_;
	/* End of HOPE implementation */
	double now = Scheduler::instance().clock();
	tcph->seqno() = seqno;
	tcph->ts() = now;
	tcph->reason() = reason;

	/* if this is the 1st pkt, setup senttime[] and transmits[]
	 * I alloc mem here, instrad of in the constructor, to cover
	 * cases which windows get set by each different tcp flows */
	if (seqno==0) {
		v_maxwnd_ = int(wnd_);
		if (v_sendtime_)
			delete []v_sendtime_;
        	if (v_transmits_)
               		delete []v_transmits_;
		v_sendtime_ = new double[v_maxwnd_];
		v_transmits_ = new int[v_maxwnd_];
		for(int i=0;i<v_maxwnd_;i++) {
			v_sendtime_[i] = -1.;
			v_transmits_[i] = 0;
		}
	}

	// record a find grained send time and # of transmits 
	int index = seqno % v_maxwnd_;
	v_sendtime_[index] = vegastime();  
	++v_transmits_[index];

	/* support ndatabytes_ in output - Lloyd Wood 14 March 2000 */
	int bytes = hdr_cmn::access(p)->size(); 
	ndatabytes_ += bytes; 
	ndatapack_++; // Added this - Debojyoti 12th Oct 2000
	send(p, 0);
	if (seqno == curseq_ && seqno > maxseq_)
		idle();  // Tell application I have sent everything so far

	if (seqno > maxseq_) {
		maxseq_ = seqno;
		if (!rtt_active_) {
			rtt_active_ = 1;
			if (seqno > rtt_seq_) {
				rtt_seq_ = seqno;
				rtt_ts_ = now;
			}
		}
	} else {
		++nrexmitpack_;
       		nrexmitbytes_ += bytes;
    	}

	if (!(rtx_timer_.status() == TIMER_PENDING))
		/* No timer pending.  Schedule one. */
		set_rtx_timer();
}

/*
 * return -1 if the oldest sent pkt has not been timeout (based on
 * fine grained timer).
 */
int
VegasTcpAgent::vegas_expire(Packet* pkt)
{
	hdr_tcp *tcph = hdr_tcp::access(pkt);
	double elapse = vegastime() - v_sendtime_[(tcph->seqno()+1)%v_maxwnd_];
	if (elapse >= v_timeout_) {
		return(tcph->seqno()+1);
	}
	return(-1);
} 

