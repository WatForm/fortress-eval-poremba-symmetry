# README

Last updated: 2022-01-11

This is how the fortress-evaluation was completed.

Below replace THISDIR with the location of this directory.

Right now this is for my mac ...

* Fortress
	- install fortress: git clone https://github.com/WatForm/fortress.git
	- the following script builds fortress and copies it into THISDIR/libs
		./install_fortress.sh
	- our evaluation was done with
		+ Z3 version 4.8.12 - 64 bit
		+ java version "12.0.1" 2019-04-16
			Java(TM) SE Runtime Environment (build 12.0.1+12)
			Java HotSpot(TM) 64-Bit Server VM (build 12.0.1+12, mixed mode, sharing)
		+ Scala code runner version 2.13.6 -- Copyright 2002-2021, LAMP/EPFL and Lightbend, Inc.
		
* Benchmarks
	- git clone https://clc-gitlab.cs.uiowa.edu:2443/SMT-LIB-benchmarks/UF.git
	- on 2022-01-11
	- Commit: dd1c268beb61a2c583caf414b32248decdff0d0a

* Generate randomly ordered list of smt2 files that are known to be unsat/sat problems

Within benchmarks directory, run
grep -r -l " unsat" . | gshuf >  ~nday/UW/github/fortress-eval-2022-tse/results/2022-01-11-unsat-random-order-filelist.txt
grep -r -l " sat" . | gshuf > ~nday/UW/github/fortress-eval-2022-tse/results/2022-01-11-sat-random-order-filelist.txt

Totals: 
Unsat 3394 files
Sat 1233 files

(Note: gshuf works for mac; shuf for bash in linux probably)

* Finding a good scope
	- within THISDIR run: python3 python/bisection-multi-fortress-versions.py
	- range is 5-30 scope determined after some trial and error
	- time range of 3 min to 20 min determined in order to have reasonable size of problems for fortress 1 
	- we don't worry about lower time limit for version 3 and 3si
	- set options for how many sat or unsat problems looking for
	- runs versions 1, 3, 3si and makes sure all complete at the scope
	
****


Get 50 SAT problems and 100 UNSAT problems with the argument that UNSAT problems are generally harder. (Note that SAT problems from step 2 might not end up SAT for finite scopes so we have to keep going until we get 50 SAT problems, but separating them should be better than ploughing through definitely unsat problems).


Then run all three versions 5x for each fortress version and take the average time.


Create a simpler table than is currently in the paper to just look at total times and not at fraction that are faster or slower.
