"""
This is used to compare the snow17 workflow, ueb workflow, observation discharge data as contingency table.
(2015 Magnusson) Evaluating snow models with varying process representations for hydrological applications
(1992 Gerrity) A note on Gandin and Murphy's Equitable Skill score
Gerrity score function: http://www.cawcr.gov.au/projects/verification/#Methods_for_foreasts_of_continuous_variables
Hanssen and Kuipers (Peirce's skill score) http://www.cawcr.gov.au/projects/verification/

results:
- Dataframe: sort the values and calcualte the percentile, assign discharge in different level dry, low, medium, high
- CDF plot of observation discharge
- contingency table
- Gerrity score
"""

import os
import csv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plot_SAC_utility import get_obs_dataframe,get_sim_dataframe


# Default settings ########################################################
watershed = 'MPHC2'

obs_file = r'D:\Research_Data\Mcphee_MPHC2\MPHC2L_F.QME'
ueb_file = r'D:\Research_Data\Mcphee_MPHC2\ueb_best_time_series_2005\MPHC2_discharge_outlet.ts'
snow17_file = r'D:\Research_Data\Mcphee_MPHC2\snow17_best_time_series\MPHC2_discharge_outlet.ts'

snow17_skip = 136
ueb_skip = 121

start_time = '1989-10-1'
end_time = '2005-9-30'
dt = 6

result_dir = os.path.join(os.getcwd(), 'discharge_table_analysis_{}_{}'.format(watershed, 'all' if end_time == '' else start_time[:4] + end_time[:4]))
if not os.path.isdir(result_dir):
    os.makedirs(result_dir)


# step 1 get discharge data frame  ##############################################
obs_df = get_obs_dataframe(obs_file, start_time, end_time)
ueb_df = get_sim_dataframe(ueb_file, start_time=start_time, end_time=end_time, sim_skip=ueb_skip)
snow17_df = get_sim_dataframe(snow17_file, start_time=start_time, end_time=end_time, sim_skip=snow17_skip)

DF = pd.concat([obs_df, ueb_df, snow17_df], axis=1)  # obs should be first used by the loop to get the discharge threshold
DF.columns = ['obs', 'ueb', 'snow17']  # obs should be first used by the loop to get the discharge threshold
DF.dropna(inplace=True)
percentile_list = [0, 0.75, 0.90, 0.99, 1]
level_list = ['dry', 'low', 'medium', 'high']


# step 2 get the cdf and assign levels  #########################################
for name in DF.columns:
    sort_col = '{}_sorted'.format(name)
    percent_col = '{}_percent'.format(name)
    level_col = '{}_level'.format(name)
    DF[sort_col] = np.sort(DF[name], axis=0)
    DF[percent_col] = 1.*np.arange(len(DF))/(len(DF)-1)
    DF[level_col] = ''

    # get discharge level threshold
    if name == 'obs':
        discharge_threshold = []
        for percentile in percentile_list[1:]:
            value = DF[DF[percent_col] <= percentile][sort_col].ix[-1]
            discharge_threshold.append(value)
        # CDF plot for observation
        fig, ax = plt.subplots()
        plt.margins(0)
        DF.plot(x=sort_col, y=percent_col, ax=ax,
                title='Cumulative Distribution of observation discharge at {}'.format(watershed),
                legend=False)
        ax.set_xlabel('discharge(cms)')
        ax.set_ylabel('Probability to not exceed')
        for x, y in zip(discharge_threshold[:-1], percentile_list[1:-1]):
            ax.plot([x, x], [y, 0], color='grey', linestyle=':')
            ax.plot([0, x], [y, y], color='grey', linestyle=':')

        ax.set_yticks(percentile_list[:-1])
        ax.set_xticks(discharge_threshold)
        fig.savefig(os.path.join(result_dir, 'cdf_obs.png'))

    # assign discharge level
    for i in range(0, len(level_list)):
        if i == 0:
            DF[level_col][(DF[name] <= discharge_threshold[i])] = level_list[i]
        elif i == len(level_list)-1:
            DF[level_col][(DF[name] > discharge_threshold[i-1])] = level_list[i]
        else:
            DF[level_col][(DF[name] > discharge_threshold[i-1]) & (DF[name] <= discharge_threshold[i])] = level_list[i]
DF.to_csv(os.path.join(result_dir, 'discharge_DF.csv'))

with open(os.path.join(result_dir, 'discharge_threshold.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerows([percentile_list[1:], discharge_threshold])


# step 3 make the contingency table and Gerrity score #########################################
GS_result = []
PSS_result = []
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

    GS = 1./N * (S_matrix*N_matrix.values).sum().sum()
    GS_result.append([name, GS])

    mul_df = S_matrix*N_matrix.values
    mul_df['total_score'] = mul_df.sum(axis=1)
    mul_df.ix['total_score'] = mul_df.sum(axis=0)
    mul_df.to_csv(os.path.join(result_dir,'multiply_matrix_{}.csv'.format(name)))

    # Pierce score
    K = len(level_list)
    N = table_df.ix['total'].sum()
    cal_df = pd.DataFrame()
    P_matrix = table_df
    P_matrix['total'] = table_df.sum(axis=1)
    P_matrix = P_matrix / N
    cal_df['pii'] = [P_matrix.ix[i, i] for i in range(0, K)]
    cal_df['pi'] = [P_matrix.ix['total', i] for i in range(0, K)]
    cal_df['qi'] = [P_matrix['total'].ix[i] for i in range(0, K)]
    cal_df['piqi'] = cal_df['pi'] * cal_df['qi']
    cal_df['pipi'] = cal_df['pi'] ** 2
    PSS = (cal_df['pii'].sum() - cal_df['piqi'].sum()) / (1 - cal_df['pipi'].sum())
    PSS_result.append([name, PSS])

    cal_df.to_csv(os.path.join(result_dir, 'PSS_cal_df_{}.csv'.format(name)))


with open(os.path.join(result_dir, 'GS_result.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerows(GS_result)

with open(os.path.join(result_dir, 'PSS_result.csv'), 'w') as f:
    writer = csv.writer(f)
    writer.writerows(PSS_result)

cal_df.to_csv(os.path.join(result_dir, 'cal_df.csv'))
S_matrix.to_csv(os.path.join(result_dir, 'S_matrix.csv'))

print 'analysis is done'