import statistics
import time
import ast
from benchmarks import *
from verification_algorithms import antichain_optimization_algorithm, counterexample_based_algorithm

try:
    os.mkdir('random_automata')
except FileExistsError:
    pass

try:
    os.mkdir('benchmarks_results')
except FileExistsError:
    pass


def run_benchmark(benchmark_type, save_file, parameters, nbr_points, range_start, range_end, range_step):
    """
    Runs several kinds of benchmarks. Given a set of fixed parameters in parameters, several values of some other
    variable are considered from range_start to range_end with a step of range_step. Given the parameters and a value
    for the variable in the range, the running time for both algorithms is evaluated nbr_points times. Consistency of
    the results from the algorithms is compared to the expected result given the benchmark being considered. The result
    of the benchmarks are printed as they are obtained and saved to the file with path save_file. We consider three
    types of benchmarks:

    - Random benchmarks:  when benchmark_type == "random", we evaluate the running time of the algorithms on random
    automata when increasing the number of objectives for Player 1 (with each function having 4 priorities). This number
    of objectives is considered in range(range_start, range_end, range_step). Given a number of objectives, both
    algorithms are evaluated on nbr_points random automata which are generated by the random_automaton function in
    benchmarks. These automata are generated (or retrieved from the random_automata folder if they already exist with
    the expected parameters) using the parameters in parameters. This parameters variables is expected to follow this
    format: [nbr_vertices, density, proba_even_general, proba_even_0, positivity], thus following the
    signature of the random_automaton function (without the number of objectives). Notice that we do not specify a value
    for name in that function, this is done by this run_benchmark function which appends which of the nbr_points
    automaton the current automaton corresponds to.

    - Intersection benchmarks for vertices:  when benchmark_type == "intersection_vertices", we evaluate the running
    time of the algorithms on the intersection example when considering the number of copies of the automaton (see
    documentation for intersection_example in benchmarks) to be in range(range_start, range_end, range_step). The
    parameters variable is expected to follow the format: [positivity] (True if the instance should be positive and
    False if it should be negative).

    - Intersection benchmarks for objectives:  when benchmark_type == "intersection_objectives", we evaluate the running
    time of the algorithms on the intersection example when considering the number of copies of the automaton (see
    documentation for intersection_example_objective_increase in benchmarks) to be in range(range_start, range_end,
    range_step), thus also increasing the number of objectives for Player 1. The parameters variable is expected to
    follow the format: [positivity] (True if the instance should be positive and False if it should be negative).

    The results of the benchmarks are saved in text format to save_file and are meant to be readable and parsable. They
    highlight the value of several statistics on the benchmarks as well as running times for each of the nbr_points
    times they were evaluated, for each set of parameter, and the mean value of those statistics and running times are
    also provided.

    :param benchmark_type: should be in ["random", "intersection_vertices", "intersection_objectives"].
    :param save_file: path to file containing benchmarks results.
    :param parameters: parameters to generate the automata in the benchmarks (see above for expected format).
    :param nbr_points: number of times the algorithms are evaluated given a set of parameters.
    :param range_start: start of the range for the variable being evaluated.
    :param range_end: end of the range for the variable being evaluated.
    :param range_step: step of the range for the variable being evaluated.
    """
    for i in list(range(range_start, range_end, range_step)):

        # lists to hold data for each of the nbr_points automata
        temp_antichain_sizes = []
        temp_nbr_payoffs_losing_player_0 = []
        temp_nbr_payoffs_realizable = []

        temp_counterexample_antichain_sizes = []
        temp_counterexample_nbr_calls = []
        temp_counterexample_nbr_calls_exists = []
        temp_counterexample_mean_time_calls_exists = []
        temp_counterexample_nbr_calls_dominated = []
        temp_counterexample_mean_time_calls_dominated = []

        temp_antichain_optimization_antichain_sizes = []
        temp_antichain_optimization_nbr_calls = []
        temp_antichain_optimization_nbr_calls1 = []
        temp_antichain_optimization_mean_time_calls1 = []
        temp_antichain_optimization_nbr_calls2 = []
        temp_antichain_optimization_mean_time_calls2 = []

        counterexample_times_process = []
        antichain_optimization_times_process = []

        counterexample_times_perf_counter = []
        antichain_optimization_times_perf_counter = []

        counterexample_times = []
        antichain_optimization_times = []

        for j in range(1, nbr_points + 1):

            if benchmark_type == "random":
                print("-------------------- trying to generate the " + str(j) + "th automaton with " + str(i)
                      + "functions --------------------")

                stats, aut, nbr, colors = random_automaton(parameters[0], parameters[1], i,  parameters[2],
                                                           parameters[3], parameters[4], str(j))
                gen_positivity = parameters[4]

            elif benchmark_type == "intersection_vertices":
                stats, aut, nbr, colors = intersection_example(i, negative_instance=not parameters[0])
                gen_positivity = parameters[0]

            elif benchmark_type == "intersection_objectives":
                stats, aut, nbr, colors = intersection_example_objective_increase(i,
                                                                                  negative_instance=not parameters[0])
                gen_positivity = parameters[0]

            else:
                class BenchmarkNotSupportedError(Exception):
                    pass

                raise BenchmarkNotSupportedError("This benchmark type is not supported.")

            temp_antichain_sizes.append(stats[0])
            temp_nbr_payoffs_losing_player_0.append(stats[1])
            temp_nbr_payoffs_realizable.append(stats[2])

            temp_counterexample_antichain_sizes.append(stats[3])
            temp_counterexample_nbr_calls_exists.append(stats[4][0])
            temp_counterexample_mean_time_calls_exists.append(float("%.3f" % statistics.mean(stats[4][1])))
            temp_counterexample_nbr_calls_dominated.append(stats[5][0])
            temp_counterexample_mean_time_calls_dominated.append(float("%.3f" % statistics.mean(stats[5][1])))
            temp_counterexample_nbr_calls.append(stats[4][0] + stats[5][0])

            temp_antichain_optimization_antichain_sizes.append(stats[6])
            temp_antichain_optimization_nbr_calls1.append(stats[7][0])
            temp_antichain_optimization_mean_time_calls1.append(float("%.3f" % statistics.mean(stats[7][1])))
            temp_antichain_optimization_nbr_calls2.append(stats[8][0])
            temp_antichain_optimization_mean_time_calls2.append(float("%.3f" % statistics.mean(stats[8][1])))
            temp_antichain_optimization_nbr_calls.append(stats[7][0] + stats[8][0])

            print(" ----- computing counterexample algorithm time -----")

            start_time_process = time.process_time()
            start_time_perf = time.perf_counter()
            start = time.time()

            positivity = counterexample_based_algorithm(aut, nbr, colors)

            end_time_process = time.process_time()
            end_time_perf = time.perf_counter()
            end = time.time()

            assert positivity == gen_positivity

            counterexample_times_process.append(float('%.3f' % (end_time_process - start_time_process)))
            counterexample_times_perf_counter.append(float('%.3f' % (end_time_perf - start_time_perf)))
            counterexample_times.append(float('%.3f' % (end - start)))

            print(" ----- computing antichain optimization time -----")

            start_time_process = time.process_time()
            start_time_perf = time.perf_counter()
            start = time.time()

            positivity = antichain_optimization_algorithm(aut, nbr, colors, is_payoff_realizable)

            end_time_process = time.process_time()
            end_time_perf = time.perf_counter()
            end = time.time()

            assert positivity == gen_positivity

            antichain_optimization_times_process.append(float('%.3f' % (end_time_process - start_time_process)))
            antichain_optimization_times_perf_counter.append(float('%.3f' % (end_time_perf - start_time_perf)))
            antichain_optimization_times.append(float('%.3f' % (end - start)))

            print("Antichain sizes " + str(temp_antichain_sizes))
            print("Number of payoffs losing " + str(temp_nbr_payoffs_losing_player_0))
            print("Number of payoffs realizable " + str(temp_nbr_payoffs_realizable))

            print("CE antichain sizes " + str(temp_counterexample_antichain_sizes))
            print("CE exists calls " + str(temp_counterexample_nbr_calls_exists))
            print("CE exists calls times " + str(temp_counterexample_mean_time_calls_exists))
            print("CE dominated calls " + str(temp_counterexample_nbr_calls_dominated))
            print("CE dominated calls times " + str(temp_counterexample_mean_time_calls_dominated))
            print("CE total nbr calls " + str(temp_counterexample_nbr_calls))

            print("CE times process " + str(counterexample_times_process))
            print("CE times perf " + str(counterexample_times_perf_counter))

            print("AO antichain sizes " + str(temp_antichain_optimization_antichain_sizes))
            print("AO call1 calls " + str(temp_antichain_optimization_nbr_calls1))
            print("AO call1 calls times " + str(temp_antichain_optimization_mean_time_calls1))
            print("AO call2 calls " + str(temp_antichain_optimization_nbr_calls2))
            print("AO call2 calls times " + str(temp_antichain_optimization_mean_time_calls2))
            print("AO total nbr calls " + str(temp_antichain_optimization_nbr_calls))

            print("AO times process " + str(antichain_optimization_times_process))
            print("AO times perf " + str(antichain_optimization_times_perf_counter))

        f = open(save_file, "a")

        f.write("Variable value used " + str(i) + "\n")
        f.write("Parameters " + str(parameters) + "\n")
        f.write("Number of objectives " + str(nbr) + "\n")

        f.write("Antichain sizes " + str(temp_antichain_sizes) + "\n")
        f.write("Number of payoffs losing " + str(temp_nbr_payoffs_losing_player_0) + "\n")
        f.write("Number of payoffs realizable " + str(temp_nbr_payoffs_realizable) + "\n")

        f.write("CE antichain sizes " + str(temp_counterexample_antichain_sizes) + "\n")
        f.write("CE exists calls " + str(temp_counterexample_nbr_calls_exists) + "\n")
        f.write("CE exists calls times " + str(temp_counterexample_mean_time_calls_exists) + "\n")
        f.write("CE dominated calls " + str(temp_counterexample_nbr_calls_dominated) + "\n")
        f.write("CE dominated calls times " + str(temp_counterexample_mean_time_calls_dominated) + "\n")
        f.write("CE total nbr calls " + str(temp_counterexample_nbr_calls) + "\n")

        f.write("CE times process " + str(counterexample_times_process) + "\n")
        f.write("CE times perf " + str(counterexample_times_perf_counter) + "\n")
        f.write("CE times " + str(counterexample_times) + "\n")

        f.write("AO antichain sizes " + str(temp_antichain_optimization_antichain_sizes) + "\n")
        f.write("AO call1 calls " + str(temp_antichain_optimization_nbr_calls1) + "\n")
        f.write("AO call1 calls times " + str(temp_antichain_optimization_mean_time_calls1) + "\n")
        f.write("AO call2 calls " + str(temp_antichain_optimization_nbr_calls2) + "\n")
        f.write("AO call2 calls times " + str(temp_antichain_optimization_mean_time_calls2) + "\n")
        f.write("AO total nbr calls " + str(temp_antichain_optimization_nbr_calls) + "\n")

        f.write("AO times process " + str(antichain_optimization_times_process) + "\n")
        f.write("AO times perf " + str(antichain_optimization_times_perf_counter) + "\n")
        f.write("AO times " + str(antichain_optimization_times) + "\n")

        f.write("Mean running time CE " + "%.3f" % statistics.mean(counterexample_times_process) + ", ")
        f.write("%.3f" % statistics.mean(counterexample_times_perf_counter) + ", ")
        f.write("%.3f" % statistics.mean(counterexample_times) + "\n")

        f.write("Mean running time AO " + "%.3f" % statistics.mean(antichain_optimization_times_process) + ", ")
        f.write("%.3f" % statistics.mean(antichain_optimization_times_perf_counter) + ", ")
        f.write("%.3f" % statistics.mean(antichain_optimization_times) + "\n")

        f.write("Mean antichain size " + "%.3f" % statistics.mean(temp_antichain_sizes) + "\n")
        f.write("Mean number losing payoffs " + "%.3f" % statistics.mean(temp_nbr_payoffs_losing_player_0) + "\n")
        f.write("Mean number realizable payoffs " + "%.3f" % statistics.mean(temp_nbr_payoffs_realizable) + "\n")

        f.write("CE mean antichain size " + "%.3f" % statistics.mean(temp_counterexample_antichain_sizes) + "\n")
        f.write("CE mean nbr exists calls " + "%.3f" % statistics.mean(temp_counterexample_nbr_calls_exists) + "\n")
        f.write("CE mean exists time " + "%.3f" % statistics.mean(temp_counterexample_mean_time_calls_exists) + "\n")
        f.write("CE mean nbr dominated calls " + "%.3f" % statistics.mean(temp_counterexample_nbr_calls_dominated) +
                "\n")
        f.write("CE mean dominated time " + "%.3f" % statistics.mean(temp_counterexample_mean_time_calls_dominated) +
                "\n")
        f.write("CE mean total nbr calls " + "%.3f" % statistics.mean(temp_counterexample_nbr_calls) + "\n")

        f.write("AO mean antichain size " + "%.3f" % statistics.mean(temp_antichain_optimization_antichain_sizes) +
                "\n")
        f.write("AO mean nbr call1 calls " + "%.3f" % statistics.mean(temp_antichain_optimization_nbr_calls1) + "\n")
        f.write("AO mean call1 time " + "%.3f" % statistics.mean(temp_antichain_optimization_mean_time_calls1) + "\n")
        f.write("AO mean nbr call2 calls " + "%.3f" % statistics.mean(temp_antichain_optimization_nbr_calls2) + "\n")
        f.write("AO mean call2 time " + "%.3f" % statistics.mean(temp_antichain_optimization_mean_time_calls2) + "\n")
        f.write("AO mean total nbr calls " + "%.3f" % statistics.mean(temp_antichain_optimization_nbr_calls) + "\n")

        f.write("\n")
        f.write("\n")
        f.write("\n")

        f.close()


