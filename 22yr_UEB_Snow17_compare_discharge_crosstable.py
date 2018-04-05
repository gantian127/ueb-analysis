"""
This is used to compare the snow17 workflow, ueb workflow, observation discharge data as contingency table.
(2015 Magnusson) Evaluating snow models with varying process representations for hydrological applications
Gerrity score function: http://www.cawcr.gov.au/projects/verification/#Methods_for_foreasts_of_continuous_variables

results:
- plot of probability distribution
- contingency table and Gerrity score
"""

import os
import csv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plot_SAC_utility import get_obs_dataframe,get_sim_dataframe


# Default settings ########################################################
watershed = 'DOLC2'
watershed_area = 0

snow17_file = r'D:\Research_Data\Mcphee_DOLC2\snow17_best_time_series\DOLC2_discharge_outlet.ts'
ueb_file = r'D:\Research_Data\Mcphee_DOLC2\UEB_best_time_series\DOLC2_discharge_outlet.ts'
obs_file = r'D:\Research_Data\Mcphee_DOLC2\DOLC2L_F.QME'

snow17_skip = 136
ueb_skip = 121

start_time = '1989-10-1'
end_time = '2010-9-30'
dt = 6

result_dir = os.path.join(os.getcwd(), 'discharge_table_analysis_{}_{}'.format(watershed, 'all' if end_time == '' else start_time[:4] + end_time[:4]))
if not os.path.isdir(result_dir):
    os.makedirs(result_dir)


# step 1 get discharge data frame  ##############################################
obs_df = get_obs_dataframe(obs_file, start_time, end_time)
ueb_df = get_sim_dataframe(ueb_file, start_time=start_time, end_time=end_time, sim_skip=ueb_skip)
snow17_df = get_sim_dataframe(snow17_file, start_time=start_time, end_time=end_time, sim_skip=snow17_skip)

DF = pd.concat([ueb_df, snow17_df, obs_df], axis=1)
DF.columns = ['obs', 'ueb', 'snow17']  # obs should be first used by the loop to get the discharge threshold
percentile_list = [0, 0.75, 0.90, 0.99, 1]
level_list = ['dry', 'low', 'medium', 'high']


# step 2 get the cdf and assign levels  #########################################
for name in DF.columns:
    sort_col = '{}_sorted'.format(name)
    percent_col = '{}_percent'.format(name)
    level_col = '{}_level'.format(name)
    DF[sort_col] = np.sort(DF[name], axis=0)
    DF[percent_col] = 1.*np.arange(len(obs_df))/(len(obs_df)-1)

    # get discharge level threshold
    if name == 'obs':
        discharge_threshold = []
        for percentile in percentile_list[1:]:
            value = DF[DF[percent_col] < percentile][sort_col].ix[-1]
            discharge_threshold.append(value)

    # assign discharge level
    DF[level_col] = level_list[0]
    for i in range(0, len(level_list)-1):
        DF[level_col][(DF[name] >= discharge_threshold[i]) & (DF[name] < discharge_threshold[i+1])] = level_list[i+1]

DF.to_csv(os.path.join(result_dir, 'discharge_level.csv'))

with open(os.path.join(result_dir, 'discharge_threshold.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerows([percentile_list[1:], discharge_threshold])


# step 3 make the contingency table and Gerrity score #########################################
GS_result = []
for name in ['snow17', 'ueb']:
    # contingency table
    table_df = pd.DataFrame(columns=level_list, index=level_list)
    for level in level_list:
        model_levels, counts = np.unique(DF[DF['obs_level'] == level][name+'_level'], return_counts=True)
        for model_level in model_levels:
            table_df[level].at[model_level] = counts[np.where(model_levels == model_level)].item()
    table_df.fillna(0, inplace=True)
    table_df.ix['total'] = table_df.sum(axis=0)
    table_df.to_csv(os.path.join(result_dir, 'table_{}.csv'.format(name)))

    # Gerrity score
    K = len(level_list)
    b = 1./(K-1)
    N = table_df.ix['total'].sum()
    N_matrix = table_df.ix[:-1]

    cal_df = pd.DataFrame(index=range(1, K+1))
    cal_df['level'] = level_list
    cal_df['n(Oi)'] = table_df.ix['total'].tolist()
    cal_df['Pi'] = 1. * cal_df['n(Oi)']/cal_df['n(Oi)'].sum()
    cal_df['Pi_cumsum'] = cal_df['Pi'].cumsum()
    cal_df['D(n)'] = (1-cal_df['Pi_cumsum']) / cal_df['Pi_cumsum']
    cal_df['R(n)'] = 1. /cal_df['D(n)']

    S_matrix = pd.DataFrame(np.zeros((K, K)), index=range(1, K+1), columns=range(1, K+1))
    for i in range(1, K+1):
        for j in range(1, K+1):
            R_sum = cal_df['R(n)'].ix[1:i-1].sum()
            D_sum = cal_df['D(n)'].ix[j:K-1].sum()

            if i == j:
                S_matrix.ix[i, j] = b*(R_sum+D_sum)
            elif j > i:
                S_matrix.ix[i, j] = b*(R_sum+D_sum-(j-i))
                S_matrix.ix[j, i] = S_matrix.ix[i, j]
            #
            # print i, j
            # print ai_inv_sum
            # print ai_sum

    GS = 1./N * (S_matrix*N_matrix.values).sum().sum()
    GS_result.append([name, GS])
    cal_df.to_csv(os.path.join(result_dir, 'cal_df_{}.csv'.format(name)))
    S_matrix.to_csv(os.path.join(result_dir, 'S_matrix_{}.csv'.format(name)))

with open(os.path.join(result_dir, 'GS_result.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerows(GS_result)