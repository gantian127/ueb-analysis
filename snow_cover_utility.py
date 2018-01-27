"""
This includes  the utility functions to support snow cover area analysis

"""
import pandas as pd
import numpy as np
import math



def get_sim_dataframe(sim_file, start_time='', end_time='', sim_skip=91, time_change_ori=('24', '25'), time_change_new=('23', '1'), column_name=''):
    # get sim daily data
    raw_sim = pd.read_csv(sim_file, skiprows=sim_skip, header=None, names=['raw'])
    sim_data = raw_sim['raw'].str.split('\s+', expand=True)
    sim_data.rename(columns={3: 'sim'}, inplace=True)
    sim_data['sim'] = sim_data['sim'].astype(float)
    for i in range(0, len(time_change_ori)):
        sim_data[[2]] = sim_data[[2]].apply(lambda x: x.replace(time_change_ori[i], time_change_new[i]))
    sim_data['time'] = sim_data[[1, 2]].apply(lambda x: ''.join(x), axis=1)
    sim_data['time'] = pd.to_datetime(sim_data['time'], format='%d%m%y%H')
    sim_data.drop([0, 1, 2], axis=1, inplace=True)
    sim_data.ix[sim_data.sim < 0, 'sim'] = np.nan
    sim = sim_data.set_index('time').groupby(pd.TimeGrouper(freq='D'))['sim'].mean()

    if start_time and end_time:
        sim = sim[(sim.index >= start_time) & (sim.index <= end_time)]

    return sim


def get_statistics(sim, obs):
    # calculate statistics
    stat_df = pd.DataFrame({'discharge': sim, 'observation': obs},
                             columns=['discharge', 'observation']
                           )

    # rmse: sqrt(mean(sum((Qs-Qo)**2)))
    stat_df['valDiff'] = stat_df['observation'] - stat_df['discharge']
    valDiff_mean = stat_df['valDiff'].mean()
    stat_df['valDiffSq'] = stat_df['valDiff'].apply(lambda x: x ** 2)
    valDiffSq_mean = stat_df['valDiffSq'].mean()
    rmse = math.sqrt(valDiffSq_mean)

    # nse: 1 - sum ((Qs-Qo)**2) / sum((Qo-Qomean)**2)
    stat_df['valDiffA'] = stat_df['valDiff'].apply(lambda x: abs(x))
    valDiffA_mean = stat_df['valDiffA'].mean()
    obs_mean = stat_df['observation'].mean()
    valDiffSq_sum = stat_df['valDiffSq'].sum()

    stat_df['valDiffMean'] = stat_df['observation'].apply(lambda x: x - obs_mean)
    stat_df['valDiffSqmean'] = stat_df['valDiffMean'].apply(lambda x: x ** 2)
    valDiffSqmean_sum = stat_df['valDiffSqmean'].sum()

    nse = 1 - (valDiffSq_sum / valDiffSqmean_sum)
    mae = valDiffA_mean

    # correlation coefficient
    r = stat_df[['observation', 'discharge']].corr()['observation'][1]

    # bias: Qs-Qo
    stat_df['bias'] = stat_df['discharge'] - stat_df['observation']
    bias = stat_df['bias'].mean()

    return {'rmse': rmse, 'nse': nse, 'mae': mae, 'r': r, 'bias': bias}