def get_counterexample_statistics(automaton, nbr_objectives, colors_map, save_file):
    """
    Get the evolution of the size of the antichain computed by the counterexample algorithm along with the running time
    of each call trying to find a counterexample.
    :param automaton: the automaton.
    :param nbr_objectives: the number of objectives for Player 1.
    :param colors_map: maps each parity objective to the set of SPOT acceptance sets used to represent its priorities.
    :param save_file: file in which to save the results.
    """
    _, _, ce_exists_stats, _, antichain_evol = counterexample_based_statistics(automaton, nbr_objectives, colors_map)

    f = open(save_file, "a")
    f.write("Call times " + str(ce_exists_stats[1]) + "\n")
    f.write("Antichain size " + str(antichain_evol) + "\n")
    f.close()


def parse_results(file_name, benchmark_type, nbr_points, save_file):
    """
    Parse the results contained in the file file_name (which is the output of run_benchmark) and creates a .dat file
    save_file containing the running time of both algorithms for each value of the variable being tested and for each
    of the nbr_points runs of the algorithms. In addition, when benchmark_type is "random", we also report the mean
    running time of each algorithm on the nbr_points runs for each value of the variable.
    :param file_name: file containing benchmarks data (output of run_benchmark).
    :param benchmark_type: should be in ["random", "intersection_vertices", "intersection_objectives"].
    :param nbr_points: number of times the algorithms are evaluated given a set of parameters.
    :param save_file: path to .dat file containing results.
    """

    x = []
    y_ce = []
    y_ao = []
    mean_y_ce = []
    mean_y_ao = []

    with open(file_name, "r") as search:

        for line in search:

            line = line.rstrip().split(" ")
            if line[0] == "Variable" and line[1] == "value" and line[2] == "used":
                current_x = int(line[3])
                for i in range(nbr_points):
                    if benchmark_type == "intersection_vertices":
                        x.append(current_x)
                    if benchmark_type == "intersection_objectives":
                        x.append(2 + current_x * 2)
                    if benchmark_type == "random":
                        x.append(current_x)

            if line[0] == "CE" and line[1] == "times" and line[2] == "process":
                current_ce_times = ast.literal_eval(" ".join(line[3:]))
                for i in range(nbr_points):
                    y_ce.append(current_ce_times[i])

            if line[0] == "AO" and line[1] == "times" and line[2] == "process":
                current_ao_times = ast.literal_eval(" ".join(line[3:]))
                for i in range(nbr_points):
                    y_ao.append(current_ao_times[i])


            if benchmark_type == "random":
                if line[0] == "Mean" and line[1] == "running" and line[2] == "time" and line[3] == "CE":
                    current_mean_y_ce = ast.literal_eval(" ".join(line[4:]))
                    for i in range(nbr_points):
                        mean_y_ce.append(float(current_mean_y_ce[0]))

                if line[0] == "Mean" and line[1] == "running" and line[2] == "time" and line[3] == "AO":
                    current_mean_y_ao = ast.literal_eval(" ".join(line[4:]))
                    for i in range(nbr_points):
                        mean_y_ao.append(float(current_mean_y_ao[0]))

    f = open(save_file, "a")
    if benchmark_type == "intersection_vertices":
        f.write("nbr_vertices CE_time AO_time\n")
        for i in range(len(x)):
            f.write(str(x[i]) + " " + str(y_ce[i]) + " " + str(y_ao[i]) + "\n")

    if benchmark_type == "intersection_objectives":
        f.write("nbr_objectives CE_time AO_time\n")
        for i in range(len(x)):
            f.write(str(x[i]) + " " + str(y_ce[i]) + " " + str(y_ao[i]) + "\n")

    if benchmark_type == "random":
        f.write("nbr_objectives CE_time AO_time mean_CE_time mean_AO_time\n")
        for i in range(len(x)):
            f.write(str(x[i]) + " " + str(y_ce[i]) + " " + str(y_ao[i]) + " " + str(mean_y_ce[i]) + " " +
                    str(mean_y_ao[i]) + "\n")

    f.close()


