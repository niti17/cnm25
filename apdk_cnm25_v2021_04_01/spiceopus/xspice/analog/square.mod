/* $Id: cfunc.tpl,v 1.1 91/03/18 19:01:04 bill Exp $ */
/*.......1.........2.........3.........4.........5.........6.........7.........8
================================================================================

FILE square/cfunc.mod

Copyright 1991
Georgia Tech Research Corporation, Atlanta, Ga. 30332
All Rights Reserved

PROJECT A-8503-405
               

AUTHORS                      

    12 Apr 1991     Harry Li


MODIFICATIONS   

     2 Oct 1991    Jeffrey P. Murray
                                   

SUMMARY

    This file contains the model-specific routines used to
    functionally describe the square (controlled squarewave
    oscillator) code model.


INTERFACES       

    FILE                 ROUTINE CALLED     

    CMmacros.h           cm_message_send();                   
                             
    CM.c                 void *cm_analog_alloc()
                         void *cm_analog_get_ptr()
                         int cm_analog_set_temp_bkpt()


REFERENCED FILES

    Inputs from and outputs to ARGS structure.
                     

NON-STANDARD FEATURES

    NONE

===============================================================================*/

/*=== INCLUDE FILES ====================*/

#include "square.h" 

                                      

/*=== CONSTANTS ========================*/




/*=== MACROS ===========================*/



  
/*=== LOCAL VARIABLES & TYPEDEFS =======*/                         


    
           
/*=== FUNCTION PROTOTYPE DEFINITIONS ===*/



                   
/*==============================================================================

FUNCTION void cm_square()

AUTHORS                      

    12 Apr 1991     Harry Li

MODIFICATIONS   

     2 Oct 1991    Jeffrey P. Murray

SUMMARY

    This function implements the square (controlled squarewave
    oscillator) code model.

INTERFACES       

    FILE                 ROUTINE CALLED     

    CMmacros.h           cm_message_send();                   
                             
    CM.c                 void *cm_analog_alloc()
                         void *cm_analog_get_ptr()
                         int cm_analog_set_temp_bkpt()


RETURNED VALUE
    
    Returns inputs and outputs via ARGS structure.

GLOBAL VARIABLES
    
    NONE

NON-STANDARD FEATURES

    NONE

==============================================================================*/

/*=== CM_SQUARE ROUTINE ===*/


/***********************************************************
*                                                          *
*  I                   <-dutycycle->                       *
*  I                                                       *
*  I                      out_high                         *
*  I                   t2    |     t3                      *
*  I                    \____v_____/                       *
*  I                    /          \                       *
*  I                                                       *
*  I                   /            \                      *
*  I                       	                               *
*  I                  /              \                     *
*  I                                                       *
*  I-----------------I                I---------------     *     
*		  ^			t1				 t4                    *
*         |                                                *
*      out_low                                             *
*                     t2 = t1 + t_rise                     *
*                     t4 = t3 + t_fall                     *
*                                                          *
***********************************************************/

