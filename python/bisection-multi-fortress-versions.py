"""
    Use a bisection algorithm to determine a scope that completes
    within the time bounds on all versions

    All indices start at 1
"""

import re
import csv
import math
from statistics import mean
from datetime import datetime
import util
from defs import *

versions = ["v1","v3","v3si"]

# for finding at files
goal = "sat"
goaltotal = 50
originalfilescopelist = thisdirprefix + "results/2020-09-13-sat-original-best-scope.txt"

# for finding unsat files
#goal = "unsat"
#goaltotal = 100
#originalfilescopelist = thisdirprefix + "results/2020-09-01-unsat-original-best-scope.txt"

filecounter = 31  # start at first line of files; counting starts at 1
                 # change above if process does not finish and we have to restart
goalcounter = 0 # need to reset this if change filecounter!!!

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")

inputfilelist = thisdirprefix + "results/2022-01-13-"+goal+"-random-order-filelist.txt"
longlogfile = thisdirprefix + "results/"+dt_string+"-"+goal+"-get-scope-LONG-LOG.txt"
logfile = thisdirprefix + "results/"+dt_string+"-"+goal+"-get-scope-LOG.txt"
outfile = thisdirprefix + "results/"+dt_string+"-"+goal+"-get-scope-filelist.txt"

# range is 5-30 determined after some trial and error
minscope = 4 # have to start 1 lower and 1 higher so can stop 
maxscope = 31  
# starting scope will be 18, but it is calculated

# 3-20 min
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
    return output

def long(n):
    return benchmarksdir + name

def get_scope_bisection_with_versions(name, cnt):
    global fortresstimeout, lowertimethreshold, uppertimethreshold, longlogf,minscope,maxscope
    global originalfilescope

    # non-recursive
    fmin = minscope
    fmax = maxscope
    # starting scope
    if name in originalfilescope.keys():
        # if we have a scope that worked in our last eval
        # start there, but still go through checking for 3 versions
        sc = originalfilescope[name]
        if not(minscope < sc and sc < maxscope):
            sc = math.ceil(mean([fmin, fmax]))
        else:
            longlogf.write("Using original scope of "+str(sc))
            longlogf.flush()
    else:
        sc = math.ceil(mean([fmin, fmax]))
    ver0_scopes_tried = [] 
    j = 0 # tests on this file
    ver = 0  # index into versions on versions list
    while minscope < sc and sc < maxscope and not(ver == 0 and sc in ver0_scopes_tried) and ver < len(versions):
        j += 1
        ver0_scopes_tried.append(sc)
        fortressargs = ' -J' + stacksize + ' --timeout ' + str(fortresstimeout) + \
            ' --mode decision --scope ' + str(sc) + ' --version ' + versions[ver] + \
            " --rawdata" + " " + long(name)
        longlogf.write("\nRUN NO. " + str(cnt) + "," + str(j) + " scope=" + str(sc) + "\n" + name + '\n')
        longlogf.write(fortressbin + fortressargs + '\n')
        longlogf.flush()
        (time, output, exitcode) = util.runprocess(fortressbin + fortressargs, longlogf, uppertimethreshold)
        # there is a 30sec delay after the process is finished to make sure Z3 is dead
        # Check if the result aligns with our goal
        out = satisfiability_of_output(output)   
        if goal != out and (out == 'unsat' or out == 'sat'):
            # quit right away b/c it doesn't match sat/unsat that we want
            return 0, "not "+goal
    
        if (out in toobig_outputcodes):
            # If there is time out, looking for a smaller scope
            ver = 0  # might already be version 0
            # lower scope
            fmax = sc
            sc = math.floor(mean([fmin, sc]))
        elif not (out in ['sat','unsat']):  # toobig_outputcodes already handled above
            return 0, "non-zero output, not known overflow or timeout"
        elif time < lowertimethreshold and ver == 0:
            # only bother with looking at higher scopes if ver == 0
            fmin = sc
            sc = math.ceil(mean([sc, fmax]))
        else:
            ver += 1

    # end of loop
    if not(minscope < sc and sc < maxscope) or (ver == 0 and sc in ver0_scopes_tried):
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

# original file scope info -> can use it to start
originalfilescope = {}
with open(originalfilescopelist) as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        filename = "./"+row[0].strip()
        originalfilescope[filename] = int(row[2].strip())

while goalcounter < goaltotal and filecounter <= len(filelist):
    name = filelist[filecounter-1].strip()
    (sc, reason) = get_scope_bisection_with_versions(name,filecounter) 
    # every file should have an entry in logf
    # and once this has been written that file is completed
    logf.write(str(filecounter)+", "+ name + ", " + reason + ", " + str(sc) + '\n')
    logf.flush()
    if reason == goal:
        goalcounter += 1
        outf.write(name + ", " + reason + ", " + str(sc) + '\n')
        outf.flush()
    filecounter += 1

outf.close()
logf.close()
longlogf.close()
print("Completed!")
