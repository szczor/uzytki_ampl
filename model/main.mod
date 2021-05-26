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
param workhours_limit{nurses} > 0, integer;
set vacation within {days, nurses};
set preferred_companions within {nurses, nurses};
set unpreferred_companions within {nurses, nurses};
set preferred_slots within {nurses,days,shifts};
set unpreferred_slots within {nurses,days,shifts};

var schedule{nurses, days, shifts}, binary;

var interaction{nurses,nurses,days,shifts},binary;


maximize happyness: 
	lambda_PS*sum{(n, d, s) in preferred_slots}(
    schedule[n,d,s]
    )-
	lambda_US*sum{(n, d, s) in unpreferred_slots}(
    schedule[n,d,s]
    )+
    lambda_PC*sum{(i, j) in preferred_companions, d in days, s in shifts}(
    interaction[i,j,d,s]
    )-
    lambda_UC*sum{(i, j) in unpreferred_companions, d in days, s in shifts}(
    interaction[i,j,d,s]
    )
;

# Demand for every shiift is satisfied
subject to demand_shift{d in days, s in shifts}:
    sum{n in nurses} schedule[n, d, s] = demand[d, s];
    
# Respect work hours limit
# subject to work_hours_limit{n in nurses}:
    # sum{s in shifts, d in days} 24/S*schedule[n, d, s] <= workhours_limit[n];
    
# Every nurse can work at most one shift per day
subject to daily_shift_limit{nurse in nurses, day in days}:
    sum{shift in shifts} schedule[nurse, day, shift] <= 1;
    
# Schedule where a nurse works in the last shift and in the first on the next day is forbidden
subject to give_sleep_time{nurse in nurses, day in {1..(D-1)}}:
    schedule[nurse, day, S] + schedule[nurse, day + 1, 1] <= 1;
    
#Vacations are respected
subject to vacations:
	sum{(d,n) in vacation, s in shifts} schedule[n,d,s] = 0;

#interaction 1
subject to interaction_1{i in nurses, j in nurses, d in days, s in shifts}:
	interaction[i,j,d,s]<=schedule[i,d,s];

#interaction 2
subject to interaction_2{i in nurses, j in nurses, d in days, s in shifts}:
	interaction[i,j,d,s]<=schedule[j,d,s];

#interaction 3
subject to interaction_3{i in nurses, j in nurses, d in days, s in shifts}:
	interaction[i,j,d,s]>=schedule[i,d,s]+schedule[j,d,s]-1;
