param S;
param D;
param N;

set shifts := {1..S};
set days := {1..D};
set nurses := {1..N};

param lambda_PC := 1;
param lambda_UC := 1;
param lambda_PS :=1;
param lambda_US :=1;

param demand{days, shifts} >= 0, integer;
param workhours_limit{nurses} > 0;
param vacation{days, nurses} >= 0, binary;
param preferred_companions{nurses, nurses}, integer;
param unpreferred_companions{nurses, nurses}, integer;
param preferred_slots{nurses,days,shifts}, binary;
param unpreferred_slots{nurses,days,shifts}, binary;

var schedule{nurses, days, shifts}, binary;

var interaction{nurses,nurses,days,shifts},binary;

var sched_preferred{nurses,days,shifts},binary;
var sched_unpreferred{nurses,days,shifts},binary;
var inter_preferred{nurses,nurses,days,shifts},binary;
var inter_unpreferred{nurses,nurses,days,shifts},binary;
var sched_vacation{nurses,days,shifts},binary;

maximize happyness: 
	lambda_PS*sum{n in nurses, d in days, s in shifts}(
    sched_preferred[n,d,s]
    )-
	lambda_US*sum{n in nurses, d in days, s in shifts}(
    sched_unpreferred[n,d,s]
    )+
    lambda_PC*sum{i in nurses,j in nurses, d in days, s in shifts}(
    inter_preferred[i,j,d,s])-
    lambda_UC*sum{i in nurses,j in nurses, d in days, s in shifts}(
    inter_unpreferred[i,j,d,s]
    )
;

# Demand for every shiift is satisfied
subject to demand_shift{d in days, s in shifts}:
    sum{n in nurses} schedule[n, d, s] = demand[d, s];
    
# Respect work hours limit
subject to work_hours_limit{n in nurses}:
    sum{s in shifts, d in days} 24/S*schedule[n, d, s] <= workhours_limit[n];
    
# Every nurse can work at most one shift per day
subject to daily_shift_limit{nurse in nurses, day in days}:
    sum{shift in shifts} schedule[nurse, day, shift] <= 1;
    
# Schedule where a nurse works in the last shift and in the first on the next day is forbidden
subject to give_sleep_time{nurse in nurses, day in {1..(D-1)}}:
    schedule[nurse, day, S] + schedule[nurse, day + 1, 1] <= 1;
    
#Vacations are respected
subject to vacations{nurse in nurses}:
	sum{d in days, s in shifts} sched_vacation[nurse,d,s]=0;

subject to sched_vacation1{n in nurses,d in days,s in shifts}:
	sched_vacation[n,d,s]>=0;
	
subject to sched_vacation2{n in nurses,d in days,s in shifts}:
	sched_vacation[n,d,s]>= schedule[n,d,s]+vacation[d,n]-1;

#interaction 1
subject to interaction_1{i in nurses, j in nurses, d in days, s in shifts}:
	interaction[i,j,d,s]<=schedule[i,d,s];

#interaction 2
subject to interaction_2{i in nurses, j in nurses, d in days, s in shifts}:
	interaction[i,j,d,s]<=schedule[j,d,s];

#interaction 3
subject to interaction_3{i in nurses, j in nurses, d in days, s in shifts}:
	interaction[i,j,d,s]>=schedule[i,d,s]+schedule[j,d,s]-1;

# new variable sched preffered representing multiplication of schedule and preferred_slots
subject to sched_preferred1{n in nurses,d in days,s in shifts}:
	sched_preferred[n,d,s]<=schedule[n,d,s];
	
subject to sched_preferred2{n in nurses,d in days,s in shifts}:
	sched_preferred[n,d,s]<=preferred_slots[n,d,s];

# new variable sched preffered representing multiplication of schedule and unpreferred_slots	
subject to sched_unpreferred1{n in nurses,d in days,s in shifts}:
	sched_unpreferred[n,d,s]>=0;
	
subject to sched_unpreferred2{n in nurses,d in days,s in shifts}:
	sched_unpreferred[n,d,s]>=schedule[n,d,s]+unpreferred_slots[n,d,s]-1;
	
# new variable sched preffered representing multiplication of interaction and preferred_companions
subject to inter_preferred1{i in nurses,j in nurses,d in days,s in shifts}:
	inter_preferred[i,j,d,s]<=interaction[i,j,d,s];
	
subject to inter_preferred2{i in nurses,j in nurses,d in days,s in shifts}:
	inter_preferred[i,j,d,s]<=preferred_companions[i,j];

# new variable sched preffered representing multiplication of interaction and unpreferred_companions
subject to inter_unpreferred1{i in nurses,j in nurses,d in days,s in shifts}:
	inter_unpreferred[i,j,d,s]>=0;
	
subject to inter_unpreferred2{i in nurses,j in nurses,d in days,s in shifts}:
	inter_unpreferred[i,j,d,s]>=interaction[i,j,d,s]+unpreferred_companions[i,j]-1;

