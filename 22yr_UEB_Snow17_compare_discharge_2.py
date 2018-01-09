"""
This is used to compare the snow17 workflow, ueb workflow, observation discharge data and make plots:
- time series of the 3 sources
- histogram of monthly mean
- histogram of annual mean
- histogram of 4-7 volume

"""

import calendar
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from plot_SAC_utility import get_sim_dataframe, get_obs_dataframe, get_DF, get_volume_error_stat, \
    get_annual_mean_stat, get_monthly_mean_stat


# user settings
ueb_file = 'DRGC2_discharge_outlet_22yr.ts'
snow17_file = 'DRGC2_discharge_outlet_RTI_snow17.ts'
obs_file = 'DRGC2H_F.QME'
start_time = '1989-10-01'
end_time = '2010-06-30'
watershed_area = 1818920000  # m^2  1818.92 km^2
watershed_name = 'Animas'


# get the discharge from file
sim_dict = {
    'ueb': get_sim_dataframe(ueb_file, start_time, end_time, sim_skip=91),
    'snow17': get_sim_dataframe(snow17_file, start_time, end_time, sim_skip=136)
}
obs_df = get_obs_dataframe(obs_file,start_time, end_time)

# get statistics for plot
monthly_mean_dict = {}
volume_err_dict = {}
annual_mean_dict = {}
for key, sim_df in sim_dict.items():
    DF = get_DF(sim_df, obs_df)
    monthly_mean_dict[key] = get_monthly_mean_stat(DF, watershed_area)
    annual_mean_dict[key] = get_annual_mean_stat(DF, watershed_area)
    volume_err_dict[key] = get_volume_error_stat(DF, watershed_area)

# create result folder
results_dir = os.path.join(os.getcwd(), 'compare_discharge_analysis_{}'.format(watershed_name))
if not os.path.isdir(results_dir):
    os.mkdir(results_dir)

# time series plot
plot_df = pd.concat([sim_dict['ueb'], sim_dict['snow17'], obs_df], axis=1)
plot_df.columns = ['ueb','snow17','obs']
fig,ax = plt.subplots(figsize=(13, 6))
plot_df.plot(ax=ax)
ax.set_title('time series of discharge')
ax.set_ylabel('discharge(cms)')
fig.savefig(os.path.join(results_dir, 'time_series.png'), dpi=1200)


# monthly plot (cms)
fig1, ax1 = plt.subplots(figsize=(10, 5))
snow17_result = monthly_mean_dict['snow17'][0][['sim', 'obs']]
ueb_result = monthly_mean_dict['ueb'][0][['sim']]
plot_df = pd.concat([snow17_result, ueb_result],axis=1)
plot_df.columns = ['snow17', 'obs', 'ueb']
plot_df.plot.bar(ax=ax1, rot=0)
ax1.set_title('monthly mean of discharge')
ax1.set_xticklabels([x[:3].upper() for x in calendar.month_name if x])
ax1.set_ylabel('discharge(cms)')
text = 'snow17_bias = {}\n' \
       'snow17_percent_bias= {}%\n' \
       'ueb_bias= {}\n' \
       'ueb_percent_bias= {}%\n'.format(round(monthly_mean_dict['snow17'][1], 3),
                                        round(monthly_mean_dict['snow17'][2], 3),
                                        round(monthly_mean_dict['ueb'][1], 3),
                                        round(monthly_mean_dict['ueb'][2], 3))
ax1.text(0.02, 0.75, text, transform=ax1.transAxes)
fig1.savefig(os.path.join(results_dir,'monthly_mean.png'), dpi=1200)

# monthly plot (depth)
fig2, ax2 = plt.subplots(figsize=(10, 5))
snow17_result = monthly_mean_dict['snow17'][0][['sim_depth', 'obs_depth']]
ueb_result = monthly_mean_dict['ueb'][0][['sim_depth']]
plot_df = pd.concat([snow17_result, ueb_result],axis=1)
plot_df.columns=['snow17', 'obs', 'ueb']
plot_df.plot.bar(ax=ax2, rot=0)
ax2.set_title('monthly mean of discharge (in depth)')
ax2.set_xticklabels([x[:3].upper() for x in calendar.month_name if x])
ax2.set_ylabel('discharge(mm)')
text = 'snow17_bias = {}\n' \
       'snow17_percent_bias= {}%\n' \
       'ueb_bias= {}\n' \
       'ueb_percent_bias= {}%\n'.format(round(monthly_mean_dict['snow17'][3], 3),
                                        round(monthly_mean_dict['snow17'][4], 3),
                                        round(monthly_mean_dict['ueb'][3], 3),
                                        round(monthly_mean_dict['ueb'][4], 3))
ax2.text(0.02, 0.75, text, transform=ax2.transAxes)
fig2.savefig(os.path.join(results_dir,'monthly_mean_depth.png'), dpi=1200)


