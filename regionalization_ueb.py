"""
This is the code used for regionalization in ueb+sac workflow.
The original code is from RTI

requirement:
- param_limits.txt
- Regionalization folder: includes basin folders which have 2nd ipython notebook node results
- Decision000.dat
- front000.dat'
- cap.txt

output:
- result000.dat file
- print output of the determined parameters

"""

import os
import pandas as pd
from numpy import genfromtxt
import numpy as np

from bokeh.plotting import figure, show, ColumnDataSource, curdoc,gridplot
from bokeh.models.widgets import Dropdown, Button, TextInput
from bokeh.io import output_notebook, push_notebook
import glob

import itertools
import datetime
from scipy.special import comb


# define functions  ##############################################################################################
# cell 4  ########################################################################
# Calculate the parameter weights between basins
def calNormalizedDifference_CAP(Basins):
    """
    Note
    - purpose: calculate the weight how similar the parameters of the basins are based on cap file (how similar the parameters are supposed to be )
    - used by cell 18
    - need the CAP file
    - comblist: create combination of basin names, each combination includes 2 basins
    - calculate the similarity between two basins using info from CAP and para_limit.txt
    - return dictionary of normalized difference sets : {['MPHC2-DOLC2'] : {'sac_UZTWC': similarity value, ...}}

    """

    # Parameter Weight Dictionary
    NormDifferenceSets = {}

    # create list of basin combinations
    comblist = list(itertools.combinations(Basins, 2))

    # Calculate parameter weights between the pairs of the basins
    for i in comblist:
        NormDifferences = {}
        for par in ShortParList:
            par_a = cap[cap['CH5_ID'] == i[0]][par].values[0]
            par_b = cap[cap['CH5_ID'] == i[1]][par].values[0]
            similarity = (par_a - par_b) / (VMax[par] - VMin[par])
            NormDifferences[par] = similarity

        NormDifferenceSets['-'.join(i)] = NormDifferences
    return NormDifferenceSets



# cell 5 ###################################################################
def calNormalizedDifference_OPT(A,B):
    """
    Note:
    - used by cell 6

    """
    if (len(A) <> len(B)):
        print('Error: Lengths of the two list are not the same.')
        dist = np.nan
    else:
        # equal weights
        # dist=np.sqrt(np.square(A-B).sum())
        # using varing weights
#         dist=np.multiply(np.absolute(A-B),np.divide(weights,float(np.sum(weights)))).sum()
#         dist = np.absolute(np.subtract(np.subtract(A-B),weights)).sum()
        dist = np.subtract(A,B)

    return dist

# cell 6 ####################################################################################
def calSimilarity(A,B,weights):
    """
    Note:
    - used by cell 18
    - optDifference: used cell 5

    Que:
    - what is A, B and weights looks like??
    - why np.absolute(optDifference-weights).sum() is the distance??
    """
    if (len(A) <> len(B)):
        print('Error: Lengths of the two list are not the same.')
        dist = np.nan
    else:
        # equal weights
        # dist=np.sqrt(np.square(A-B).sum())
        # using varing weights
        optDifference = calNormalizedDifference_OPT(A,B)
        dist=np.absolute(optDifference-weights).sum()
    return dist

# cell 7 ##########################################################
def collect_unnorm(Basin):
    """
    Modify:
    - os.path.join(dirname,'Decision_unnorm.dat')

    Note:
    - used by cell 8
    - read Decision_Unnorm.dat file from each node and write as one Decision_unnorm.txt
    - The final Decision_unnorm.txt file will be saved in Basin folder.
    - The final Decision_unnorm.txt file format will be node name + all parameter names as header and corresponding values for all nodes
    """

    fo = open('Decision_unnorm.txt','wb')
    for dirname in sorted(glob.glob(Basin+'*')):

        nodename = dirname.split('_')[1]
#         print nodename
        with open(os.path.join(dirname, 'Decision_Unnorm.dat'), 'r') as fd:
            for line in fd:
                pass
            lastline = line
        fo.write(nodename+','+lastline)
    fo.close()
    return

