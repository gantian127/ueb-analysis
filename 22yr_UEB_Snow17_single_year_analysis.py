"""
This is using the RDHM time series to analyze the SWE and discharge at each year (snow17 vs ueb workflow)
Each year result are saved as single graph

requirements:
- put utility py file
- the output should be from the updated code that has mm/dt or mm units.

step:
- check swe
- check discharge

"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from plot_SAC_utility import get_sac_ts_dataframe, get_obs_dataframe

# Default settings ########################################################
plt.ioff()
# McPhee
watershed = 'MPHC2'
watershed_area = 2117470000
snow17_dir = r'D:\Research_Data\2_Mcphee\Mcphee_scenarios\snow17_best\{}'.format(watershed)
ueb_dir = r'D:\Research_Data\2_Mcphee\Mcphee_scenarios\s8_ueb_cali_utcoffset_final_best\{}'.format(watershed)
obs_discharge_path = r'D:\Research_Data\2_Mcphee\Mcphee_scenarios\QME_MPHC2L_F.QME'

# # # Dillon
# watershed = 'DIRC2'
# watershed_area = 867764000
# snow17_dir = r'D:\Research_Data\3_Dillon\Calibration\snow17_best_cali\{}'.format(watershed)
# ueb_dir = r'D:\Research_Data\3_Dillon\Calibration\ueb_best_cali\{}'.format(watershed)
# obs_discharge_path = r'D:\Research_Data\3_Dillon\obs_discharge\QME_DIRC2L_F.QME'

snow17_skip = 136
ueb_skip = 121

water_year_list = [1994, 1997, 2001, 2008] #range(1990, 2010)  #[1996, 1997, 2002, 2003, 2004, 2005, 2006]
dt = 6

result_dir = os.path.join(os.getcwd(), 'single_year_analysis_{}'.format(watershed))
if not os.path.isdir(result_dir):
    os.makedirs(result_dir)


# step 1 get dataframe of model results
if os.path.isdir(ueb_dir):
    ts_file_list = [os.path.join(ueb_dir, name) for name in os.listdir(ueb_dir) if name[-2:] == 'ts']
    ueb_df = get_sac_ts_dataframe(ts_file_list, sim_skip=ueb_skip)
    ueb_df.columns = ['ueb_' + name if 'ueb' not in name else name for name in ueb_df.columns]

if os.path.isdir(snow17_dir):
    ts_file_list = [os.path.join(snow17_dir, name) for name in os.listdir(snow17_dir) if name[-2:] == 'ts']
    snow17_df = get_sac_ts_dataframe(ts_file_list, sim_skip=snow17_skip)
    snow17_df.columns = ['snow17_'+name if 'snow17' not in name else name for name in snow17_df.columns]

obs_df = get_obs_dataframe(obs_discharge_path)

# step2 get plots for each water year
def get_discharge_stats(obs, sim):
    nse = 1 - sum(np.power((obs - sim), 2)) / sum(np.power((obs - obs.mean()), 2))
    bias = (sim - obs).mean()
    rmse = np.sqrt(np.mean(np.power((obs - sim), 2)))
    return {'nse': nse, 'bias': bias, 'rmse': rmse}


for water_year in water_year_list:
    start_time = '{}-10-01'.format(water_year-1)
    end_time = '{}-10-01'.format(water_year)

    # get subset results as plot df
    ueb_data = ueb_df[(ueb_df.index >= start_time) & (ueb_df.index < end_time)]
    ueb_data['ueb_rmlt_cum'] = ueb_data['ueb_xmrg'].cumsum()
    ueb_data['ueb_rmlt_cum_ratio'] = ueb_data['ueb_rmlt_cum']/ueb_data['ueb_rmlt_cum'].ix[-1]
    ueb_data['ueb_swe_total'] = ueb_data['ueb_SWE'] + ueb_data['ueb_Wc']

    snow17_data = snow17_df[(snow17_df.index >= start_time) & (snow17_df.index < end_time)]
    snow17_data['snow17_rmlt_cum'] = snow17_data['snow17_rmlt'].cumsum()
    snow17_data['snow17_rmlt_cum_ratio'] = snow17_data['snow17_rmlt_cum']/snow17_data['snow17_rmlt_cum'].ix[-1]
    snow17_data['snow17_swe_total'] = snow17_data['snow17_liqw'] + snow17_data['snow17_we']

    plot_df = pd.concat([ueb_data, snow17_data], axis=1)

    # get daily discharge as discharge df
    ueb_discharge = ueb_data.groupby(pd.Grouper(freq='D'))['ueb_discharge'].mean()
    snow17_discharge = snow17_data.groupby(pd.Grouper(freq='D'))['snow17_discharge'].mean()
    obs_discharge = obs_df[(obs_df.index >= start_time) & (obs_df.index < end_time)]

    discharge_df = pd.concat([ueb_discharge, snow17_discharge, obs_discharge], axis=1)
    discharge_df.dropna(inplace=True)
    discharge_df['obs_cum'] = (3600*24*discharge_df.obs).cumsum()/watershed_area
    discharge_df['obs_cum_ratio'] = discharge_df['obs_cum']/discharge_df['obs_cum'].ix[-1]
    discharge_df['ueb_obs_diff'] = discharge_df['ueb_discharge'] - discharge_df['obs']
    discharge_df['snow17_obs_diff'] = discharge_df['snow17_discharge'] - discharge_df['obs']

    # cum rmlt compare
    # fig, ax = plt.subplots(figsize=(10, 8))
    # plot_df.plot(y=['ueb_rmlt_cum_ratio','snow17_rmlt_cum_ratio'],
    #              ax=ax,
    #              title='Compare of cumulative rain plus melt in {} water year'.format(water_year))
    # # discharge_df.plot.area(y='obs_cum_ratio', ax=ax)
    # ax.legend(['UEB', 'SNOW-17'])

    # swe compare
    fig, ax = plt.subplots(figsize=(13, 6))
    plot_df.plot(y=['ueb_swe_total', 'snow17_swe_total'],
                 ax=ax)
    ax.legend(['UEB', 'SNOW-17'])
    ax.set_xlabel('WY {}'.format(water_year))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.tick_params(axis='x', rotation=0)
    plt.xticks(horizontalalignment="center")
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'swe_{}.png'.format(water_year)))

    # discharge compare
    stat = {}
    for model in ['ueb', 'snow17']:
        model_name = 'UEB' if model == 'ueb' else 'SNOW-17'
        stat[model_name] = get_discharge_stats(discharge_df['obs'], discharge_df['{}_discharge'.format(model)])

    fig, ax = plt.subplots(figsize=(13, 6))
    discharge_df.plot.area(y='obs',
                           ax=ax,
                           style='silver')
    discharge_df.plot(y=['ueb_discharge', 'snow17_discharge'],
                      ax=ax,
                      )
    handles, labels = ax.get_legend_handles_labels()
    ax.set_ylim([0.0, discharge_df[['obs', 'ueb_discharge', 'snow17_discharge']].max().max() * 1.05])
    ax.legend(handles, ['UEB', 'SNOW-17', 'Obs'])
    text = ''
    for model, stat_dict in stat.items():
        text += '{}:\n' \
                'rmse={} cms\n' \
                'nse={}\n' \
                'bias={} cms\n\n'.format(model, round(stat_dict['rmse'], 2), round(stat_dict['nse'], 2), round(stat_dict['bias'], 2))
    ax.text(0.02, 0.7, text, transform=ax.transAxes, size=8)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.minorticks_off()
    ax.set_xlabel('WY {}'.format(water_year))
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'discharge_{}.png'.format(water_year)))

    fig, ax = plt.subplots(figsize=(13, 7))
    discharge_df.plot(y=['ueb_obs_diff', 'snow17_obs_diff'],
                      ax=ax,
                      )

    ax.legend(['UEB', 'SNOW-17'])
    fig.savefig(os.path.join(result_dir, 'discharge_err_{}.png'.format(water_year)))

    # temp compare
    fig, ax = plt.subplots(figsize=(13, 7))
    plot_df.plot(y=['uebTair'],
                      ax=ax,
                      )

    ax.legend(['temperature'])
    fig.savefig(os.path.join(result_dir, 'temp_{}.png'.format(water_year)))

    # prec compare
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_df.plot(y=['uebPrec'],
                 ax=ax,)
    ax.legend(['precipitation'])
    fig.savefig(os.path.join(result_dir, 'prec_{}.png'.format(water_year)))