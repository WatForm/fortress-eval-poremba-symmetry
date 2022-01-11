"""
    Use a bisection algorithm to determine a scope that completes
    within the time bounds on all versions
"""

import re
import csv
import math
from statistics import mean
from datetime import datetime
import util
from defs import *

versions = ["v1","v3","v3si"]

goal = "sat"
goaltotal = 50
#goal = "unsat"
#countgoal = 100

counter = 0  # change this if process does not finish and we have to restart

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")

inputfilelist = thisdirprefix + "results/2022-01-11-"+goal+"-random-order-filelist.txt"
longlogfile = thisdirprefix + "results/"+dt_string+"-"+goal+"-bisection-multi-fortress-LONG-LOG.txt"
logfile = thisdirprefix + "results/"+dt_string+"-"+goal+"-bisection-multi-fortress-LOG.txt"
outfile = thisdirprefix + "results/"+dt_string+"-"+goal+"-with-scope-filelist.txt"

# range is 5-30 determined after some trial and error
minscope = 4 # have to start 1 lower and 1 higher so can stop 
maxscope = 31  
# starting scope will be 18, but it is calculated

lowertimethreshold = 3 * 60  # seconds
uppertimethreshold = 20 * 60  # seconds
fortresstimeout = (uppertimethreshold + 600) * 1000  # ms; always way bigger

fortressbin = thisdirprefix + 'libs/fortressdebug-0.1.0/bin/fortressdebug'
stacksize = '-Xss8m'  # fortress JVM Stack size set to 8 MB

def satisfiability_of_output(output):
    if re.search('Unsat', output):
        return 'unsat'
    elif re.search('Sat', output):
        return 'sat'
    return output

def long(n):
    return benchmarksdir + name

def get_scope_bisection_with_versions(name, cnt):
    global fortresstimeout, lowertimethreshold, uppertimethreshold, longlogf,minscope,maxscope

    # non-recursive
    fmin = minscope
    fmax = maxscope
    # starting scope
    sc = math.ceil(mean([fmin, fmax]))
    j = 0 # tests on this file
    ver = 0  # index into versions on versions list
    while minscope < sc and sc < maxscope and ver < len(versions):
        ++j
        fortressargs = ' -J' + stacksize + ' --timeout ' + str(fortresstimeout) + \
            ' --mode decision --scope ' + str(sc) + ' --version ' + versions[ver] + \
            " " + long(name)
        longlogf.write("\nRUN NO. " + str(cnt) + "," + str(j) + " scope=" + str(sc) + "\n" + name + '\n')
        longlogf.write(fortressbin + fortressargs + '\n')
        longlogf.flush()
        (time, output, exitcode) = util.runprocess(fortressbin + fortressargs, longlogf, uppertimethreshold)
        # Check if the result aligns with our goal
        out = satisfiability_of_output(output)   
        if goal != out and (out == 'unsat' or out == 'sat'):
            # quit right away b/c it doesn't match sat/unsat that we want
            return 0, "not goal"
     
        if (out == "TIMEOUT" or out == "NONZEROCODE" or out == "StackOverflowError") :
            # If there is time out, looking for a smaller scope
            ver = 0  # might already be version 0
            # lower scope
            fmax = sc
            sc = math.floor(mean([fmin, sc]))
        elif time < lowertimethreshold and ver == 0:
            # only bother with looking at higher scopes if ver == 0
            fmin = sc
            sc = math.ceil(mean([sc, fmax]))
        else:
            ++ver

    # end of loop
    if minscope < sc and sc < maxscope:
        return 0, "no scope finishes in time range for all versions"
    else: 
        # we'd have to go to the logs to find out the times for these
        return sc, goal

# main


# long log if need to check for errors
longlogf = open(longlogfile, "w")

# shorter log of all file results
logf = open(logfile, "w")

# output file list to use
outf = open(outfile, "w")

# read in the randomized list of files for this process
filelist = []
startingscope = {}
with open(inputfilelist) as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        filename = row[0].strip()
        filelist.append(filename)
maxcount = len(filelist)

while counter < goaltotal and counter <= maxcount:
    name = filelist[counter].strip()
    (sc, reason) = get_scope_bisection_with_versions(name,counter) 
    # every file should have an entry in logf
    # and once this has been written that file is completed
    logf.write(str(counter)+", "+ name + ", " + reason + ", " + str(sc) + '\n')
    logf.flush()
    if reason == goal:
        outf.write(name + ", " + reason + ", " + str(sc) + '\n')
        outf.flush()
    ++counter

outf.close()
logf.close()
longlogf.close()
print("Completed!")