# cell 8 #########################################################
def genResult(Basin, NASA_RUNS):
    """
    modify:
    - pass NASA_RUNS as parameter
    - use os.path.join() to form the rootdir
    - Cols_un: used the parameter sequence from Decision_Unnorm.txt of each node, remove snow parameters, add Beta 0, Beat2
    - ColsInd_un: determined by len(Cols_un)
    - skiprows=1 (skip the 1st line of header)
    - Cols: formed by Cols_un to remove '_un' and add ['F1','F2','F3]
    - ColsInd: determined by len(Cols)
    - used subprocess to create the 'result.txt' file
    - ParList: formed by Cols_un to remove'_un'


    Que (important function to understand)
    # what is this function used for??
    # ColsInd_un and Cols_un how to determine this for ueb??
    # What is Beta parameters used for? determine PET function shape
    # how to determine ParList for ueb???

    Note:
    - purpose: find out the nodes and its corresponding parameter values.  (normalized A /unnormalized B values)
    - it needs 2nd auto-calibrationnode results as folders in Basin folder
    - the node results folder need to include Decision_Unnorm.dat file (2nd auto-cali)
    - it needs 'Decision000.dat' file and 'front000.dat' file in Basin folder
    - a Decision_unnorm.txt file is created in Basin folder
    - a result000.dat file is created in Basin folder
    - the function return result is a dataframe that includes the value for each parameter

    """

    cwd = os.getcwd()
    rootdir = os.path.join(NASA_RUNS, Basin)
    os.chdir(rootdir)

    Cols_un = [
               'NODE',
               'sac_UZTWM_un',
               'sac_UZFWM_un',
               'sac_LZTWM_un',
               'sac_LZFPM_un',
               'sac_LZFSM_un',
               'sac_UZK_un',
               'sac_LZPK_un',
               'sac_LZSK_un',
               'sac_ZPERC_un',
               'sac_REXP_un',
               'sac_PFREE_un',
               'Beta0_un',
               'Beta1_un',
               'Beta2_un']

    ColsInd_un = range(len(Cols_un))

    collect_unnorm(Basin)   # Decision_unnorm.txt file created under rootdir

    Dec_unnorm = pd.read_csv(os.path.join(rootdir, 'Decision_unnorm.txt'), delimiter=",", usecols=ColsInd_un, skiprows=1,
                             header=None, names=Cols_un, na_values=-999)
    Dec_unnorm['UZTWM_Rank_un'] = Dec_unnorm['sac_UZTWM_un'].rank(ascending=1)  # this is giving a rank value based on sac_UZTWM_un col, the higher the value, the higher the rank value (1 as lowest rank)
    Dec_unnorm['LZTWM_Rank_un'] = Dec_unnorm['sac_LZTWM_un'].rank(ascending=1)  # this is giving a rank value based on sac_LZTWM_un col

    Cols = ['F1', 'F2', 'F3'] +  [var.replace('_un','') for var in Cols_un[1:]]
    ColsInd = range(len(Cols))

    # Create result000.dat by merging front000.dat and Decision000.dat
    #!paste -d" "    front000.dat   Decision000.dat > result000.dat
    import subprocess
    paste = 'paste -d" "  front000.dat   Decision000.dat > result000.dat'
    process = subprocess.call(paste, shell=True).wait()
    
    Decision_000 = pd.read_csv(rootdir + 'result000.dat', delimiter=" ", usecols=ColsInd, skiprows=0, header=None,
                               names=Cols, na_values=-999)

    Decision_000['UZTWM_Rank'] = Decision_000['sac_UZTWM'].rank(ascending=1)
    Decision_000['LZTWM_Rank'] = Decision_000['sac_LZTWM'].rank(ascending=1)

    # result=Dec_unnorm.merge(Decision_000,left_on='UZTWM_Rank',right_on='UZTWM_Rank',how='inner')

    # Not using stats anymore for regionalization
    #     ColsInd=range(11)
    #     Cols=['NODE','Simulated Mean','Observed Mean','PBIAS','MonBias','MaxErr','PerAvgAbsErr','PerDRMS','MaxMonVolErr',
    #           'PerAvgAbsMonVolErr','PerMonVolRMSE']
    #     STAT1=pd.read_csv(rootdir+'stat1.txt',delim_whitespace=True,
    #                       usecols=ColsInd,skiprows=0,header=None,names=Cols,na_values=-999)

    #     ColsInd=range(8)
    #     Cols=['NODE','DRMS','DailyAvgAbsErr','AvgAbsMonVolErr','MonVolRMSE','CORR','OFFSET','SLOPE']
    #     STAT2=pd.read_csv(rootdir+'stat2.txt',delim_whitespace=True,
    #                       usecols=ColsInd,skiprows=0,header=None,names=Cols,na_values=-999)

    A = Decision_000.sort_values(by=['sac_UZTWM', 'sac_LZTWM'], ascending=[1, 0])
    B = Dec_unnorm.sort_values(by=['sac_UZTWM_un', 'sac_LZTWM_un'], ascending=[1, 0])
    A['NODE'] = B['NODE'].values

    result = pd.merge(A, B, on='NODE')

    #     result=pd.concat([A, B], axis=1)    # Concat does not combine row by row. Use merge.
    #     result=pd.merge(pd.merge(pd.concat([A, B], axis=1),STAT1,on='NODE'),STAT2,on='NODE')

    # Unnormalized values are actually scalers and want to recalculate them.
    Limits = genfromtxt(rootdir + Basin + '_' + str(result['NODE'][0]) + '/params1k.co.calb/param_limits.txt',
                        delimiter='\t', \
                        dtype=("|S11"), autostrip=True, comments="#")
    Max = [float(V) for V in Limits[:, 1]]
    Min = [float(V) for V in Limits[:, 2]]
    VMax = dict(zip(Limits[:, 0], Max))
    VMin = dict(zip(Limits[:, 0], Min))

    ParList = [var.replace('_un','') for var in Cols_un[1:]]

    for item in ParList:
        item_un = item + '_un'
        result[item_un] = (VMax[item] - VMin[item]) * result[item] + VMin[item]

    os.chdir(cwd)

    return result