def generate_tables(file_name):
    """
    Parse the results contained in the file file_name (which is the output of run_benchmark) and prints the latex table
    containing the mean antichain size, mean antichain size approximation for the counterexample algorithm and mean
    antichain size approximation for the antichain optimization algorithm as well as the ratio of lost payoffs.
    :param file_name: file containing benchmarks data (output of run_benchmark).
    """

    mean_antichain_size = []
    mean_number_losing_payoffs = []
    mean_number_realizable_payoffs = []
    ce_mean_antichain_size = []
    ao_mean_antichain_size = []

    dict_pattern = {
        "Mean antichain size": mean_antichain_size,
        "Mean number losing payoffs": mean_number_losing_payoffs,
        "Mean number realizable payoffs": mean_number_realizable_payoffs,
        "CE mean antichain size": ce_mean_antichain_size,
        "AO mean antichain size": ao_mean_antichain_size
    }

    dict_pattern_names = {
        "Mean antichain size": "$|\paretoSet{G}|$",
        "CE mean antichain size": "$|A|$ in Algorithm \\ref{algo:fpt}",
        "AO mean antichain size": "$|A|$ in Algorithm \\ref{algo:fpt-CE}"
    }

    for pattern in dict_pattern.keys():

        with open(file_name, "r") as search:

            for line in search:

                line = line.rstrip().split(pattern)

                if len(line) == 2:
                    dict_pattern[pattern].append(line[1])

        dict_pattern[pattern] = list(reversed(dict_pattern[pattern]))

    nbr_elements = len(dict_pattern["Mean number realizable payoffs"])
    print("t " + " & ", end=" ")
    for i in range(nbr_elements - 1):
        print(str(i + 1) + " & ", end=" ")
    print(str(nbr_elements) + " \\\\")

    for pattern in dict_pattern_names.keys():
        print(dict_pattern_names[pattern] + " & ", end=" ")
        current_list = dict_pattern[pattern]
        nbr_elements = len(current_list)
        for i in range(nbr_elements - 1):
            print(current_list[i].strip() + " & ", end=" ")
        print(current_list[nbr_elements - 1].strip() + " \\\\")

    print("Ratio of lost payoffs" + " & ", end=" ")
    nbr_elements = len(dict_pattern["Mean number realizable payoffs"])
    for i in range(nbr_elements - 1):
        print("%.3f" % (float(list(dict_pattern["Mean number losing payoffs"])[i]) / float(list(
            dict_pattern["Mean number realizable payoffs"])[i])) + " & ", end=" ")
    print("%.3f" % (float(list(dict_pattern["Mean number losing payoffs"])[nbr_elements - 1]) / float(list(
        dict_pattern["Mean number realizable payoffs"])[nbr_elements - 1])) + " \\\\")


