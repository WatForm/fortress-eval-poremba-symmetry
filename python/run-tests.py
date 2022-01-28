"""
    Run every file at the input scope on all versions x times
    Tally as we go

    Outputs
    -filelist - just goal files, and their scope
    -LOG   - all files and one line about them
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

versions = ["v1","v3","v3si"]
num_tries = 1

# for finding at files
goal = "sat"

# for finding unsat files
#goal = "unsat"


filecounter = 1  # start at first line of files; counting starts at 1
                 # change above if process does not finish and we have to restart
goalcounter = 0 # need to reset this if change filecounter!!!

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")

inputfilelist = thisdirprefix + "results/2022-01-15-"+goal+"-file-scope-list.txt"
longlogfile = thisdirprefix + "results/"+dt_string+"-"+goal+"-run-tests-LONG-LOG.txt"
timedatafile = thisdirprefix + "results/"+dt_string+"-"+goal+"-run-tests-time-data.txt"

# 3-20 min
lowertimethreshold = 3 * 60  # seconds
uppertimethreshold = 20 * 60  # seconds
fortresstimeout = (uppertimethreshold + 600) * 1000  # ms; always way bigger

fortressbin = thisdirprefix + 'libs/fortressdebug-0.1.0/bin/fortressdebug'
stacksize = '-Xss8m'  # fortress JVM Stack size set to 8 MB
toobig_outputcodes = ["TIMEOUT", "JavaStackOverflowError", "JavaOutOfMemoryError"]

totaltimes = {}

def satisfiability_of_output(output):
    if re.search('Unsat', output):
        return 'unsat'
    elif re.search('Sat', output):
        return 'sat'
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
for i in range(len(versions)):
    totaltimes[i] = 0
for name in filescope.keys():
    sc = filescope[name]
    for i in range(num_tries):
        for v in range(len(versions)):
            fortressargs = ' -J' + stacksize + ' --timeout ' + str(fortresstimeout) + \
                ' --mode decision --scope ' + str(sc) + ' --version ' + versions[v] + \
                " --rawdata" + " " + long(name)
            longlogf.write("\nRUN NO. " + str(cnt) + "  "+ versions[v] + "  "+ name + " scope=" + str(sc) +  '\n')
            longlogf.write(fortressbin + fortressargs + '\n')
            longlogf.flush()
            (time, output, exitcode) = util.runprocess(fortressbin + fortressargs, longlogf, uppertimethreshold)
            status = satisfiability_of_output(output)
            totaltimes[v] += time
            # there is a 30sec delay after the process is finished to make sure Z3 is dead
            if exitcode == 0:
                timedataf.write(\
                    name + ", " + \
                    status + ", " + \
                    str(sc) + ", " + \
                    versions[v] + ", " + \
                    str(time) +'\n')
            else:
                timedataf.write(\
                    name + ", " + \
                    'non-zero exit code' +'\n')
            timedataf.flush()
        longlogf.write("totals so far:  ")
        for v in range(0,len(versions)):
            longlogf.write(versions[v]+" "+str(round(totaltimes[v],2))+"   ")
        longlogf.write("\n======\n")
        longlogf.flush()
    cnt += 1

timedataf.close()
longlogf.close()

print("Completed!")
