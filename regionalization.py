"""
This is the regionalization code from RTI.
"""

# import
#
import os
import pandas as pd
from numpy import genfromtxt
import numpy as np
from bokeh.charts import BoxPlot
from bokeh.plotting import figure, show, ColumnDataSource, curdoc,gridplot
from bokeh.models import HoverTool, TapTool,HBox,VBox,BoxSelectTool, Range1d, Circle, LabelSet
from bokeh.models.widgets import Dropdown, Button, TextInput
from bokeh.io import output_notebook, push_notebook
import glob

import itertools
import datetime
from scipy.special import comb

# define functions  ##############################################################################################

def GetHydrographs2(Basin, PID):
    QSRC = ColumnDataSource(data=dict(Time=[], Obs=[], Mod=[]))
    rootdir = NASA_RUNS + Basin + '_96' + '\\'
    startDate = '10-1-1988 06:00:00'
    print(rootdir + Basin + '_' + PID + '\\' + Basin + '_discharge_outlet.ts')
    F = open(rootdir + Basin + '_' + PID + '\\' + Basin + '_discharge_outlet.ts', 'r')
    # F=open('/projects/NASA/calb/input/mcp3/decks/NASA_RUNS/discharge_5yr/BUEC2_78236/BUEC2_discharge_outlet.ts','r')
    for i, line in enumerate(F):
        if line.startswith('$'):
            comment = i
    F.close()
    mod_data = genfromtxt(rootdir + Basin + '_' + PID + '\\' + Basin + '_discharge_outlet.ts', skip_header=comment + 3,
                          dtype=float)
    # mod_data = genfromtxt('/projects/NASA/calb/input/mcp3/decks/NASA_RUNS/discharge_5yr/BUEC2_78236/BUEC2_discharge_outlet.ts', skip_header=comment+3, dtype=float)
    dates = pd.date_range(startDate, periods=len(mod_data[:, 3]), freq='6H')
    Mod = pd.DataFrame(index=dates, columns=['Mod'])
    Mod['Mod'] = mod_data[:, 3]
    Mod['Mod'] = Mod['Mod'].mul(3.2808 ** 3)  # cms to cfs
    Mod = Mod.resample('D').mean()
    obs_filename = glob.glob('Z:\\NASA\\hisobs\\' + Basin + '*_F.QME')
    Obs = pd.read_table(obs_filename[0], index_col=0, parse_dates=True, sep=',', skiprows=3, header=None)
    Obs.rename(columns={1: 'Obs'}, inplace=True)
    Obs['Obs'][Obs['Obs'] < 0] = np.nan
    Obs = Obs.resample('1D').mean()  # Resample to 3 hour


def euclideanDistance(A, B, weights):
    if (len(A) <> len(B)):
        print('Error: Lengths of the two list are not the same.')
        dist = np.nan
    else:
        # equal weights
        # dist=np.sqrt(np.square(A-B).sum())
        # using varing weights
        dist = np.multiply(np.absolute(A - B), np.divide(weights, float(np.sum(weights)))).sum()
    return dist


# Calculate the parameter weights between basins
def calNormalizedDifference_CAP(Basins):

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

    #     START=max(Obs.index[0],Mod.index[0])
    #     END=min(Obs.index[-1],Mod.index[-1])

    START = Mod.index[0]
    END = Mod.index[-1]

    ix = pd.DatetimeIndex(start=START, end=END, freq='D')
    Obs = Obs.reindex(ix)

    Obs_Trim = Obs[(Obs.index >= START) & (Obs.index <= END)]
    # QSRC=ColumnDataSource(data=dict(Time=[],Obs=[],Mod=[]))
    QSRC.data = dict(Time=Obs_Trim.index, Obs=Obs_Trim.values.flatten(), Mod=Mod.values.flatten())

    return QSRC


def calNormalizedDifference_OPT(A,B):
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


def calSimilarity(A,B,weights):
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


def collect_unnorm(Basin):
    fo = open('Decision_unnorm.txt','wb')
    for dirname in sorted(glob.glob(Basin+'*')):

        nodename = dirname.split('_')[1]
#         print nodename
        with open(dirname+'\\Decision_Unnorm.dat','r') as fd:
            for line in fd:
                pass
            lastline = line
        fo.write(nodename+','+lastline)
    fo.close()
    return


