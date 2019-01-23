"""
This is using the RDHM time series to analyze the SWE and discharge at each year (snow17 vs ueb workflow)
Selected years (max 4) results are combined within one plot

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

water_year_list = [1994, 1997, 2001, 2008]  #range(1990, 2010)  #[1996, 1997, 2002, 2003, 2004, 2005, 2006]
dt = 6

result_dir = os.path.join(os.getcwd(), 'single_year_analysis_combine_{}'.format(watershed))
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

fig, ax_list = plt.subplots(len(water_year_list), 1, figsize=(13, 4*len(water_year_list)))
# plt.tight_layout()


for index, water_year, ax in zip(['a', 'b', 'c', 'd'], water_year_list, ax_list):
    start_time = '{}-10-01'.format(water_year-1)
    end_time = '{}-10-01'.format(water_year)

    # get discharge df
    ueb_data = ueb_df[(ueb_df.index >= start_time) & (ueb_df.index < end_time)]
    snow17_data = snow17_df[(snow17_df.index >= start_time) & (snow17_df.index < end_time)]

    ueb_discharge = ueb_data.groupby(pd.Grouper(freq='D'))['ueb_discharge'].mean()
    snow17_discharge = snow17_data.groupby(pd.Grouper(freq='D'))['snow17_discharge'].mean()
    obs_discharge = obs_df[(obs_df.index >= start_time) & (obs_df.index < end_time)]
    discharge_df = pd.concat([ueb_discharge, snow17_discharge, obs_discharge], axis=1)
    discharge_df.dropna(inplace=True)

    # discharge compare
    stat = {}
    for model in ['ueb', 'snow17']:
        model_name = 'UEB' if model == 'ueb' else 'SNOW-17'
        stat[model_name] = get_discharge_stats(discharge_df['obs'], discharge_df['{}_discharge'.format(model)])

    discharge_df.plot.area(y='obs',
                           ax=ax,
                           style='silver')
    discharge_df.plot(y=['ueb_discharge', 'snow17_discharge'],
                      ax=ax,
                      )
    handles, labels = ax.get_legend_handles_labels()
    ax.set_ylim([0.0, 150])
    if ax == ax_list[0]:
        ax.legend(handles, ['UEB', 'SNOW-17', 'Obs'])
    else:
        ax.get_legend().remove()

    text = '({})\n\n'.format(index)
    # for model, stat_dict in stat.items():
    #     text += '{}\n' \
    #             'rmse: {} cms\n' \
    #             'nse: {}\n' \
    #             'bias: {} cms\n\n'.format(model, round(stat_dict['rmse'], 2), round(stat_dict['nse'], 2), round(stat_dict['bias'], 2))
    for model, stat_dict in stat.items():
        text += '{}\n' \
                'NSE: {}\n\n'.format( model, round(stat_dict['nse'], 2))
    ax.text(0.02, 0.3, text, transform=ax.transAxes, size=13)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.minorticks_off()
    ax.set_xlabel('WY {}'.format(water_year))
    ax.set_ylabel('discharge (cms)')

plt.tight_layout()
fig.savefig(os.path.join(result_dir, 'discharge_combine.png'))