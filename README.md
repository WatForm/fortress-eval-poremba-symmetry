# README

This is how the evaluation of Poremba, Day and Vakili's symmetry breaking schemes was completed.

## TL;DR
```
git clone https://github.com/WatForm/fortress-eval-poremba-symmetry.git
git clone https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks/UF.git
git clone https://github.com/WatForm/fortress.git
cd fortress-eval-poremba-symmetry.git
./install_fortress.sh
<set options for sat in python/run-tests.py>
python3 python/run-tests.py &
<set options for unsat in python/run-tests.py>
python3 python/run-tests.py &
python3 python/tally-results.py &
```

The results (after many days!) will be data in:

results/date-time-sat-run-tests.txt

results/date-time-unsat-run-tests.txt

with the run times for every tested version recorded in the above files.

## Complete Experiment Instructions

Below replace THISDIR with the location of this directory.

* Get the fortress evaluation scripts (this repo)
	- git clone https://github.com/WatForm/fortress-eval-poremba-symmetry.git
	
* Install Fortress
	- requirements:
	 	+ Java 10 or higher
		+ sbt 
		+ a command-line version of z3 
			- Binaries for Z3 are [available here](https://github.com/Z3Prover/z3/releases).
    			- If using MacOS, we recommend using Homebrew: `brew install z3`.
    			- If on `Ubuntu`, do not use `apt-get`, since its version of Z3 is out of date.
	- in a sister directory: git clone https://github.com/WatForm/fortress.git
		+ master branch (release v-poremba-symmetry-eval-1)
    	- within fortress-eval-poremba-symmetry, run the script to build fortress 
		+ ./install_fortress.sh
		+ this script copies the necessary parts of fortress into THISDIR/libs
    - we use (on tumbo.cs):
    	+ sbt 1.6.1
    	+ java 13.0.2 2020-01-14
	  Java(TM) SE Runtime Environment (build 13.0.2+8)
	  Java HotSpot(TM) 64-Bit Server VM (build 13.0.2+8, mixed mode, sharing)
    	+ Z3 version 4.8.10 - 64 bit    
	
* Get the benchmark files
	- git clone https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks/UF.git
	- Commit: dd1c268beb61a2c583caf414b32248decdff0d0a (master branch)

* Generate randomly ordered list of smt2 files that are known to be unsat/sat problems
	- these filelists are included in this repo because if you redo this step, you may get a different order and therefore may not get the same results
	- Within benchmarks directory, run
	```
	grep -r -l "(set-info :status unsat)" . | gshuf >  ../fortress-eval-poremba-symmetry/results/2022-01-13-unsat-random-order-filelist.txt
	grep -r -l "(set-info :status sat)" . | gshuf > ../fortress-eval-poremba-symmetry/results/2022-01-13-sat-random-order-filelist.txt
	```
	- Totals: Unsat 3394 files Sat 1233 files
	(Note: gshuf works for mac; shuf for bash in linux probably)

* Finding a good scope
	- within python/bisection-multi-fortress-versions.py, set sat/unsat and any other parameters
		+ we asked for 50 sat and 100 unsat 
			- unsat problems are generally harder
			- known SAT problems might not end up SAT at a specific/finite scope so harder to find these problems
		+ scope of 5 to 30 (range of scopes determined after some trial and error) -- all timing is done by the python script not fortress
		+ v1 (Fortress) time within 3-20min; v3 (Fortress+),v3si (Fortress+SI) times < 30min (to have reasonable size problems with no timeouts)
	- within THISDIR run: 
	 ```python3 python/bisection-multi-fortress-versions.py```	
	- some files are not parseable because our smt parser does not support everything in smt-lib
	- for files of the same name, we started the bisection algorithm with the good scope  from 1st submission (but ran the bisection algorithm on it to make sure that scope fit in the time window for all versions)
	- results are in:  
	results/2022-01-15-sat-file-scope-list.txt  
	results/2022-01-28-unsat-file-scope-list.txt
	
* Performance testing
        - change settings in python/run-tests.py to run the sat files or the unsat files
	- within THISDIR run: 
	```
	python3 python/run-tests.py
	```
	This script runs each file three times on the three versions of fortress.

	Resulting data is in:  
	results/sat-v1-v3-v3si-time-data.txt
	results/unsat-v1-v3-v3si-time-data.txt

* Tally results
	- within THISDIR run:
	```
	python3 python/tally-results.py
	```
	This script determines the average of the 3 runs for each file and sums the totals for each version and prints summary data to the terminal.  It also directly creates the tables and plots that appear in the paper.