void cm_square(ARGS)  /* structure holding parms, 
                                   inputs, outputs, etc.     */
{
    	int i;            /* generic loop counter index */
	int cntl_size;    /* control array size         */
	int freq_size;    /* frequency array size       */
	int int_cycle;    /* integer number of cycles   */ 

    	double *x;        /* pointer to the control array values */
	double *y;        /* pointer to the frequecy array values */
	double cntl_input; /* control input                       */
	double out;        /* output */
	double dout_din;   /* slope of the frequency array wrt the control
						  array.  Used to extrapolate a frequency above
						  and below the control input high and low level */
	double output_low; /* output low */
	double output_hi;  /* output high */
	double dphase;     /* fractional part into cycle */
    	double *phase;     /* pointer to the phase value */
	double *phase1;    /* pointer to the old phase value */
	double freq;       /* frequency of the wave           */
	double d_cycle;    /* duty cycle   */
	double *t1;        /* pointer containing the value of time1 */
	double *t2;        /* pointer containing the value of time2 */
	double *t3;        /* pointer containing the value of time3 */
	double *t4;        /* pointer containing the value of time4 */
     	double time1;      /* time1 = duty_cycle * period of the wave */    
	double time2;      /* time2 = time1 + risetime */
	double time3;      /* time3 = current time+time to end of period*/  
	double time4;      /* time4 = time3 + falltime */
	double t_rise;     /* risetime */
	double t_fall;     /* falltime */

    Mif_Complex_t ac_gain;

    /**** Retrieve frequently used parameters... ****/

    cntl_size = PARAM_SIZE(cntl_array);           
    freq_size = PARAM_SIZE(freq_array);           
    output_low = PARAM(out_low);
    output_hi = PARAM(out_high);
    d_cycle = PARAM(duty_cycle);
    t_rise = PARAM(rise_time);
    t_fall = PARAM(fall_time);

    /* check and make sure that the control array is the
	   same size as the frequency array */

	if(cntl_size != freq_size){
		cm_message_send(square_array_error);
		return;
 	}

   /* First time throught allocate memory */
  if(INIT==1){
		phase = cm_analog_alloc(INT1,sizeof(double));
		t1 = cm_analog_alloc(T1,sizeof(double));
		t2 = cm_analog_alloc(T2,sizeof(double));
		t3 = cm_analog_alloc(T3,sizeof(double));
		t4 = cm_analog_alloc(T4,sizeof(double));

	}

    if(ANALYSIS == MIF_DC){

	/* initialize time values */
	t1 = cm_analog_get_ptr(T1,0);
	t2 = cm_analog_get_ptr(T2,0);
	t3 = cm_analog_get_ptr(T3,0);
	t4 = cm_analog_get_ptr(T4,0);

	*t1 = -1;
	*t2 = -1;
	*t3 = -1;
	*t4 = -1;

		OUTPUT(out) = output_low;
		PARTIAL(out,cntl_in) = 0; 

  }else

  /* Retrieve previous values */

  if(ANALYSIS == MIF_TRAN){

	phase = cm_analog_get_ptr(INT1,0);
	phase1 = cm_analog_get_ptr(INT1,1);
	t1 = cm_analog_get_ptr(T1,1);
	t2 = cm_analog_get_ptr(T2,1);
	t3 = cm_analog_get_ptr(T3,1);
	t4 = cm_analog_get_ptr(T4,1);

	time1 = *t1;
	time2 = *t2;
	time3 = *t3;
	time4 = *t4;

    /* Allocate storage for breakpoint domain & freq. range values */

    x = (double *) tmalloc(cntl_size*sizeof(double));
    if (x == '\0') {
        cm_message_send(square_allocation_error); 
        return;
    }

    y = (double *) tmalloc(freq_size*sizeof(double));
    if (y == '\0') {
        cm_message_send(square_allocation_error);  
        return;
    }

    /* Retrieve x and y values. */       
    for (i=0; i<cntl_size; i++) {
        *(x+i) = PARAM(cntl_array[i]);
        *(y+i) = PARAM(freq_array[i]);
    }                       
    
    /* Retrieve cntl_input value. */       
    cntl_input = INPUT(cntl_in);

    /* Determine segment boundaries within which cntl_input resides */
				/*** cntl_input below lowest cntl_voltage ***/
    if (cntl_input <= *x) {
             dout_din = (*(y+1) - *y)/(*(x+1) - *x);
             freq = *y + (cntl_input - *x) * dout_din;

	     if(freq <= 0){
		  cm_message_send(square_freq_clamp);
		  freq = 1e-16;
             }
		/* freq = *y; */	
    }
    else 
        /*** cntl_input above highest cntl_voltage ***/
	
        if (cntl_input >= *(x+cntl_size-1)){ 
            dout_din = (*(y+cntl_size-1) - *(y+cntl_size-2)) /
                          (*(x+cntl_size-1) - *(x+cntl_size-2));
            freq = *(y+cntl_size-1) + (cntl_input - *(x+cntl_size-1)) * dout_din;
			/* freq = *(y+cntl_size-1); */

        } else { /*** cntl_input within bounds of end midpoints...   
                must determine position progressively & then 
                calculate required output.                    ***/

            for (i=0; i<cntl_size-1; i++) {

                if ((cntl_input < *(x+i+1)) && (cntl_input >= *(x+i))){ 
            		
					/* Interpolate to the correct frequency value */

					freq = ((cntl_input - *(x+i))/(*(x+i+1) - *(x+i)))* 
							(*(y+i+1)-*(y+i)) + *(y+i); 
                } 
    
            }
        }
       /* calculate the instantaneous phase */
		*phase = *phase1 + freq*(TIME - T(1));

		/* convert the phase to an integer */
		int_cycle = *phase1;
		
		/* dphase is the percent into the cycle for
	       the period */	
		dphase = *phase1 - int_cycle;

	/* Calculate the time variables and the output value
		for this iteration */ 	

	if((time1 <= TIME) && (TIME <= time2)){
		time3 = T(1) + (1 - dphase)/freq;
		time4 = time3 + t_fall;

		if(TIME < time2){
			cm_analog_set_temp_bkpt(time2);
		}

		cm_analog_set_temp_bkpt(time3);
		cm_analog_set_temp_bkpt(time4);
			
        OUTPUT(out) = output_low + ((TIME - time1)/(time2 - time1))*
			(output_hi - output_low); 

	}else
	
	if((time2 <= TIME) && (TIME <= time3)){

		time3 = T(1) + (1.0 - dphase)/freq;
		time4 = time3 + t_fall;
		if(TIME < time3){
			cm_analog_set_temp_bkpt(time3);
		}
		cm_analog_set_temp_bkpt(time4);
        OUTPUT(out) = output_hi;

	}else

	if((time3 <= TIME) && (TIME <= time4)){
		
		if(dphase > 1-d_cycle){
			dphase = dphase - 1.0;
		}

		/* subtract d_cycle from 1 because my initial definition
		of duty cyle was that part of the cycle which the output 
		is low.  The more standard definition is the part of the 
		cycle where the output is high. */
		time1 = T(1) + ((1-d_cycle) - dphase)/freq;
		time2 = time1 + t_rise;

		if(TIME < time4){
			cm_analog_set_temp_bkpt(time4);
		}

		cm_analog_set_temp_bkpt(time1);
		cm_analog_set_temp_bkpt(time2);

		OUTPUT(out) = output_hi + ((TIME - time3)/(time4 - time3))*
			(output_low - output_hi);

	}else{

		if(dphase > 1-d_cycle){
			dphase = dphase - 1.0;
		}

		/* subtract d_cycle from 1 because my initial definition
		of duty cyle was that part of the cycle which the output 
		is low.  The more standard definition is the part of the 
		cycle where the output is high. */
		time1 = T(1) + ((1-d_cycle) - dphase)/freq;
		time2 = time1 + t_rise;

		if((TIME < time1) || (T(1) == 0)){
			cm_analog_set_temp_bkpt(time1);
		}

		cm_analog_set_temp_bkpt(time2);
			OUTPUT(out) = output_low;
	}

	PARTIAL(out,cntl_in) = 0.0;

     /* set the time values for storage */

	t1 = cm_analog_get_ptr(T1,0);
	t2 = cm_analog_get_ptr(T2,0);
	t3 = cm_analog_get_ptr(T3,0);
	t4 = cm_analog_get_ptr(T4,0);

	*t1 = time1;
	*t2 = time2; 
	*t3 = time3;
	*t4 = time4;

    } else {                      /* Output AC Gain */

   /* This model has no AC capabilities */

        ac_gain.real = 0.0; 
        ac_gain.imag= 0.0;
        AC_GAIN(out,cntl_in) = ac_gain;
    }
} 

