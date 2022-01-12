# README

Last updated: 2022-01-11

This is how the fortress evaluation of Poremba and Day's symmetry breaking schemes was completed.

Below replace THISDIR with the location of this directory.

## TL;DR
```
git clone https://github.com/WatForm/fortress-eval-poremba-symmetry.git
git clone https://github.com/WatForm/fortress.git
git clone https://github.com/WatForm/fortress.git
cd fortress-eval-poremba-symmetry.git
./install_fortress.sh
```

## Complete Experiment Instructions

* Fortress evaluation scripts (this repo)
	- git clone https://github.com/WatForm/fortress-eval-poremba-symmetry.git
	
* install Fortress
	- requirements:
	 	+ Java 10 or higher
		+ sbt 
		+ a command-line version of z3 
			- Binaries for Z3 are [available here](https://github.com/Z3Prover/z3/releases).
    			- If using MacOS, we recommend using Homebrew: `brew install z3`.
    			- If on `Ubuntu`, do not use `apt-get`, since its version of Z3 is out of date.
	- in a sister directory: git clone https://github.com/WatForm/fortress.git
    	- within fortress-eval-poremba-symmetry, run the script to build fortress 
		+ ./install_fortress.sh
		+ this script copies the necessary parts of fortress into THISDIR/libs
    - we use (tumbo.cs):
    	+ sbt 1.6.1
    	+ java 13.0.2 2020-01-14
	  Java(TM) SE Runtime Environment (build 13.0.2+8)
	  Java HotSpot(TM) 64-Bit Server VM (build 13.0.2+8, mixed mode, sharing)
    	+ Z3 version 4.8.10 - 64 bit    
	
* Get the benchmark files
	- c
	- on 2022-01-11
	- Commit: dd1c268beb61a2c583caf414b32248decdff0d0a

* Generate randomly ordered list of smt2 files that are known to be unsat/sat problems
	- these filelists are included in this repo because if you redo this step, you may get a different order and therefore may not get the same results
	- Within benchmarks directory, run
	```
	grep -r -l " unsat" . | gshuf >  ~nday/UW/github/fortress-eval-2022-tse/results/2022-01-11-unsat-random-order-filelist.txt
	grep -r -l " sat" . | gshuf > ~nday/UW/github/fortress-eval-2022-tse/results/2022-01-11-sat-random-order-filelist.txt
	```
	- Totals: Unsat 3394 files Sat 1233 files
	(Note: gshuf works for mac; shuf for bash in linux probably)

* Finding a good scope
	- within python/bisection-multi-fortress-versions.py, set sat/unsat and any other parameters
		+ we asked for 50 sat and 100 unsat 
			- unsat problems are generally harder
			- known SAT problems might not end up SAT at a specific/finite scope so harder to find these problems
		+ scope of 5 to 30 (range of scopes determined after some trial and error) -- all timing is done by the python script not fortress
		+ v1 time within 3-20min; v3,v3si times < 30min (to have reasonable size problems with no timeouts)
	- within THISDIR run: 
	 ```python3 python/bisection-multi-fortress-versions.py```	

* Performance testing
	- within THISDIR run: 
	- this runs each file at the designated scope 5x on the three versions of fortress

* Tally results
	- within THISDIR run:
	- determines the average of the 5 runs for each file and sums the totals for 
	- generates the tables for the paper in latex
	- generates the plots for the paper in latex