# cell 10 #####################################################
# Select parameter set that only contains the calibration parameters
def filterParWeightSets(ParWeightSets):
    """
    Note:
    - used by cell 18
    - This is trying to filter out the parameter values that equal 0
    - return new_Sets {'MPHC2-DOLC2': {'sac_UZTWC': value'}}
    """
    new_Sets ={}
    for i,bcomb in enumerate(ParWeightSets.keys()):
        new=dict((k,v) for k,v in ParWeightSets[bcomb].items() if v != 0)
        new_Sets[bcomb]=new
    return new_Sets


# cell 11  ############################
def getVmaxVmin(parameter_limit_file):
    """
    Note:
    - need 'para_limits.txt' as input
    - load data from file as array [37 row, 3 col]
       array([['snow_SCF', '1.3', '0.9'],
              ['mfrng', '2.0', '0.1'],
              ...
             ])
    - create 2 dict, one for min one for max value with variable name
      {'Beta22': 10.0, 'sac_RSERV': 0.4, 'Beta21': 10.0, 'sac_UZK': 0.5,...}
    """

    Limits=genfromtxt(parameter_limit_file,delimiter='\t',\
    dtype=("|S11"), autostrip=True,comments="#")
    Max=[float(V) for V in Limits[:,1]]
    Min=[float(V) for V in Limits[:,2]]
    VMax=dict(zip(Limits[:,0],Max))
    VMin=dict(zip(Limits[:,0],Min))
    return VMax, VMin


