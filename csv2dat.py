import numpy as np
import csv
import configparser
import sys
import os.path
import logging


class DatWriter:
    def __init__(self, file_name):
        self._file = open(file_name, "w")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.close()

    def close(self):
        self._file.close()

    def write_param(self, name, value):
        if isinstance(value, np.ndarray):
            if len(value.shape) == 1:
                self._write_array_1d(name, value)
            elif len(value.shape) == 2:
                self._write_array_2d(name, value)
            elif len(value.shape) == 3:
                self._write_array_3d(name, value)
            else:
                raise ValueError("unsupported ndarray dimmention")
        else:
            self._file.write(f"param {name} := {value};\n")
    
    def _write_array_1d(self, name, array):
        f = self._file
        f.write(f"param {name} :=")
        for i in range(array.shape[0]):
            f.write(f"\n\t{i+1}\t{array[i]}")
        f.write(";\n")

    def _write_array_2d(self, name, array):
        self._file.write(f"param {name}:\n\t\t")
        self._write_matrix(array)
        self._file.write(";\n")

    def _write_array_3d(self, name, array):
        f = self._file
        f.write(f"param {name} :=")
        for i in range(array.shape[0]):
            f.write(f"\n\t[{i + 1}, *, *]:\t")
            self._write_matrix(array[i, :, :])
        f.write(";\n")

    def _write_matrix(self, subarray):
        f = self._file
        for j in range(subarray.shape[1]):
            f.write(f"{j+1}\t")
        f.write(":=")
        for i in range(subarray.shape[0]):
            f.write(f"\n\t{i+1}")
            for j in range(subarray.shape[1]):
                if subarray.dtype == bool:
                    f.write(f"\t{1 if subarray[i, j] else 0}")
                else:
                    f.write(f"\t{subarray[i, j]}")


class ModelDTO:
    def __init__(self, n_nurses, n_days, n_shifts):
        self.n = n_nurses
        self.d = n_days
        self.s = n_shifts
        self.work_hours_limit = np.zeros(n_nurses)
        self.demand = np.zeros((n_days, n_shifts), dtype=int)
        self.preferred_shifts = np.zeros((n_nurses, n_days, n_shifts), dtype=bool)
        self.non_preferred_shifts = np.zeros((n_nurses, n_days, n_shifts), dtype=bool)
        self.vacation = np.zeros((n_days, n_nurses), dtype=bool)
        self.liked_coworkers = np.zeros((n_nurses, n_nurses), dtype=bool)
        self.disliked_coworkers = np.zeros((n_nurses, n_nurses), dtype=bool)


def detect_size_params(model_input_files):
    n, d, s = 0, 0, 0
    for row in csv.reader(open(model_input_files["WorkHoursLimits"])):
        n = max(n, int(float(row[0])))
    for row in csv.reader(open(model_input_files["Demand"])):
        d = max(d, int(float(row[0])))
        s = max(s, len(row) - 1)
    return n, d, s


def read_model(options, target: ModelDTO, logger: logging.Logger):
    def convert_int(value_desc, str_value):
        val = float(str_value)
        if val != int(val):
            logger.warning(f"expected {value_desc} should be integer, but has fractional value {val}")
        return int(val)
    def open_csv(name_in_model):
        return csv.reader(open(options["Files"][name_in_model]))

    # PARAM: work_hours_limit
    for row in open_csv("WorkHoursLimits"):
        nurse = convert_int("nurse id", row[0]) - 1
        if nurse >= target.n:
            logger.error(f"nurse index {nurse + 1} is out of range")
            continue
        limit = float(row[0])
        if target.work_hours_limit[nurse] != 0:
            logger.warning(f"nurse {nurse + 1} has work hours defined twice")
        target.work_hours_limit[nurse] = limit

    # PARAM: demand
    isset = [False] * target.d
    for row in open_csv("Demand"):
        day = convert_int("day number", row[0]) - 1
        if day >= target.d:
            logger.error(f"day index {day + 1} is out of range")
            continue
        if len(row) - 1 != target.s:
            logger.warning(f"day {day + 1} has invalid number of values as demand param")
        if isset[day]:
            logger.warning(f"day {day + 1} has demand defined twice")
        isset[day] = True
        for s in range(min(target.s, len(row) - 1)):
            target.demand[day, s] = float(row[s + 1])

    # PARAM: preferred_shifts
    for row in open_csv("PreferredShifts"):
        nurse = convert_int("nurse id", row[0]) - 1
        day = convert_int("day number", row[1]) - 1
        shift = convert_int("shift number", row[2]) - 1
        target.preferred_shifts[nurse, day, shift] = True

    # PARAM: preferred_shifts
    for row in open_csv("NonPreferredShifts"):
        nurse = convert_int("nurse id", row[0]) - 1
        day = convert_int("day number", row[1]) - 1
        shift = convert_int("shift number", row[2]) - 1
        target.non_preferred_shifts[nurse, day, shift] = True

    # PARAM: vacation
    for row in open_csv("Vacation"):
        nurse = convert_int("nurse id", row[0]) - 1
        for day in row[1:]:
            day = convert_int("day number", day)
            if day > 0:
                target.vacation[day - 1, nurse] = True

    # PARAM: preferred_companions
    for row in open_csv("LikedCoworkers"):
        nurse1 = convert_int("nurse id", row[0]) - 1
        nurse2 = convert_int("nurse id", row[1]) - 1
        target.liked_coworkers[nurse1, nurse2] = True

    # PARAM: unpreferred_companions
    for row in open_csv("DislikedCoworkers"):
        nurse1 = convert_int("nurse id", row[0]) - 1
        nurse2 = convert_int("nurse id", row[1]) - 1
        target.disliked_coworkers[nurse1, nurse2] = True


def write_model(output_file, data: ModelDTO, logger: logging.Logger):
    with DatWriter(output_file) as dat:
        dat.write_param("N", data.n)
        dat.write_param("D", data.d)
        dat.write_param("S", data.s)
        dat.write_param("workhours_limit", data.work_hours_limit)
        dat.write_param("demand", data.demand)
        dat.write_param("preferred_slots", data.preferred_shifts)
        dat.write_param("unpreferred_slots", data.non_preferred_shifts)
        dat.write_param("vacation", data.vacation)
        dat.write_param("preferred_companions", data.liked_coworkers)
        dat.write_param("unpreferred_companions", data.disliked_coworkers)


def main(argv):
    if len(argv) < 2:
        print(f"Usage: python {argv[0]} path/to/model_description.ini [path/to/output.dat]")
        return 1
    
    config = configparser.ConfigParser()
    config.read(argv[1])

    # translate config-relative paths
    rel_dir = os.path.dirname(argv[1])
    for file_key in config["Files"]:
        if not os.path.isabs(config["Files"][file_key]):
            config["Files"][file_key] = os.path.join(rel_dir, config["Files"][file_key])

    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s] [%(levelname)s]  %(message)s")
    logger = logging.getLogger()
    n, d, s = 0, 0, 0
    if config["Params"]["Autodetect"] == "Yes":
        n, d, s = detect_size_params(config["Files"])
        logger.info(f"Detected problem size: {n} nurses, {d} days, {s} shifts")
    else:
        n = int(config["Params"]["NumberOfNurses"])
        d = int(config["Params"]["NumberOfDays"])
        s = int(config["Params"]["NumberOfShifts"])
    model = ModelDTO(n, d, s)
    read_model(config, model, logger)
    write_model(config["Output"]["FileName"] if len(argv) == 2 else argv[2], model, logger)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