run_benchmark("intersection_vertices",
              "benchmarks_results/intersection-vertices-positive.txt",
              [True],
              1,
              100000, 0, -1000)

parse_results("benchmarks_results/intersection-vertices-positive.txt",
              "intersection_vertices",
              1,
              "benchmarks_results/intersection-vertices-positive.dat")

run_benchmark("intersection_vertices",
              "benchmarks_results/intersection-vertices-negative.txt",
              [False],
              1,
              100000, 0, -1000)

parse_results("benchmarks_results/intersection-vertices-negative.txt",
              "intersection_vertices",
              1,
              "benchmarks_results/intersection-vertices-negative.dat")

run_benchmark("intersection_objectives",
              "benchmarks_results/intersection-objectives-positive.txt",
              [True],
              1,
              10, 1, -1)

parse_results("benchmarks_results/intersection-objectives-positive.txt",
              "intersection_objectives",
              1,
              "benchmarks_results/intersection-objectives-positive.dat")

run_benchmark("intersection_objectives",
              "benchmarks_results/intersection-objectives-negative.txt",
              [False],
              1,
              10, 1, -1)

parse_results("benchmarks_results/intersection-objectives-negative.txt",
              "intersection_objectives",
              1,
              "benchmarks_results/intersection-objectives-negative.dat")

run_benchmark("random",
              "benchmarks_results/random-positive.txt",
              [500, 0.2, 0.2, 0.1, True],
              50,
              15, 5, -1)

parse_results("benchmarks_results/random-positive.txt",
              "random",
              50,
              "benchmarks_results/random-positive.dat")

run_benchmark("random",
              "benchmarks_results/random-negative.txt",
              [500, 0.2, 0.1, 0.5, False],
              50,
              15, 6, -1)

parse_results("benchmarks_results/random-negative.txt",
              "random",
              50,
              "benchmarks_results/random-negative.dat")
