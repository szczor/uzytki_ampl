param S;
param D;
param N;

set shifts := {1..S};
set days := {1..D};
set nurses := {1..N};
set weeks := {0 .. (floor(D/7) - 1)};
set weekdays := {0 .. 6};

param lambda_PC := 1;
param lambda_UC := 1;
param lambda_PS := 1;
param lambda_US := 1;
param lambda_WHS := 100;
param lambda_W := 15;

param demand{days, shifts} >= 0, integer;
param workhours_limit{nurses} > 0, integer;
set vacation within {days, nurses};
set preferred_companions within {nurses, nurses};
set unpreferred_companions within {nurses, nurses};
set preferred_slots within {nurses,days,shifts};
set unpreferred_slots within {nurses,days,shifts};

var schedule{nurses, days, shifts}, binary;

var interaction{nurses,nurses,days,shifts},binary;

var weekend{nurses, weeks}, binary;
# Two variables below are not declared integers, because it prevents fpump heurestic.
var max_weekends_worked;
var min_weekends_worked;

# Binary indicator whether S consecutive shifts starting from given shift 
# on given day are free for given nurse. 
# This assumes that S shifts cover entire day, however length can be arbitrary.
var rest_24h_indicator{nurses, weeks, weekdays, shifts}, binary;
# Maximal allowed value of sum of rest_24h_indicator[n, w, *, *]:
# there are S in each of 7 days; one oth them must be free
param WORKED_24H_LIMIT := 6 * S;

var alpha_min;
var alpha_max;


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
    -lambda_WHS * (alpha_max - alpha_min)
    - lambda_W * (max_weekends_worked - min_weekends_worked)
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
    
# max 6 night shifts per week
subject to night_limit{n in nurses, w in weeks}:
    sum{d in {(7 * w + 1) .. min(7 * (w + 1), D)}} schedule[n, d, S] <= 6;
    
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

# weekend work indicators constraints
subject to weekends_1{n in nurses, w in weeks}:
    weekend[n, w] >= (sum{s in shifts} (schedule[n, 7 * w + 6, s] + schedule[n, 7 * w + 7, s])) / S;
subject to weekends_2{n in nurses, w in weeks}:
    weekend[n, w] <= sum{s in shifts} (schedule[n, 7 * w + 6, s] + schedule[n, 7 * w + 7, s]);
subject to min_weekends_worked_constraint{n in nurses}:
    min_weekends_worked <= sum{w in weeks} weekend[n, w];
subject to max_weekends_worked_constraint{n in nurses}:
    max_weekends_worked >= sum{w in weeks} weekend[n, w];

# alphas with bounds
subject to alpha_min_bounds{n in nurses}:
    sum{d in days, s in shifts} schedule[n, d, s] * 24 / S / workhours_limit[n] >= alpha_min;
subject to alpha_max_bounds{n in nurses}:
    sum{d in days, s in shifts} schedule[n, d, s] * 24 / S / workhours_limit[n] <= alpha_max;
    
# Define rest_24h_indicator using schedule; for the last day of week this must be defined separately
subject to define_rest_24h_indicator{n in nurses, w in weeks, wd in {0 .. 5}, s in shifts}:
    rest_24h_indicator[n, w, wd, s] >= 0.999 / S * sum{i in {0 .. (S-1)}} schedule[n, 1 + 7 * w + wd + ((s - 1 + i) div S), 1 + ((s - 1 + i) mod S)];
subject to define_rest_24h_indicator_last{n in nurses, w in weeks}:
    rest_24h_indicator[n, w, 6, 1] >= 0.999 / S * sum{i in shifts} schedule[n, 1 + 7 * w + 6, i];
# Now use it to ensure nurses have contiguous 24h rest time
subject to contiguous_24h_break{n in nurses, w in weeks}:
    sum{wd in weekdays, s in shifts} rest_24h_indicator[n, w, wd, s] <= WORKED_24H_LIMIT;
