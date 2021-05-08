# Nurse Scheduling Problem 

## Instance file

The .csv instance files contain information about working hours and nurses preferences. Each file consists of following sections:

	1. demand - each row contains number of a day followed by demand for nurses on each shift
	2. workhours - each row contains nurse id followed by maximum number of working hours
	3. vacation - each row contains nurse id followed by number of vacation day
	4. preferred_companions - each row contains pair of nurses id; 1;7; means that nurse 1 prefers to work with nurse 7
	5. unpreferred_companions - each row contains pair of nurses id; 1;7; means that nurse 1 prefers not to work with nurse 7
	6. preferred_shifts - each row contains nurse id followed by number of preferred day and shift
	7. unpreferred_shifts - each row contains nurse id followed by number of unpreferred day and shift
	
The csv file should be transformed into dat file.
  
## Runing with gmpl

To run optimization by gmpl, navigate to directory containing glpsol and execute following command in the command line:

```
glpsol -m <model_file>.mod -d <model_file>.dat -o <model_file>.sol
```

The result will be written to file specified by -o option.


## Running on [neos server](https://ampl.com/try-ampl/run-ampl-on-neos/) 

	1. Go to [Gurobi](https://neos-server.org/neos/solvers/milp:Gurobi/AMPL.html) or other optimizer site.
	2. Upload model, data and command file.
	3. Click 'Submit to NEOS' button and wait for results.