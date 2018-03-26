"""
This is used to analyze all the auto-calibration population results.
This is to replace version 1. Only need to run this script to get the analysis and results

requirements:
- put this code and the utility code at the same level with the test folder

steps:
- analyze the time serise:
  a) time series plots for all populations and the best option (least percent error sum)
  b) box plot to show the parameter values
  c) box plot to show the stats values for discharge time series

- analyze the front and decision result:
  a) box plot of front values (objective function values)
  b) box plot of decision values (parameter values)

- analyze the peadj parameters:
  a) box plot for peadj values

"""

import os
from plot_SAC_utility import get_sim_dataframe, get_obs_dataframe, get_basic_stats, get_annual_mean_stat,\
     get_monthly_mean_stat, get_volume_error_stat
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import calendar
import linecache


# user settings ####################################################
watershed_name = 'DOLC2'
watershed_area = 1503860000
obs_file_path = '/uufs/chpc.utah.edu/common/home/ci-water6-1/TianGan/22yr_Animas_watershed_sac/Paul_test_2/data/hisobs/DOLC2L_F.QME'
output_folders = [
                  # 'test_work2_1st',
                  # 'test_work2_2nd_for_plot',
                    'test_DOLC2_1st',
                    'test_DOLC2_2nd'
                 ]
start_time = '1989/10/01'
end_time = '2010/09/30'


output2_folders = [
    # '/uufs/chpc.utah.edu/common/home/ci-water6-1/TianGan/22yr_Animas_watershed_sac/Paul_test_2/UEB_DRGC2_NSGAII_Parallel_RDHM_NASA_work2_for_plot/',
    '/uufs/chpc.utah.edu/common/home/ci-water6-1/TianGan/22yr_Animas_watershed_sac/Paul_test_2/UEB_DRGC2_NSGAII_Parallel_RDHM_NASA/',
    ]

result_dir = os.path.join(os.getcwd(), 'auto_cali_analysis_{}'.format(watershed_name))
if not os.path.isdir(result_dir):
    os.mkdir(result_dir)

# Time series analysis #######################################################
print 'step1: time series analysis'
for i in range(0, len(output_folders)):

    # get option and observation time series
    output_folder = output_folders[i]
    sim_list = []
    column_names = []
    folder_list = os.listdir(output_folder)
    for folder in folder_list:
        folder_path = os.path.join(os.getcwd(), output_folder, folder)
        if os.path.isdir(folder_path):
            ts_file_name = [x for x in os.listdir(folder_path) if x[-3:] == '.ts'].pop()
            ts_file_path = os.path.join(folder_path, ts_file_name)
            sim = get_sim_dataframe(ts_file_path, start_time=start_time, end_time=end_time)
            sim_list.append(sim)
            column_names.append(folder)

    DF = pd.concat(sim_list, axis=1, join='inner')
    DF.columns = column_names

    obs = get_obs_dataframe(obs_file_path)

    # get the statistics for all the options
    stat_result = pd.DataFrame(columns=['rmse', 'nse', 'r', 'bias', 'monthly_bias', 'annual_bias', 'vol_err'])
    for column in column_names:
        df = pd.concat([DF[column], obs], axis=1, join_axes=[DF[column].index]).reset_index()
        df.columns = ['time', 'sim', 'obs']
        rmse, nse, _, r, bias = get_basic_stats(df)
        _,_,_,_, monthly_bias = get_monthly_mean_stat(df, watershed_area)
        _,_,_,_, annual_bias = get_annual_mean_stat(df, watershed_area)
        _,_,_,_, vol_err = get_volume_error_stat(df, watershed_area, start_month=4, end_month=7)

        stat_result.loc[column] = [rmse, nse, r, bias, monthly_bias, annual_bias, vol_err]

    # get the best option
    stat_result['score'] = stat_result['monthly_bias'].abs() + stat_result['annual_bias'].abs() + stat_result['vol_err'].abs()
    best_folder = stat_result['score'].idxmin()
    best_rmse = stat_result['rmse'].idxmin()
    best_nse = stat_result['nse'].idxmax()
    best_r = stat_result['r'].idxmax()
    best_bias = stat_result['bias'].abs().idxmin()
    best_month_bias = stat_result['monthly_bias'].abs().idxmin()
    best_annual_bias = stat_result['annual_bias'].abs().idxmin()
    best_vol_err = stat_result['vol_err'].abs().idxmin()
    DF2 = pd.concat([DF[best_folder], obs], axis=1, join='inner')

    path = os.path.join(result_dir, 'stat_result_{}.csv'.format(output_folder))
    stat_result.to_csv(path)
    with open(path, 'a') as my_file:
        my_file.write(
            '\n best score = {}'
            '\n best rmse = {} '
            '\n best r = {} '
            '\n best nse= {}'
            '\n best bias = {}'
            '\n best month_bias= {}'
            '\n best annual_bias= {}'
            '\n best vol_err= {}'
            .format(best_folder, best_rmse, best_r, best_nse, best_bias, best_month_bias, best_annual_bias, best_vol_err)
        )

    # plot the time series band plot
    fig, ax = plt.subplots()
    DF.plot(ax=ax, color='grey', linewidth=1.5, legend=False)
    DF2.plot(ax=ax, color=['r', 'b'], linewidth=0.5, legend=False)
    grey_line = mlines.Line2D([], [], color='grey', label='all {} options'.format(len(column_names)))
    blue_line = mlines.Line2D([], [], color='b', label='observation')
    red_line = mlines.Line2D([], [], color='r', label='best option')
    ax.legend(handles=[grey_line, blue_line, red_line])
    ax.set_title('Time series of discharge for auto-calibration population')
    ax.set_xlabel('time')
    ax.set_ylabel('discharge(cms)')
    a = stat_result.loc[best_folder]
    text = 'rmse = {} \nnse= {} \nr= {} \nbias= {} \n '.format(a['rmse'], a['nse'], a['r'], a['bias'])
    ax.text(0.05, 0.8, text, transform=ax.transAxes)
    fig.savefig(os.path.join(result_dir, 'time_series_band_plot_{}.png'.format(output_folder)))

    # plot the boxplot for percent bias
    fig2, ax2 = plt.subplots()
    stat_result.boxplot(['annual_bias','monthly_bias','vol_err'], grid=False, ax=ax2)
    ax2.set_ylabel('percent error (%)')
    ax2.set_title('Boxplot of different percent bias')
    ax2.set_xticklabels(['annual mean bias', 'monthly mean bias', 'April-July volume error'])
    fig2.savefig(os.path.join(result_dir, 'boxplot_of_percent_bias_{}.png'.format(output_folder)))

    # plot the boxplot for stats
    fig3, ax3 = plt.subplots(2, 2, figsize=(10,8))
    stat_result.boxplot(['nse'], grid=False, ax=ax3[0, 0])
    stat_result.boxplot(['r'], grid=False, ax=ax3[0, 1])
    stat_result.boxplot(['rmse'], grid=False, ax=ax3[1, 0])
    stat_result.boxplot(['bias'], grid=False, ax=ax3[1, 1])
    plt.suptitle('Boxplot of basic stats')
    ax3[1, 0].set_ylabel('discharge(cms)')
    ax3[1, 1].set_ylabel('discharge(cms)')
    fig3.savefig(os.path.join(result_dir, 'boxplot_of_basic_stats_{}.png'.format(output_folder)))