def genResult(Basin):
    #     rootdir=NASA_RUNS+'NSGAII_64_'+Basin+'\\'
    cwd = os.getcwd()
    rootdir = NASA_RUNS + Basin + '_96' + '\\'
    os.chdir(rootdir)

    ColsInd_un = range(18)
    Cols_un = ['NODE',
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
               'snow_SCF_un',
               'snow_MFMAX_un',
               'snow_MFMIN_un',
               'snow_UADJ_un',
               'snow_PXTMP_un',
               'Beta0_un']

    collect_unnorm(Basin)

    Dec_unnorm = pd.read_csv(rootdir + 'Decision_unnorm.txt', delimiter=",", usecols=ColsInd_un, skiprows=0,
                             header=None, names=Cols_un, na_values=-999)
    Dec_unnorm['UZTWM_Rank_un'] = Dec_unnorm['sac_UZTWM_un'].rank(ascending=1)
    Dec_unnorm['LZTWM_Rank_un'] = Dec_unnorm['sac_LZTWM_un'].rank(ascending=1)

    ColsInd = range(20)
    Cols = ['F1', 'F2', 'F3', 'sac_UZTWM', 'sac_UZFWM', 'sac_LZTWM', 'sac_LZFPM', 'sac_LZFSM', 'sac_UZK', 'sac_LZPK',
            'sac_LZSK', 'sac_ZPERC',
            'sac_REXP', 'sac_PFREE', 'snow_SCF', 'snow_MFMAX', 'snow_MFMIN', 'snow_UADJ', 'snow_PXTMP', 'Beta0']

    # Create result000.dat by merging front000.dat and Decision000.dat
    #!paste -d" "    front000.dat   Decision000.dat > result000.dat
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

    ParList = ['sac_UZTWM', 'sac_UZFWM', 'sac_LZTWM', 'sac_LZFPM', 'sac_LZFSM', 'sac_UZK', 'sac_LZPK', 'sac_LZSK',
               'sac_ZPERC',
               'sac_REXP', 'sac_PFREE', 'snow_SCF', 'snow_MFMAX', 'snow_MFMIN', 'snow_UADJ', 'snow_PXTMP', 'Beta0']

    for item in ParList:
        item_un = item + '_un'
        result[item_un] = (VMax[item] - VMin[item]) * result[item] + VMin[item]

    os.chdir(cwd)

    return result


# Calculate the parameter weights between basins
def calWeights(Basins, threshold=0.7):

    # Parameter Weight Dictionary
    ParWeightSets={}

    # create list of basin combinations
    comblist=list(itertools.combinations(Basins,2))

    # Calculate parameter weights between the pairs of the basins
    for i in comblist:
        ParWeights={}
        for par in ShortParList:
            par_a=cap[cap['CH5_ID']==i[0]][par].values[0]
            par_b=cap[cap['CH5_ID']==i[1]][par].values[0]
            similarity=1-abs(par_a-par_b)/(VMax[par]-VMin[par])

            # We may not consider some eparameters in similaruty calculation if they are very different
            if similarity < threshold:
                ParWeights[par]=0
            else:
                ParWeights[par]=similarity

        ParWeightSets['-'.join(i)]=ParWeights
    return ParWeightSets


# Select parameter set that only contains the calibration parameters
def filterParWeightSets(ParWeightSets):
    new_Sets ={}
    for i,bcomb in enumerate(ParWeightSets.keys()):
        new=dict((k,v) for k,v in ParWeightSets[bcomb].items() if v != 0)
        new_Sets[bcomb]=new
    return new_Sets

def getVmaxVmin(parameter_limit_file):
    Limits=genfromtxt(parameter_limit_file,delimiter='\t',\
    dtype=("|S11"), autostrip=True,comments="#")
    Max=[float(V) for V in Limits[:,1]]
    Min=[float(V) for V in Limits[:,2]]
    VMax=dict(zip(Limits[:,0],Max))
    VMin=dict(zip(Limits[:,0],Min))
    return VMax, VMin


# Calculation #######################################################################################
# Cell 12 #######
# Define basins to be included for the regionalization
# Basins = ['BUEC2','BSWC2','SKEC2']
Basins = np.array(['DRRC2','LCCC2','DOLC2','MPHC2'])
# To use predetermined parameter sets for specific basins, set the values with index of the final set of parameter
FixOrNot =np.array([67,25,52,-1])
IncludeForRegionalization = np.array([1,1,1,1])

Basins2 = Basins[IncludeForRegionalization>0]
FixOrNot2 = FixOrNot[IncludeForRegionalization>0]

NASA_RUNS='Z:\\NASA\\calb\\input\\mcp3\\decks\\Regionalization\\'
mcprundir='Z:\\NASA\\calb\\input\\mcp3\\decks\\RDHM_postprocessing\\'
parameter_limit_file='Z:\\NASA\\calb\\input\\mcp3\\decks\\Regionalization\\param_limits.txt'

