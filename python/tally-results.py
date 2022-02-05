# form of data:
# filename, unsat, scope, version, time(seconds)

import csv

goal = "unsat"

inputfilename = "results/unsat-v1-v3-time-data.txt"

v1_v3_tex_name = goal+"-fortress-vs-fortress+.tex"
v3_v3si_tex_name = goal+"-fortress+-vs-fortress+SI.tex"
v1_v3si_tex_name = goal+"-fortress-vs-fortress+SI.tex"

tex_location = "results/"

outlier_threshold = 0.8
show_outliers = False
# this is useful because sometimes multiple versions will timeout on the same file
show_timeouts = True
# tuple position for data read from csv
name = 0
result = 1
scope = 2
version = 3
time = 4

numentries = 3


# map filename to average time for that version
v1 = {}
v2 = {}
v2si = {}
v2g = {}
v3 = {}
v3si = {}
scp = {}

# needed for scatterplot
mymax = 0

def getv(v):
    if v=='v1':
        return v1
    elif v=='v2':
        return v2
    elif v=='v3':
        return v3
    elif v=='v3si':
        return v3si
    elif v=='v2si':
        return v2si
    elif v=='v2g':
        return v2g
    else:
        print("unknown version! "+v)
        exit(1)

def getname(v):
    if v=='v1':
        return "Fortress"
    elif v=='v2':
        return v2
    elif v=='v3':
        return "Fortress+"
    elif v=='v3si':
        return "Fortress+SI"
    elif v=='v2si':
        return v2si
    elif v=='v2g':
        return v2g
    else:
        print("unknown version! "+v)
        exit(1)


# args are: name of output file, two dictionaries
def make_scatterplot(name,a,b):
    global filelist,mymax
    plotf = open(name,"w")
    plotf.write('''
    % This file is auto-generated by fortress-evaluation/evaluate/tally-results.py

    %\\documentclass[11pt]{article}
    % graphics
    %\\usepackage{tikz}
    %\\usepackage{pgfplots}
    %\\pgfplotsset{width=7.5cm,compat=1.12}
    %\\usepgfplotslibrary{fillbetween}
    %\\begin{document}
    \\begin{tikzpicture}
    \\pgfplotsset{
       scale only axis,
    }

    \\begin{axis}[
      axis lines = middle,
      xmin=0,
      ymin=0,
      xmax='''+str(MAXTIME)+''',
      ymax='''+str(MAXTIME)+''',
      x label style={at={(axis description cs:0.5,-0.1)},anchor=north},
      y label style={at={(axis description cs:-0.11,.5)},rotate=90,anchor=south},
      xlabel=
    '''+getname(a).strip()+
    ''' (seconds),
      ylabel=
    '''+getname(b).strip()+
    ''' (seconds),
    ]
    \\addplot[only marks, mark=x]
    coordinates{ % plot 1 data set
    ''')

    av = getv(a)
    bv = getv(b)
    for f in filelist:
        if f in av.keys() and f in bv.keys():
            if not(av[f] in [TIMEOUT,NO_NEW_SORTS] or bv[f] in[TIMEOUT,NO_NEW_SORTS]):
                plotf.write("("+str(av[f])+","+str(bv[f])+")\n")
    plotf.write('''
    }; \\label{plot_one}
    \\draw [blue,dashed] (rel axis cs:0,0) -- (rel axis cs:1,1);
    % plot 1 legend entry
    \\addlegendimage{/pgfplots/refstyle=plot_one}
    \\end{axis}
    \\end{tikzpicture}
    %\\end{document}
    ''')
    plotf.close()



filelist = []
data = []
with open(inputfilename) as f:
    reader = csv.reader(f,delimiter=",")
    for row in reader:
        fname = row[0].strip()
        if not (fname in filelist):
            filelist.append(fname)
        data.append([fname,row[result].strip(),row[scope].strip(),row[version].strip(),row[time].strip()])

for f in filelist:
    # get all the rows in the results file for this test
    f_entries = [r for r in data if r[0] == f]

    # all entries should be for this scope
    sc = f_entries[0][scope]
    scp[f] = sc

    # sanitization checks    
    for j in f_entries:
        if j[scope] != sc or j[result]!=goal:
            # data checks: all were run for same scope and got the expected result
            print(sc)
            print(j[scope])
            print(goal)
            print(j[result])
            print("check "+j[0]+" scopes or results don't match")
            exit(1)

    # take the average of the entries for each version
    # and store it in the dictionary

    # this is per file
    for v in ['v1','v3','v3si']:
        f_v_entries = [r for r in f_entries if r[version] == v]
        if f_v_entries!=[]:
            if len(f_v_entries)!=numentries:
                print("check "+f+" not "+str(numentries)+" data entries for "+v)
                exit(1)
            sum = 0
            for i in f_v_entries:
                sum += float(i[time])
            getv(v)[f] = round(sum/numentries,2)

# arguments are string names
def compare(aa,bb):

    # assumption: we want the faster one to be "b"
    # so we look for outliers where "b" is much slower than "a"

    global mymax
    # v1[file] = average time (seconds)v1[file/]
    # v2[file] = average time (seconds)
    # etc

    a = getv(aa)
    b = getv(bb)
    num_a_faster = 0
    num_b_faster = 0
    num_same_value = 0

    total_a_time = 0
    total_b_time = 0

    total_files = 0

    for f in filelist:
        if f in a.keys() and f in b.keys():
            # put this first so these don't get counted for the timeout and 
            # other tallies

            if a[f] < b[f] :
                num_a_faster += 1
                # find outliers
                if a[f]/b[f] < outlier_threshold and show_outliers:
                    print("Outlier: "+ f)
                    print("Scope: "+ str(scp[f]))
                    print(aa +" time:"+str(round(a[f],2)) )
                    print(bb +" time:"+str(round(b[f],2)) +"\n")
            elif b[f] < a[f]:
                num_b_faster += 1
            else:
                num_same_value +=1
            total_a_time += a[f]
            total_b_time += b[f]
            total_files += 1


    print(inputfilename)
    an = getname(aa)
    bn = getname(bb)
    print("All files: " + str(len(filelist)))
    print("Num files in tally: "+str(total_files))
    print("Num files same time: "+str(num_same_value))
    print("Total "+an+" time for all files "+str(round(total_a_time,2)))
    print("Total "+bn+" time for all files "+ str(round(total_b_time,2)))
    print("total"+bn+"/total"+an+" "+str(round(total_b_time/total_a_time,2)))

    print("Number of files "+an+" faster "+str(num_a_faster))
    print("Number of files "+bn+" faster "+str(num_b_faster))

print('-----')
print('Compare Fortress with Fortress+\n')
compare("v1","v3")
#make_scatterplot(tex_location+v1_v3_tex_name, "v1","v3")
print("")

#print('-----')
#print('Compare Fortress+ with Fortress+SI\n')
#compare("v3","v3si")
#make_scatterplot(tex_location+v3_v3si_tex_name, "v3", "v3si")

#print('-----')
#print('Compare Fortress with Fortress+SI\n')
#compare("v1","v3si")
##make_scatterplot(tex_location+v1_v3si_tex_name, "v1","v3si")
#print("")