# Calculation #######################################################################################
# cell 12 ###################################################
"""
Note:
- need to put parameter_limit_file same as python code level.


Que:
# when and how to use the code?? 
Ans: need to run 3 times of this code to find out the best parameters for all subwatershed in Mcphee
 -> auto-cali head watersheds 
 -> regionalization to find best parameters for DRRC2 and LCCC2 (if there are other close headwatersheds, they can be used) 
 -> auto-cali DOLC2 
 -> regionalization to find best parameters for DOLC2 based on best parameters determined for DRRC2 and LCCC2
 -> auto-cali MPHC2
 -> regionalization to find best parameters for MPHC2 based on best paramters determined for DRRC2, LCCC2, MPHC2

# FixOrNot: what is the index from? -1 mean not fixed, others means fixed. The index number corresponds to the determined node numbers

# IncludeForRegionalization: does this mean when it is specified as 0, it won't be used for regioinalization?
  Ans: always 1 

# what is NASA_RUNS folder: 
Ans: Use the 2nd ipython notebook nodes results
 -> include basin folder (e.g. 'DOLC2'), then this folder include auto-cali node folders (see cell 8 rootdir)

#ShortParList for ueb should only include sac parameters
"""

# Define basins to be included for the regionalization
# Basins = ['BUEC2','BSWC2','SKEC2']
Basins = np.array(['DRRC2','LCCC2'])
# To use predetermined parameter sets for specific basins, set the values with index of the final set of parameter
FixOrNot =np.array([-1,-1])
IncludeForRegionalization = np.array([1,1]) # always 1

Basins2 = Basins[IncludeForRegionalization>0]
FixOrNot2 = FixOrNot[IncludeForRegionalization>0]

NASA_RUNS=r'./Regionalization'
mcprundir=r'./RDHM_postprocessing' # not used
parameter_limit_file=r'./param_limits.txt'

VMax, VMin = getVmaxVmin(parameter_limit_file)
CAPfile = r'./CAP.csv'

# Read CAP parameters for the basins
cap=pd.read_csv(CAPfile,delimiter=",",skiprows=0,header=0,na_values=-999)

# Define parameter vector to be included for the similrity calculation
# or we can use all cap parameters for this claculation (?)
ShortParList = ['sac_UZTWM','sac_UZFWM','sac_LZTWM','sac_LZFSM','sac_LZFPM','sac_ZPERC','sac_UZK','sac_REXP','sac_PFREE','sac_LZSK','sac_LZPK']


# cell 13 #############################################################
# Read Calibrated Parameter Sets  for the basins to be regionalized
results={}
sources={}
for Basin in Basins:
    print Basin
    results[Basin]=genResult(Basin,NASA_RUNS)
    sources[Basin]=ColumnDataSource(results[Basin])
print results, sources

# cell 14 ###############################################################
"""
Que
- what is 'F2'? why set 20 as the value
  ans: F2 penalty function. default 20 
Note
- Normalize F1,F2,F3 result 
- calculate the mean of the normalized F1-F3 result: results[Basin]['Obj']
- rank the mean of normalized F1-F3 result: results[Basin]['obj_rank']

"""
# Normalize objective functions, calculate rank of mean normalized objective functions

for Basin in Basins:

    if results[Basin]['F2'].min() == 20:
        results[Basin]['F2'] = results[Basin]['F2'] - 20

    minF1 = results[Basin]['F1'].min()
    maxF1 = results[Basin]['F1'].max()
    minF2 = results[Basin]['F2'].min()
    maxF2 = results[Basin]['F2'].max()
    minF3 = results[Basin]['F3'].min()
    maxF3 = results[Basin]['F3'].max()

    F1_range = [minF1, maxF1]
    F2_range = [minF2, maxF2]
    F3_range = [minF3, maxF3]

    # Calculate normalized fitness function values
    # Made F1_norm to be 3-rd power to give more weighting on the lower values of the F1 (negative KG)
    # A lower F1 (negative KG) means a better fitness
    F1_norm = np.power((results[Basin]['F1'] - F1_range[0]) / (F1_range[1] - F1_range[0]), 3)
    F2_norm = np.power((results[Basin]['F2'] - F2_range[0]) / (F2_range[1] - F2_range[0]), 1)
    F3_norm = np.power((results[Basin]['F3'] - F3_range[0]) / (F3_range[1] - F3_range[0]), 1)
    F3_norm.replace(np.inf, 0)

    F_concat = pd.concat([F1_norm, F2_norm, F3_norm], axis=1)

    results[Basin]['F1_norm'] = F1_norm
    results[Basin]['F2_norm'] = F2_norm
    results[Basin]['F3_norm'] = F3_norm
    results[Basin]['Obj'] = F_concat.mean(axis=1)  # mean of normalized objective functions
    results[Basin]['obj_rank'] = results[Basin]['Obj'].rank(ascending=True)

