param S;
param D;
param N;

set shifts := {1..S};
set days := {1..D};
set nurses := {1..N};

param liked_coworker_reward := 1;
param disliked_coworker_penalty := 1;

param demand{days, shifts} >= 0, integer;
param workhours_limit{nurses} > 0;
param vacation{days, nurses} >= 0, binary;
param liked{nurses, nurses}, integer;

var schedule{nurses, days, shifts}, binary;


maximize happyness: 
    sum{i in nurses, j in nurses, d in days, s in shifts} (
        (liked_coworker_reward * (1 + liked[i, j]) / 2  +  disliked_coworker_penalty * (1 - liked[i, j]) / 2)
        * schedule[i, d, s] * schedule[j, d, s] * liked[i, j]
    )
;


# Respect work hours limit
subject to work_hours_limit{n in nurses}:
    sum{s in shifts, d in days} schedule[n, d, s] <= workhours_limit[n];

# Demand for every shiift is satisfied
subject to demand_shift{d in days, s in shifts}:
    sum{n in nurses} schedule[n, d, s] >= demand[d, s];
    
# Every nurse can work at most one shift per day and vacation requests are respected
subject to daily_shift_limit{nurse in nurses, day in days}:
    sum{shift in shifts} schedule[nurse, day, shift] <= 1 - vacation[day, nurse];
    
# Schedule where a nurse works in the last shift and in the first on the next day is forbidden
subject to give_sleep_time{nurse in nurses, day in {1..(D-1)}}:
    schedule[nurse, day, S] + schedule[nurse, day + 1, 1] <= 1;
