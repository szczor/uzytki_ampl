# Nurse Rostering

The model itself is in `model/` directore. In the repo there are also several utility scripts:

- `csv2dat.py` that converts input from a number of CSV files into single `.dat` file suitable for model `model/main.mod`.
- `visualization.py` that presents the solution in a human readable way.

The model is linear and it seems to work with `glpsol`.


## Running the model

First to generate data from CSV files you can use `csv2dat.py` script (se following section for more info):

```sh
python csv2dat.py example_data/example.ini test.dat
```

This should generate `test.dat` with input suitable for the model. You can run it with `glpsol` (currently it seems to take 
several minutes for `glpsol` to find a solution; however it then stucks for omptimizing it for at least very long time):

```sh
glpsol -m model/main.mod -d test.dat -o solution.sol --tmlim 1800
```

Or from `ampl` CLI (assuming `model.mod` and `test.dat` are copied to the working directory):

```
option solver cplex;
model model.mod;
data testmini.dat;
solve;
```


## Visualizing the solution

Assuming that you have a `glpsol`–generated solution in file `solution.sol` you can generate visualisation like this:

```
python visualise_schedule.py solution.sol output_name
```

This should generate visualizations of 7-day schedules in a form output_name_week_i.png in a directory `wykresy/`. For example if your data contains
28 days, it will generate 4 plots where each plot represents one week. If your data is shorter than one week, it will generate one plot.


## Converting input from CSV files

CSV files are converted to `.dat` input for our model by `csv2dat.py` script. Foor convenience the script uses a config file with 
a list of files to process (and several other options). When run, it expects one or two command line parameters:

- The first (required) is path to the config file describing which CAV files to use. For more info, check out example of cuch 
  file: `example_data/example.ini` (every option is commented there). Keep in mind that relative paths to CSV files defined in 
  that file are taken relative to the location of the INI file.
- The second (optional) parameter is the desired path to output file. If present it will override the option `FileName` from 
  `Output` section (otherwise this option must be set in the INI file). The relative path to output is treated as relative to the 
  directory from which the script is invoked.

An example invocation that produces `test.dat` from sample data provided in `example_data/` directory (that were given to us by 
F33) would be:

```sh
python3 csv2dat.py example_data/example.ini test.dat
```
