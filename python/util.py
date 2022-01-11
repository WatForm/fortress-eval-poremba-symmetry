import sys
import os
import os.path
import signal
import re
from subprocess import Popen, PIPE, TimeoutExpired
from time import monotonic as timer
import csv
import math
from statistics import mean
from datetime import datetime
from time import strftime
import psutil
import time


def check(processName,longlogf):
    '''
    Check if there is any running process that contains the given name processName.
    from: https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
    '''

    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                longlogf.write("Z3 process exists: "+str(proc.pid)+"\n")
                longlogf.flush()
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def killp(p,name,longlogf):
     try:
         # occasionally the child process dies by itself and this then
         # causes an exception b/c child.pid does not exist
         # so the try/except is needed
         p.kill()
         # the following seems to have processlookup errors even though process
         # exists
         # os.killpg(p.pid, signal.SIGKILL) 
         longlogf.write("killed: "+name+"\n")
         longlogf.flush()
     except ProcessLookupError:
        longlogf.write("os.killpg could not find: "+str(p.pid)+"\n")
        longlogf.flush()
        if check(name,longlogf):
            longlogf.close()
            exit(1)
     except Exception as ex:
         template = "An exception of type {0} occurred. Arguments:\n{1!r}"
         message = template.format(type(ex).__name__, ex.args)
         longlogf.write(message+"\n")
         longlogf.write("Did not kill: "+str(p.pid)+" "+ name+"\n")
         longlogf.flush()
     return

def kill_child_processes(longlogf):   
    # have to kill sh, java, z3 child processes
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    children.sort(key=lambda x: x.pid,reverse=True)
    for c in children:
        longlogf.write("Need to kill: "+str(c.pid)+" "+ c.name()+"\n")
        longlogf.flush() 
    for c in children:
        longlogf.write("Trying to kill: "+str(c.pid)+" "+ c.name()+"\n")
        killp(c,c.name(),longlogf)
    time.sleep(30) # seconds
    # have to wait to make sure processes killed
    # When the time was set to 15 seconds, there's still a small possibility of Z3 process
    # hasn't been cleaned up yet. We increased it to 30 seconds to avoid that.

def runprocess(name,longlogf,uppertimethreshold):
    start = timer()
    exitcode = None
    # check for leftover Z3 process; if they exist stop
    if check("z3",longlogf):
        longlogf.write("Extra Z3 process running")
        output = "EXTRA_Z3"
        t = uppertimethreshold
    else:
        with Popen(name, shell=True, stdout=PIPE, stderr=PIPE, preexec_fn=os.setsid) as process:
            try:
                (out,err) = process.communicate(timeout=uppertimethreshold)
                t = timer() - start
                output = out.decode("utf-8")
                longlogf.write(output)
                minutes = math.floor(t / 60)
                seconds = round(t % 60,3)
                longlogf.write("\nPython time: "+str(minutes)+'m '+str(seconds)+'s\n')
                longlogf.flush()
                if process.returncode == 1:
                    longlogf.write("\n***Non-zero return code: " + name+"\n")
                    longlogf.flush()
                    if re.search(r'java.lang.StackOverflowError', str(err)):
                        output = "StackOverflowError"
                    else:
                        output = "NONZEROCODE"
                    t = uppertimethreshold
                exitcode = process.returncode
            except TimeoutExpired:
                t = uppertimethreshold
                output = "TIMEOUT"
                longlogf.write(output+"\n")
                longlogf.flush()       	
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                longlogf.write(message+"\n")
                # longlogf.write(str(sys.exc_info()[0])+"\n")
                longlogf.flush()
                t = uppertimethreshold
                output = "PROBLEM: "+message
            kill_child_processes(longlogf)
    return t, output, exitcode