# annual plot (cms)
fig3, ax3 = plt.subplots(figsize=(13, 6))
snow17_result = annual_mean_dict['snow17'][0][['sim', 'obs']]
ueb_result = annual_mean_dict['ueb'][0][['sim']]
plot_df = pd.concat([snow17_result, ueb_result], axis=1)
plot_df.columns = ['snow17', 'obs', 'ueb']
plot_df.plot.bar(ax=ax3, rot=0)
ax3.set_title('annual mean of discharge')
ax3.set_xticklabels(plot_df.index.year)
ax3.set_ylabel('discharge(cms)')
text = 'snow17_bias = {}\n' \
       'snow17_percent_bias= {}%\n' \
       'ueb_bias= {}\n' \
       'ueb_percent_bias= {}%\n'.format(round(annual_mean_dict['snow17'][1], 3),
                                        round(annual_mean_dict['snow17'][2], 3),
                                        round(annual_mean_dict['ueb'][1], 3),
                                        round(annual_mean_dict['ueb'][2], 3))
ax3.text(0.02, 0.8, text, transform=ax3.transAxes)
fig3.savefig(os.path.join(results_dir, 'annual_mean.png'), dpi=1200)

# annual plot (depth)
fig4, ax4 = plt.subplots(figsize=(13, 6))
snow17_result = annual_mean_dict['snow17'][0][['sim_depth', 'obs_depth']]
ueb_result = annual_mean_dict['ueb'][0][['sim_depth']]
plot_df = pd.concat([snow17_result, ueb_result], axis=1)
plot_df.columns = ['snow17', 'obs', 'ueb']
plot_df.plot.bar(ax=ax4, rot=0)
ax4.set_title('annual mean of discharge (in depth)')
ax4.set_xticklabels(plot_df.index.year)
ax4.set_ylabel('discharge(mm)')
text = 'snow17_bias = {}\n' \
       'snow17_percent_bias= {}%\n' \
       'ueb_bias= {}\n' \
       'ueb_percent_bias= {}%\n'.format(round(annual_mean_dict['snow17'][3], 3),
                                        round(annual_mean_dict['snow17'][4], 3),
                                        round(annual_mean_dict['ueb'][3], 3),
                                        round(annual_mean_dict['ueb'][4], 3))
ax4.text(0.02, 0.8, text, transform=ax4.transAxes)
fig4.savefig(os.path.join(results_dir, 'annual_mean_depth.png'), dpi=1200)


# annual plot (cms)
fig5, ax5 = plt.subplots(figsize=(13, 6))
snow17_result = volume_err_dict['snow17'][0][['sim_vol', 'obs_vol']]
ueb_result = volume_err_dict['ueb'][0][['sim_vol']]
plot_df = pd.concat([snow17_result, ueb_result], axis=1)
plot_df.columns = ['snow17', 'obs', 'ueb']
plot_df.plot.bar(ax=ax5, rot=0)
ax5.set_title('April to July volume')
ax5.set_xticklabels(plot_df.index.year)
ax5.set_ylabel('volume(m^3)')
text = 'snow17_bias = {}\n' \
       'snow17_percent_bias= {}%\n' \
       'ueb_bias= {}\n' \
       'ueb_percent_bias= {}%\n'.format(round(volume_err_dict['snow17'][1], 3),
                                        round(volume_err_dict['snow17'][2], 3),
                                        round(volume_err_dict['ueb'][1], 3),
                                        round(volume_err_dict['ueb'][2], 3))
ax5.text(0.02, 0.8, text, transform=ax5.transAxes)
fig5.savefig(os.path.join(results_dir, 'volume_err.png'), dpi=1200)

# annual plot (depth)
fig6, ax6 = plt.subplots(figsize=(13, 6))
snow17_result = volume_err_dict['snow17'][0][['sim_depth', 'obs_depth']]
ueb_result = volume_err_dict['ueb'][0][['sim_depth']]
plot_df = pd.concat([snow17_result, ueb_result], axis=1)
plot_df.columns = ['snow17', 'obs', 'ueb']
plot_df.plot.bar(ax=ax6, rot=0)
ax6.set_title('April to July volume (in depth)')
ax6.set_xticklabels(plot_df.index.year)
ax6.set_ylabel('depth(mm)')
text = 'snow17_bias = {}\n' \
       'snow17_percent_bias= {}%\n' \
       'ueb_bias= {}\n' \
       'ueb_percent_bias= {}%\n'.format(round(volume_err_dict['snow17'][3], 3),
                                        round(volume_err_dict['snow17'][4], 3),
                                        round(volume_err_dict['ueb'][3], 3),
                                        round(volume_err_dict['ueb'][4], 3))
ax6.text(0.02, 0.8, text, transform=ax6.transAxes)
fig6.savefig(os.path.join(results_dir, 'volume_err_depth.png'), dpi=1200)