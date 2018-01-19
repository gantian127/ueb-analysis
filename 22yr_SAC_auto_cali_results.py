"""
This is used to select the optimal results of the SAC+Routing results

- list all the options with statistics in csv files
- select the best options
- make plots for the best options

Note:
- put plot_SAC_utility.py and this file under the 1st level folder for auto calibration and run:
  python 22yr_SAC_auto_cali_results.py
- remember use the default python from CHPC
  module load python/2.7.11
  module unload python/2.7.11
"""

import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import shutil

from plot_SAC_utility import get_sacsma_time_and_discharge, get_statistics, get_rit_discharge,\
    get_data_by_time_aggregation, plot_obs_vs_sim

results_dir = './output/test'

if os.path.isdir('./analysis'):
    shutil.rmtree('./analysis')
os.mkdir('./analysis')

obs_file = os.path.join('./data/hisobs', os.listdir('./data/hisobs/')[0])
option_list = []
stat_names = ['rmse', 'nse', 'r', 'mae','bias']
top_number = 6

# get the statistics for all options
print 'calculate statistics'
for subdir in os.listdir(results_dir):
    sim_file = os.path.join(results_dir, subdir, subdir.split('_')[0]+'_discharge_outlet.ts')
    results = get_sacsma_time_and_discharge(discharge=sim_file,
                                        discharge_skip=255,
                                        unit_factor=1, unit_offset=0,
                                        time_hr_change='24', time_hr_change_factor=1)
    sim, time = get_data_by_time_aggregation(results['time'], results['discharge'], freq='D')
    obs = get_rit_discharge(obs_file, skiprows=3, start_date_obj=results['time'][0], end_date_obj=results['time'][-1],
                            unit_factor=0.0283168, unit_offset=0)
    statistics = get_statistics(sim, obs)
    result = [statistics[name] for name in stat_names]
    result.append(subdir)
    option_list.append(result)
    print result

with open('./analysis/all_results.csv', 'wb') as all_results:
    wr = csv.writer(all_results, dialect='excel')
    option_list.insert(0, stat_names + ['option'])
    wr.writerows(option_list)


# sort the statistics and get optimal results
optimal_folders = []
with open('./analysis/ranks.csv', 'wb') as ranks:
    wr = csv.writer(ranks, dialect='excel')
    for i in range(0, len(stat_names)):
        wr.writerow(['{}'.format(stat_names[i])])
        a = option_list[1:]
        if start_name[i] == 'bias':
            a = [abs(x) for x in a]

        a.sort(key=lambda pair: pair[i], reverse=False if stat_names[i] in ['mae', 'rmse', 'bias'] else True)
        wr.writerows(a[:top_number])
        for option in a[:top_number]:
            optimal_folders.append(option[-1])

# make plot for the results
print 'make plots'
best_options = []
for subdir in set(optimal_folders):
    sim_file = os.path.join(results_dir, subdir, subdir.split('_')[0]+'_discharge_outlet.ts')
    results = get_sacsma_time_and_discharge(discharge=sim_file,
                                        discharge_skip=255,
                                        unit_factor=1, unit_offset=0,
                                        time_hr_change='24', time_hr_change_factor=1)
    sim, time = get_data_by_time_aggregation(results['time'], results['discharge'], freq='D')
    obs = get_rit_discharge(obs_file, skiprows=3, start_date_obj=results['time'][0], end_date_obj=results['time'][-1],
                            unit_factor=0.0283168, unit_offset=0)
    plt.ioff()  # no need to show the plot interactively
    plot_obs_vs_sim(time=time,
                    sim=sim,
                    obs=obs,
                    month_interval=12,
                    format='%Y',
                    ts_xlim=[datetime(time[0].astype('M8[D]').astype('O').year, 1, 1),
                             datetime(time[-1].astype('M8[D]').astype('O').year, 12, 31)],
                    xlim=[0, max(sim+obs)],
                    ylim=[0, max(sim+obs)],
                    save_name='obs_sim_discharge_{}.png'.format(subdir),
                    save_folder='./analysis')
    best_options.append(subdir)
    shutil.copyfile(sim_file, os.path.join('./analysis', subdir+'_discharge_outlet.ts'))

with open('./analysis/best_options.txt','w') as best_options_file:
    for item in best_options:
        best_options_file.write("%s\n"%item)

print 'Done'





