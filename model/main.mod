param pNumberOfShifts;
param pNumberOfDays;
param pNumberOfNurses;

param pShiftLength := 24/pNumberOfShifts;
param pMaxNightShifts := 6;

set sShifts := {1..pNumberOfShifts};
set sDays := {1..pNumberOfDays};
set sNurses := {1..pNumberOfNurses};
set sWeeks := {0 .. (floor(pNumberOfDays/7) - 1)};
set sWeekdays := {0 .. 6};

param pLambdaPC := 1;
param pLambdaUC := 1;
param pLambdaPS := 1;
param pLambdaUS := 1;
param pLambdaWHS := 100;
param pLambdaW := 50;

param pDemand{sDays, sShifts} >= 0, integer;
param pWorkhoursLimit{sNurses} > 0, integer;

set sVacations within {sDays, sNurses};
set sPreferredCompanions within {sNurses, sNurses};
set sUnpreferredCompanions within {sNurses, sNurses};
set sPreferredSlots within {sNurses, sDays, sShifts};
set sUnpreferredSlots within {sNurses, sDays, sShifts};

# Binary indicator whether S consecutive shifts starting from given shift 
# on given day are free for given nurse. 
# This assumes that S shifts cover entire day, however length can be arbitrary.
var vRest24hIndicator{sNurses, sWeeks, sWeekdays, sShifts}, binary;
# Maximal allowed value of sum of vRest24hIndicator[n, w, *, *]:
# there are S in each of 7 days; one oth them must be free
param pMaxDaysWithout24BreakInWeek := 6 * pNumberOfShifts;

var vSchedule{sNurses, sDays, sShifts}, binary;

var vInteraction{sNurses, sNurses, sDays, sShifts}, binary;

var vWeekend{sNurses, sWeeks}, binary;
# Two variables below are not declared integers, because it prevents fpump heurestic.
var vMaxWeekendsWorked;
var vMinWeekendsWorked;

var vAlphaMin;
var vAlphaMax;

maximize happyness: 
	pLambdaPS*sum{(n, d, s) in sPreferredSlots}(
    vSchedule[n,d,s]
    )-
	pLambdaUS*sum{(n, d, s) in sUnpreferredSlots}(
    vSchedule[n,d,s]
    )+
    pLambdaPC*sum{(i, j) in sPreferredCompanions, d in sDays, s in sShifts}(
    vInteraction[i,j,d,s]
    )-
    pLambdaUC*sum{(i, j) in sUnpreferredCompanions, d in sDays, s in sShifts}(
    vInteraction[i,j,d,s]
    )
    - pLambdaWHS * (vAlphaMax - vAlphaMin)
    - pLambdaW * (vMaxWeekendsWorked - vMinWeekendsWorked)
;

# Demand for every shiift is satisfied
subject to cDemandShift{d in sDays, s in sShifts}:
    sum{n in sNurses} vSchedule[n, d, s] = pDemand[d, s];
    
# Respect work hours limit
subject to cWorkHoursLimit{n in sNurses}:
    sum{s in sShifts, d in sDays} pShiftLength*vSchedule[n, d, s] <= pWorkhoursLimit[n];
    
# Every nurse can work at most one shift per day
subject to cDailyShiftLimit{nurse in sNurses, day in sDays}:
    sum{shift in sShifts} vSchedule[nurse, day, shift] <= 1;
    
# respect night shifts per week limit
subject to cNightLimit{n in sNurses, w in sWeeks}:
    sum{d in {(7 * w + 1) .. min(7 * (w + 1), pNumberOfDays)}} vSchedule[n, d, pNumberOfShifts] <= pMaxNightShifts;
    
# Schedule where a nurse works in the last shift and in the first on the next day is forbidden
subject to cGiveSleepTime{nurse in sNurses, day in {1..(pNumberOfDays-1)}}:
    vSchedule[nurse, day, pNumberOfShifts] + vSchedule[nurse, day + 1, 1] <= 1;
    
#Vacations are respected
subject to cVacations:
	sum{(d,n) in sVacations, s in sShifts} vSchedule[n,d,s] = 0;

#interaction 1
subject to cInteraction1{i in sNurses, j in sNurses, d in sDays, s in sShifts}:
	vInteraction[i,j,d,s]<=vSchedule[i,d,s];

#interaction 2
subject to cInteraction2{i in sNurses, j in sNurses, d in sDays, s in sShifts}:
	vInteraction[i,j,d,s]<=vSchedule[j,d,s];

#interaction 3
subject to cInteraction3{i in sNurses, j in sNurses, d in sDays, s in sShifts}:
	vInteraction[i,j,d,s]>=vSchedule[i,d,s]+vSchedule[j,d,s]-1;

# weekend work indicators constraints
subject to cWeekends1{n in sNurses, w in sWeeks}:
    vWeekend[n, w] >= (sum{s in sShifts} (vSchedule[n, 7*w + 6, s] + vSchedule[n, 7*w + 7, s])) / pNumberOfShifts;
subject to cWeekends2{n in sNurses, w in sWeeks}:
    vWeekend[n, w] <= sum{s in sShifts} (vSchedule[n, 7*w + 6, s] + vSchedule[n, 7*w + 7, s]);
subject to cMinWeekendsWorked{n in sNurses}:
    vMinWeekendsWorked <= sum{w in sWeeks} vWeekend[n, w];
subject to cMaxWeekendsWorked{n in sNurses}:
    vMaxWeekendsWorked >= sum{w in sWeeks} vWeekend[n, w];

# alphas with bounds
subject to cAlphaMin{n in sNurses}:
    sum{d in sDays, s in sShifts} vSchedule[n, d, s] * pShiftLength / pWorkhoursLimit[n] >= vAlphaMin;
subject to cAlphaMax{n in sNurses}:
    sum{d in sDays, s in sShifts} vSchedule[n, d, s] * pShiftLength / pWorkhoursLimit[n] <= vAlphaMax;

# Define vRest24hIndicator using schedule; for the last day of week this must be defined separately
subject to cDefineRest24hIndicator{n in sNurses, w in sWeeks, wd in {0 .. 5}, s in sShifts}:
    vRest24hIndicator[n, w, wd, s] >= 0.999 / pNumberOfShifts * sum{i in {0 .. (pNumberOfShifts-1)}} vSchedule[n, 1 + 7 * w + wd + ((s - 1 + i) div pNumberOfShifts), 1 + ((s - 1 + i) mod pNumberOfShifts)];
subject to cDefineRest24hIndicatorLastDay{n in sNurses, w in sWeeks}:
    vRest24hIndicator[n, w, 6, 1] >= 0.999 / pNumberOfShifts * sum{i in sShifts} vSchedule[n, 1 + 7 * w + 6, i];
# Now use it to ensure nurses have contiguous 24h rest time
subject to cContiguous24hBreak{n in sNurses, w in sWeeks}:
    sum{wd in sWeekdays, s in sShifts} vRest24hIndicator[n, w, wd, s] <= WORKED_24H_LIMIT;