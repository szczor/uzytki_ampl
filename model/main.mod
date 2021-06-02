param pNumberOfShifts;
param pNumberOfDays;
param pNumberOfNurses;

param pShiftLength := 24/pNumberOfShifts;
param pMaxNightShifts := 6;

set sShifts := {1..pNumberOfShifts};
set sDays := {1..pNumberOfDays};
set sNurses := {1..pNumberOfNurses};
set sWeeks := {1..(pNumberOfDays/7)};

param pLambdaPC := 1;
param pLambdaUC := 1;
param pLambdaPS := 1;
param pLambdaUS := 1;
param pLambdaWHS := 100;

param pDemand{sDays, sShifts} >= 0, integer;
param pWorkhoursLimit{sNurses} > 0, integer;

set sVacations within {sDays, sNurses};
set sPreferredCompanions within {sNurses, sNurses};
set sUnpreferredCompanions within {sNurses, sNurses};
set sPreferredSlots within {sNurses, sDays, sShifts};
set sUnpreferredSlots within {sNurses, sDays, sShifts};

var vSchedule{sNurses, sDays, sShifts}, binary;

var vInteraction{sNurses, sNurses, sDays, sShifts}, binary;

var vWeekend{sNurses, sWeeks}, binary;

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
    -pLambdaWHS * (vAlphaMax - vAlphaMin)
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
    sum{d in {(7 * (w-1) + 1) .. min(7 * w , pNumberOfDays)}} vSchedule[n, d, pNumberOfShifts] <= pMaxNightShifts;
    
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
    vWeekend[n, w] >= (sum{s in sShifts} (vSchedule[n, 7*(w-1) + 6, s] + vSchedule[n, 7*(w-1) + 7, s])) / pNumberOfShifts;

subject to cWeekends2{n in sNurses, w in sWeeks}:
    vWeekend[n, w] <= sum{s in sShifts} (vSchedule[n, 7*(w-1) + 6, s] + vSchedule[n, 7*(w-1) + 7, s]);

# alphas with bounds
subject to cAlphaMin{n in sNurses}:
    sum{d in sDays, s in sShifts} vSchedule[n, d, s] * pShiftLength / pWorkhoursLimit[n] >= vAlphaMin;
subject to cAlphaMax{n in sNurses}:
    sum{d in sDays, s in sShifts} vSchedule[n, d, s] * pShiftLength / pWorkhoursLimit[n] <= vAlphaMax;
