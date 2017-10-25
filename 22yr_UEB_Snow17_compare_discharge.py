"""
This is used to compare the discharge results from different model results
"""

import os

from plot_SAC_utility import *

sim_file = 'DRGC2_discharge_outlet_62824_22yr_cali.ts'
obs_file = 'DRGC2H_F.QME'
watershed_area = 1818920000  # m^2  1818.92 km^2

results_dir = os.path.join(os.getcwd(), 'test_discharge_{}'.format(sim_file[:-3]))
if not os.path.isdir(results_dir):
    os.mkdir(results_dir)


# get data frame
DF = get_sim_obs_dataframe(sim_file, obs_file,
                           # start_time='2005-10-01', end_time='2006-9-30',
                           save_folder=results_dir)

# daily discharge analysis
plot_obs_vs_sim(DF.time, DF.sim, DF.obs,
                month_interval=12, format='%Y',
                ts_xlim=[datetime(DF.time[0].year, 1, 1),
                         datetime(DF.time[len(DF)-1].year, 12, 31)],
                # month_interval=1, format='%Y/%m',
                save_folder=results_dir)

# monthly analysis
get_monthly_mean_analysis(DF, watershed_area, save_folder=results_dir)

# annual analysis
get_annual_mean_analysis(DF, watershed_area, save_folder=results_dir)

# April - July Volume error
get_volume_error_analysis(DF, save_folder=results_dir, start_month=4, end_month=7)