# Cell 16 and 17 ######################################################################################
"""
Que:
- what is the purpose of this cell?
- How to decide the maxF1 and maxF2?

Note:
- cell 16: This is used to find out the nodes index that satisfy the requirement: F1 < maxF1 and F2 < maxF2
- cell 17: list the length of the node index that satisfy the requirement
- make the combination size smaller by first filter some bad nodes. 
- determine a standard value for the filter. may include minF1, minF2 for the filter
- use the auto-cali boxplot as a way to set the maxF1 maxF2 value to remove outlier

"""
# Manually Filter Pareto Solutions
# results2=results
maxF1={}
maxF2={}
maxF1['MPHC2']=-0.9
maxF2['MPHC2']=2000

m=[]
for i,item in enumerate(Basins2):
    print item
    if FixOrNot2[i] < 0:
        m.append(results[item][(results[item]['F1'] < maxF1[item]) & (results[item]['F2'] < maxF2[item])].index.values.tolist())
    else:
        m.append([FixOrNot2[i]])


for i,item in enumerate(m):
    print len(item)


# cell 18  ##########################################################################
"""
Note:
- used cell 6
- ParWeightSets: used cell 4
- new_Sets: used cell 10 
- n: create combination based on m list. (m list includes lists of best index of fixed basins, and possible indexs of basins to find the best paramters)

Que:
- best_2 = 100: how to determine this?
  ans: this just needs to be a high number 
"""
# # To minotor processing time
starttime = datetime.datetime.now()

ParWeightSets = calNormalizedDifference_CAP(Basins2)
new_Sets = filterParWeightSets(ParWeightSets)

n = list(itertools.product(*m))

# Initializing the best with an arbitrary high value
best_2 = 100

ncomb = comb(len(results), 2, exact=True)  # number of combinations for each two basins as 1 cobination

for k, a in enumerate(n):
    sum = 0
    #     print 'sum=',sum
    for i in range(0, len(a)):
        for j in range(i + 1, len(a)):
            comkey = '-'.join([Basins2[i], Basins2[j]])
            #             dist=euclideanDistance(np.array(results2[Basins[i]].iloc[[a[i]]][new.keys()]),np.array(results2[Basins[j]].iloc[[a[j]]][new.keys()]),new.values())
            dist = calSimilarity(np.array(results[Basins2[i]].iloc[[a[i]]][new_Sets[comkey].keys()]),
                                 np.array(results[Basins2[j]].iloc[[a[j]]][new_Sets[comkey].keys()]),
                                 new_Sets[comkey].values())
            #             print 'dist=',dist
            sum = sum + dist
            #             print 'sum=',sum
    if sum < best_2:
        best_2 = sum
        best_pareto_2 = [a, best_2 / ncomb]
    # print i, j, a[i], a[j], dist
    #     print k, a, sum
    if k % 1000 == 0:
        print k, sum / ncomb, np.array(a), best_pareto_2
print k, sum / ncomb, np.array(a), best_pareto_2
# b.loc[i] = np.append(np.array(a), sum / len(new))

endtime = datetime.datetime.now()
print best_pareto_2
print 'processing took ' + str((endtime - starttime).total_seconds()) + " seconds"

# cell 19-21 ####################################################################
"""
Used to print the best parameter with note value
"""
print(best_pareto_2)
print(Basins)
# print nodeId for the final parameter sets
for i in range(0,len(best_pareto_2[0])):
    print results[Basins2[i]].iloc[[best_pareto_2[0][i]]]['NODE']