VMax, VMin = getVmaxVmin(parameter_limit_file)
CAPfile = r'C:\Projects\1336_NASA\BasinCharacteristics\CAP.csv'

# Read CAP parameters for the basins
cap=pd.read_csv(CAPfile,delimiter=",",skiprows=0,header=0,na_values=-999)


# Define parameter vector to be included for the similrity calculation
# or we can use all cap parameters for this claculation (?)
ShortParList = ['sac_UZTWM','sac_UZFWM','sac_LZTWM','sac_LZFSM','sac_LZFPM','sac_ZPERC','snow_MFMAX','snow_MFMIN','sac_UZK','sac_REXP','sac_PFREE','sac_LZSK','sac_LZPK','snow_UADJ']


# cell 13 ##################
# Read Calibratioed Parameter Sets  for the basins to be regionalized
results={}
sources={}
for Basin in Basins:
    print Basin
    results[Basin]=genResult(Basin)
    sources[Basin]=ColumnDataSource(results[Basin])


# cell 14 #################
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


# cell 15  ###################
import warnings

warnings.filterwarnings('ignore')

output_notebook()

xrange = Range1d(start=-1, end=1)

TOOLS = "pan,box_zoom,wheel_zoom,tap,box_select,lasso_select,reset,hover,help"
selected_circle = Circle(fill_alpha=1, fill_color="firebrick", line_color='black')

PlotShortParList = ['F1', 'F2', 'F3'] + ShortParList + ['snow_SCF', 'Beta0_un']
Colors = ['blue', 'red', 'green', 'purple', 'orange']

for i, par in enumerate(PlotShortParList):

    if par not in ('F1', 'F2', 'F3', 'snow_SCF', 'Beta0_un', 'Beta1_un', 'Beta2_un'):
        globals()["PLOT{0}".format(i)] = figure(title=par, tools=TOOLS, width=120, height=250, x_range=xrange,
                                                y_range=Range1d(start=VMin[par.split('_un')[0]],
                                                                end=VMax[par.split('_un')[0]]))
    else:
        globals()["PLOT{0}".format(i)] = figure(title=par, tools=TOOLS, width=120, height=250, x_range=xrange)

    if par in ('F1', 'F2', 'F3', 'Beta0_un', 'Beta1_un', 'Beta2_un'):
        yvar = par
    else:
        yvar = par + '_un'

    for j in range(0, len(Basins)):
        xloc = -1 + (j + 1) * (2. / (len(FixOrNot) + 1))
        globals()["x{0}".format(i)] = []
        for k in range(0, len(results[Basins[j]])):
            globals()["x{0}".format(i)].append(xloc)
        globals()["renderer1{0}".format(i)] = globals()["PLOT{0}".format(i)].circle(globals()["x{0}".format(i)],
                                                                                    yvar, source=sources[Basins[j]],
                                                                                    alpha=0.1, color=Colors[j], size=6,
                                                                                    selection_color='blue')
        if par not in ('F1', 'F2', 'F3', 'snow_SCF', 'Beta0_un', 'Beta1_un', 'Beta2_un'):
            globals()["PLOT{0}".format(i)].circle([xloc], cap[cap['CH5_ID'] == Basins[j]][par].values[0], alpha=1,
                                                  color='black', size=8)

        if FixOrNot[j] > 0:
            globals()["PLOT{0}".format(i)].circle([xloc], results[Basins[j]].iloc[FixOrNot[j]][yvar], alpha=1,
                                                  color=Colors[j], size=12)

            # Adding Legend in a separate plot
labelsource = ColumnDataSource(
    data=dict(x=[0] * (len(Basins) + 1), y=range(0, len(Basins) + 1), names=np.append(Basins, ['CAP'])))
labels = LabelSet(x='x', y='y', text='names', level='glyph', x_offset=10, y_offset=-10, source=labelsource,
                  text_font_size='10pt')
i += 1
globals()["PLOT{0}".format(i)] = figure(width=120, height=250, x_range=Range1d(start=-0.2, end=2),
                                        y_range=Range1d(start=-1, end=len(Basins) + 1))

globals()["PLOT{0}".format(i)].circle([0], [len(Basins)], alpha=1, color='black', size=12)
for j in range(0, len(Basins)):
    globals()["PLOT{0}".format(i)].circle([0], [j], alpha=1, color=Colors[j], size=12)

