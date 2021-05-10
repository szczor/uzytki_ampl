param S;
param D;
param N;

set shifts := {1..S};
set days := {1..D};
set nurses := {1..N};

param demand {days, shifts}>=0;

param not_preferred{nurses}>=0;

param preferred{nurses}>=0;

var schedule{nurses, days, shifts}, binary;

minimize cost: 1;

#s.t. working_days{n in nurses}:
#sum{i in days, j in shifts}(schedule[n,i,j]) <= 3;

s.t. demand_shift{i in days, j in shifts}:
sum{n in nurses}(schedule[n,i,j]) = (demand[i,j]);

s.t. not_preferred_companions{i in days, j in shifts}:
sum{n in nurses}(schedule[n,i,j]*schedule[not_preferred[n],i,j])=0;

#this works assuming each nurse has one companion she wants to work with
s.t. preferred_companions{i in days, j in shifts}:
sum{n in nurses}(schedule[n,i,j]*schedule[preferred[n],i,j])=N;

# Every nurse can work at most one shift per day
subject to max_one_shift_daily{nurse in nurses, day in days}:
    sum{shift in shifts} schedule[nurse, day, shift] <= 1;
    
# Schedule where a nurse works in the last shift and in the first on the next day is forbidden
subject to give_sleep_time{nurse in nurses, day in {1..(D-1)}}:
    schedule[nurse, day, S] + schedule[nurse, day + 1, 1] <= 1;
