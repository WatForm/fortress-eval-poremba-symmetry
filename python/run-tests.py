"""
    Run every file at the input scope on all versions x times
    Tally as we go

    Outputs
    -file-scope- list - just goal files, and their scope
    -LONG-LOG - everything
    -time-data - goal files, scope, all versions & times (collects some data for initial perf comparisons)
"""

import re
import csv
import math
from statistics import mean
from datetime import datetime
import util
from defs import *

versions = ["v3si"]
num_tries = 3

# for 50 sat files
goal = "sat"
inputfilelist = thisdirprefix + "results/2022-01-15-"+goal+"-file-scope-list.txt"

# for 100 unsat files
#goal = "unsat"
#inputfilelist = thisdirprefix + "results/2022-01-28-"+goal+"-file-scope-list.txt"


filecounter = 1  # start at first line of files; counting starts at 1
                 # change above if process does not finish and we have to restart

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")


longlogfile = thisdirprefix + "results/"+dt_string+"-"+goal+"-run-tests-LONG-LOG.txt"
timedatafile = thisdirprefix + "results/"+dt_string+"-"+goal+"-run-tests-time-data.txt"

# 3-20 min
# not really needed this time
lowertimethreshold = 3 * 60  # seconds
uppertimethreshold = 20 * 60  # seconds
fortresstimeout = (uppertimethreshold + 600) * 1000  # ms; always way bigger

fortressbin = thisdirprefix + 'libs/fortressdebug-0.1.0/bin/fortressdebug'
stacksize = '-Xss8m'  # fortress JVM Stack size set to 8 MB
toobig_outputcodes = ["TIMEOUT", "JavaStackOverflowError", "JavaOutOfMemoryError"]

def satisfiability_of_output(output):
    if re.search('Unsat', output):
        return 'unsat'
    elif re.search('Sat', output):
        return 'sat'
    elif re.search(r'No new sorts', output):
        return 'No_new_sorts'
    return output

def long(n):
    return benchmarksdir + name

# main

# long log if need to check for errors
longlogf = open(longlogfile, "w")

# output file list to use
timedataf = open(timedatafile, "w")

filescope = {}
with open(inputfilelist) as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        filename = row[0].strip()
        sc = int(row[2])
        filescope[filename] = sc

cnt = 1
for name in filescope.keys():
    sc = filescope[name]
    for i in range(num_tries):
        for v in range(len(versions)):
            longlogf.write("\nRUN NO. " + str(cnt) + "  "+ versions[v] + "  "+ name + " scope=" + str(sc) +  '\n')
            new_sorts = False
            if versions[v] == "v3si" or versions[v] == "v2si":
                # check for new scopes first 
                fortressargs = ' -J' + stacksize + ' --timeout ' + str(fortresstimeout) + \
                    ' --mode checkfornewsorts --scope ' + str(sc) + ' --version ' + versions[v] + \
                    " --rawdata" + " " + long(name)
                longlogf.write(fortressbin + fortressargs + '\n')
                longlogf.flush()
                (time, output, exitcode) = util.runprocess(fortressbin + fortressargs, longlogf, uppertimethreshold)
                status = satisfiability_of_output(output)
                if status == 'No_new_sorts':
                    longlogf.write("NO NEW SORTS\n")
                    longlogf.flush()
                    break
                else:
                    # just one line is returned
                    x = [int(s) for s in re.findall(r'\d+',output)]
                    new_sorts = True
                    old_num_sorts = x[0]
                    new_num_sorts = x[1]
            fortressargs = ' -J' + stacksize + ' --timeout ' + str(fortresstimeout) + \
                ' --mode decision --scope ' + str(sc) + ' --version ' + versions[v] + \
                " --rawdata" + " " + long(name)
            longlogf.write(fortressbin + fortressargs + '\n')
            longlogf.flush()
            (time, output, exitcode) = util.runprocess(fortressbin + fortressargs, longlogf, uppertimethreshold)
            status = satisfiability_of_output(output)
            # there is a 30sec delay after the process is finished to make sure Z3 is dead
            if exitcode == 0 and goal == satisfiability_of_output(output):
                timedataf.write(\
                    name + ", " + \
                    status + ", " + \
                    str(sc) + ", " + \
                    versions[v] + ", " + \
                    str(time))
                if new_sorts:
                    timedataf.write(", "+str(old_num_sorts)+", "+str(new_num_sorts))
                timedataf.write('\n')
            else:
                timedataf.write(\
                    name + ", " + \
                    status + ", " + \
                    str(sc) + ", " + \
                    versions[v] + ", " + \
                    'non-zero exit code' +'\n')
            timedataf.flush()
    cnt += 1

longlogf.write("Completed!\n")
longlog.flush()

timedataf.close()
longlogf.close()