globals()["PLOT{0}".format(i)].circle(x='x', y='y', source=labelsource, size=0)
globals()["PLOT{0}".format(i)].add_layout(labels)
globals()["PLOT{0}".format(i)].xaxis.major_label_text_font_size = '0pt'
globals()["PLOT{0}".format(i)].xaxis.major_tick_line_color = None
globals()["PLOT{0}".format(i)].xaxis.minor_tick_line_color = None
globals()["PLOT{0}".format(i)].yaxis.major_label_text_font_size = '0pt'
globals()["PLOT{0}".format(i)].yaxis.major_tick_line_color = None
globals()["PLOT{0}".format(i)].yaxis.minor_tick_line_color = None
globals()["PLOT{0}".format(i)].xgrid.grid_line_color = None
globals()["PLOT{0}".format(i)].ygrid.grid_line_color = None

# textbox = TextInput(title="PID: ", value=str(results['DRGC2']['NODE'][0]))
# textbox.on_change('value',update_data)

p = gridplot([[PLOT0, PLOT1, PLOT2, PLOT3, PLOT4, PLOT5, PLOT6],
              [PLOT7, PLOT8, PLOT9, PLOT10, PLOT11, PLOT12, PLOT13],
              [PLOT14, PLOT15, PLOT16, PLOT17, PLOT18, PLOT19]
              #               [PLOT14,PLOT15,PLOT16,PLOT17,PLOT18,PLOT19,PLOT20],
              #               [textbox],
              ])


def callback(attrname, old, new):
    print 'Hello2..."'
    return


# print sources['DRGC2'].selected

# renderer11.on_change('selected',callback)



show(p)

# curdoc().add_root(p)



# cell 16 ##############################
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


# cell 17 #############################
for i,item in enumerate(m):
    print len(item)


# cell 18 ##############################
# # To minotor processing time
starttime = datetime.datetime.now()

ParWeightSets = calNormalizedDifference_CAP(Basins2)
new_Sets = filterParWeightSets(ParWeightSets)

n = list(itertools.product(*m))

# Initializing the best with an arbitrary high value
best_2 = 100

ncomb = comb(len(results), 2, exact=True)  # number of combinations

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



# cell 19-20  ##############################
# best_pareto_2 = [(67, 25, 52, 65L), 3.3701952266661004]
print(best_pareto_2)

print(Basins)


# cell 21  ####################################
# print nodeId for the final parameter sets
for i in range(0,len(best_pareto_2[0])):
    print results[Basins2[i]].iloc[[best_pareto_2[0][i]]]['NODE']


# cell 22  #####################################
# All 5 basins
FixOrNot3 = np.copy(FixOrNot)
FixOrNot3[IncludeForRegionalization > 0] = best_pareto_2[0]
# FixOrNot3 = [61,2,64,72,98]

import warnings

warnings.filterwarnings('ignore')

output_notebook()

xrange = Range1d(start=-1, end=1)

TOOLS = "pan,box_zoom,wheel_zoom,tap,box_select,lasso_select,reset,hover,help"
selected_circle = Circle(fill_alpha=1, fill_color="firebrick", line_color='black')

PlotShortParList = ['F1', 'F2', 'F3'] + ShortParList + ['snow_SCF', 'Beta0_un']
Colors = ['blue', 'red', 'green', 'purple', 'orange']

for i, par in enumerate(PlotShortParList):
    if par not in ('F1', 'F2', 'F3', 'snow_SCF', 'Beta0_un', 'Beta1_un', 'Beta2_un'):
        globals()["PLOT{0}".format(i)] = figure(title=par, tools=TOOLS, width=120, height=250, x_range=xrange,
                                                y_range=Range1d(start=VMin[par.split('_un')[0]],
                                                                end=VMax[par.split('_un')[0]] * 1.3))
    else:
        globals()["PLOT{0}".format(i)] = figure(title=par, tools=TOOLS, width=120, height=250, x_range=xrange)

    if par in ('F1', 'F2', 'F3', 'Beta0_un', 'Beta1_un', 'Beta2_un'):
        yvar = par
    else:
        yvar = par + '_un'

    for j in range(0, len(Basins)):
        xloc = -1 + (j + 1) * (2. / (len(FixOrNot3) + 1))
        globals()["x{0}".format(i)] = []
        for k in range(0, len(results[Basins[j]])):
            globals()["x{0}".format(i)].append(xloc)
        globals()["renderer1{0}".format(i)] = globals()["PLOT{0}".format(i)].circle(globals()["x{0}".format(i)],
                                                                                    yvar, source=sources[Basins[j]],
                                                                                    alpha=0.1, color=Colors[j], size=6,
                                                                                    selection_color='blue')
        if FixOrNot3[j] > 0:
            globals()["PLOT{0}".format(i)].circle([xloc], results[Basins[j]].iloc[FixOrNot3[j]][yvar], alpha=1,
                                                  color=Colors[j], size=12)

        if par not in ('F1', 'F2', 'F3', 'snow_SCF', 'Beta0_un', 'Beta1_un', 'Beta2_un'):
            globals()["PLOT{0}".format(i)].circle([xloc], cap[cap['CH5_ID'] == Basins[j]][par].values[0], alpha=1,
                                                  color='black', size=8)

        globals()["PLOT{0}".format(i)].xaxis.major_label_text_font_size = '0pt'
        globals()["PLOT{0}".format(i)].xaxis.major_tick_line_color = None
        globals()["PLOT{0}".format(i)].xaxis.minor_tick_line_color = None