# decisions000.dat and front000.dat analysis  #####################################################
print 'step2: decision and front analysis'
for i in range(0, len(output2_folders)):
    output2_folder = output2_folders[i]
    decision_file_path = os.path.join(output2_folder, 'Decision000.dat')
    front_file_path = os.path.join(output2_folder, 'front000.dat')

    if os.path.isfile(decision_file_path):
        decision_df = pd.read_csv(decision_file_path,header=None, sep='\s+')
        fig4, ax4 = plt.subplots(figsize=(12, 5))
        decision_df.boxplot(ax=ax4, grid=False)
        ax4.set_xticklabels(['sac_UZTWM','sac_UZFWM','sac_LZTWM','sac_LZFPM','sac_LZFSM','sac_UZK','sac_LZPK',
                             'sac_LZSK','sac_ZPERC','sac_REXP','sac_PFREE','Beta0','Beta1','Beta2',], fontdict={'fontsize':7}) # this is got from 'GeneHeader.txt'
        plt.suptitle('Boxplot for Decision000.dat file')
        fig4.savefig(os.path.join(result_dir, 'decision000_{}.png'.format(i)))

    if os.path.isfile(front_file_path):
        front_df = pd.read_csv(front_file_path, header=None, sep='\s+')
        front_df.columns = ['negative Kling-Gupta', 'volume difference', 'penalty']
        fig5, ax5 = plt.subplots(1, 3, figsize=(12, 5))
        front_df.boxplot(['negative Kling-Gupta'], grid=False, ax=ax5[0])
        front_df.boxplot(['volume difference'], grid=False, ax=ax5[1])
        front_df.boxplot(['penalty'], grid=False, ax=ax5[2])
        plt.suptitle('Boxplot for front000.dat file')
        fig5.savefig(os.path.join(result_dir, 'front000_{}.png'.format(i)))



# peadj parameter analysis #########################################################################
print 'step3: peadj analysis'
for i in range(0, len(output_folders)):

    output_folder = output_folders[i]
    columns = ['peadj_'+x[:3].upper() for x in calendar.month_name if x]
    peadj_result = pd.DataFrame(columns=columns)
    folder_list = os.listdir(output_folder)

    # get peadj values from each inputdeck file
    for folder in folder_list:
        folder_path = os.path.join(os.getcwd(), output_folder, folder)
        if os.path.isdir(folder_path):
            deck_file_name = [x for x in os.listdir(folder_path) if x[-4:] == '.out'].pop()
            deck_file_path = os.path.join(folder_path, deck_file_name)
            parse_list = []
            for line_num in [153, 154]:
                str_list = linecache.getline(deck_file_path, line_num).replace('\n', '').split(' ')[2:]
                parse_list.extend(str_list)

            para_values = []
            for i in range(0, len(parse_list)):
                para_values.append(float(parse_list[i].replace(columns[i]+'=','')))

            peadj_result.loc[folder]=para_values

    # boxplot for peadj values
    fix6, ax6 = plt.subplots(figsize=(15, 5))
    peadj_result.boxplot(grid=False, ax=ax6)
    fix6.savefig(os.path.join(result_dir, 'peadj_{}.png'.format(output_folder)))

    # save results
    path = os.path.join(result_dir, 'peadj_result_{}.csv'.format(output_folder))
    peadj_result.to_csv(path)

print 'All analysis is done'