The `example.ini` file contains sample configuration for `csv2dat.py` script that can be used to generate `.dat` file from data 
in this directory.

The .csv instance files contain information about working hours and nurses preferences. Each file consists of following sections:

	1. demand - each row contains number of a day followed by demand for nurses on each shift
	2. workhours - each row contains nurse id followed by maximum number of working hours
	3. vacation - each row contains nurse id followed by number of vacation day
	4. preferred_companions - each row contains pair of nurses id; 1;7; means that nurse 1 prefers to work with nurse 7
	5. unpreferred_companions - each row contains pair of nurses id; 1;7; means that nurse 1 prefers not to work with nurse 7
	6. preferred_shifts - each row contains nurse id followed by number of preferred day and shift
	7. unpreferred_shifts - each row contains nurse id followed by number of unpreferred day and shift