# Adding Legend in a separate plot
labelsource = ColumnDataSource(
    data=dict(x=[0] * (len(Basins) + 1), y=range(0, len(Basins) + 1), names=np.append(Basins, ['CAP'])))
labels = LabelSet(x='x', y='y', text='names', level='glyph', x_offset=10, y_offset=-10, source=labelsource,
                  text_font_size='10pt')
i += 1
globals()["PLOT{0}".format(i)] = figure(width=120, height=250, x_range=Range1d(start=-0.2, end=2),
                                        y_range=Range1d(start=-1, end=len(Basins) + 1))

globals()["PLOT{0}".format(i)].circle([0], [len(Basins)], alpha=1, color='black', size=12)
for j in range(0, len(Basins)):
    globals()["PLOT{0}".format(i)].circle([0], [j], alpha=1, color=Colors[j], size=12)

globals()["PLOT{0}".format(i)].circle(x='x', y='y', source=labelsource, size=0)
globals()["PLOT{0}".format(i)].add_layout(labels)
globals()["PLOT{0}".format(i)].xaxis.major_label_text_font_size = '0pt'
globals()["PLOT{0}".format(i)].xaxis.major_tick_line_color = None
globals()["PLOT{0}".format(i)].xaxis.minor_tick_line_color = None
globals()["PLOT{0}".format(i)].yaxis.major_label_text_font_size = '0pt'
globals()["PLOT{0}".format(i)].yaxis.major_tick_line_color = None
globals()["PLOT{0}".format(i)].yaxis.minor_tick_line_color = None
globals()["PLOT{0}".format(i)].xgrid.grid_line_color = None
globals()["PLOT{0}".format(i)].ygrid.grid_line_color = None

# textbox = TextInput(title="PID: ", value=str(results['DRGC2']['NODE'][0]))
# textbox.on_change('value',update_data)

p = gridplot([[PLOT0, PLOT1, PLOT2, PLOT3, PLOT4, PLOT5, PLOT6],
              [PLOT7, PLOT8, PLOT9, PLOT10, PLOT11, PLOT12, PLOT13],
              [PLOT14, PLOT15, PLOT16, PLOT17, PLOT18, PLOT19]
              #               [PLOT14,PLOT15,PLOT16,PLOT17,PLOT18,PLOT19,PLOT20],
              #               [textbox],
              ])


def callback(attrname, old, new):
    print 'Hello2..."'
    return


# print sources['DRGC2'].selected

# renderer11.on_change('selected',callback)



show(p)

# curdoc().add_root(p)


# cell 23  ###########################
print(Basins)
for item in range(0,len(Basins)):
    print int(results[Basins[item]].iloc[best_pareto_2[0][item]]['NODE']),results[Basins[item]].iloc[best_pareto_2[0][item]]['F1'],results[Basins[item]].iloc[best_pareto_2[0][item]]['F2'],results[Basins[item]].iloc[best_pareto_2[0][item]]['F3']


# cell 24 #################################
QSRCALL={}
Plots=[]
for i,Basin in enumerate(Basins2):
    nodeid = int(results[Basin].iloc[best_pareto_2[0][i]]['NODE'])
    print nodeid
    QSRCALL[Basin]=GetHydrographs2(Basin,str(nodeid))
    globals()['Q{0}'.format(i+1)]=figure(title=Basin,height=250, width=850,x_axis_type="datetime",tools=TOOLS)
    globals()['Q{0}'.format(i+1)].line('Time','Mod',source=QSRCALL[Basin],line_color='red',line_width=2,legend='Simulated')
    globals()['Q{0}'.format(i+1)].circle('Time','Obs',source=QSRCALL[Basin],size=1,color='black',legend='Observed')
    Plots.append(globals()['Q{0}'.format(i+1)])
q=gridplot(zip(*[iter(Plots)]*1)) #Convert list to list of list. *1 means one to each list.
show(q)