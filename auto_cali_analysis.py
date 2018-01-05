"""
This is used to analyze all the auto-calibration population results.
This can be used after running the 22yr_SAC_auto_cali_results.py to find out the best option.
- time series plots for all populations: there is no big band
- box plot to show the parameter values and the objective values

"""

import os
from plot_SAC_utility import get_sim_dataframe, get_obs_dataframe
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


# user settings
obs_file_path = '/uufs/chpc.utah.edu/common/home/ci-water6-1/TianGan/22yr_Animas_watershed_sac/Paul_test_2/data/hisobs/DRGC2H_F.QME'
output_folders = [
                  'test_work2_1st',
                  'test_work2_2nd_for_plot']
best_folders = [
                '',
                'DRGC2_17284']

# get all the options time series
for i in range(0, len(output_folders)):
    output_folder = output_folders[i]
    sim_list = []
    column_names = []
    folder_list = os.listdir(output_folder)
    for folder in folder_list:
        folder_path = os.path.join(os.getcwd(), output_folder, folder)
        if os.path.isdir(folder_path):
            ts_file_name = [x for x in os.listdir(folder_path) if x[-3:] == '.ts'].pop()
            ts_file_path = os.path.join(folder_path,ts_file_name)
            sim = get_sim_dataframe(ts_file_path)
            sim_list.append(sim)
            column_names.append(folder)

    DF = pd.concat(sim_list, axis=1, join='inner')
    DF.columns = column_names

    # get best and the observation time series
    obs = get_obs_dataframe(obs_file_path)
    if best_folders[i]:
        DF2 = pd.concat([DF[best_folders[i]], obs], axis=1, join='inner')
        best_color = 'r'
    else:
        DF2 = pd.concat([DF.iloc[:, [0]], obs], axis=1, join='inner')
        best_color = 'grey'

    # plot the time series band plot
    fig, ax = plt.subplots()
    DF.plot(ax=ax, color='grey', linewidth=1.5, legend=False)
    DF2.plot(ax=ax, color=[best_color, 'b'], linewidth=0.5, legend=False)
    grey_line = mlines.Line2D([], [], color='grey', label='all {} options'.format(len(column_names)))
    blue_line = mlines.Line2D([], [], color='b', label='observation')
    handles = [grey_line, blue_line]
    if best_folders[i]:
        red_line = mlines.Line2D([], [], color='r', label='best option')
        handles.append(red_line)
    ax.legend(handles=handles)
    ax.set_title('Time series of discharge for {} round auto-calibration population'.format(i+1))
    ax.set_xlabel('time')
    ax.set_ylabel('discharge(cms)')
    fig.savefig('time_series_band_plot_{}.png'.format(i+1), dpi=1200)

print 'Time series plot finished'