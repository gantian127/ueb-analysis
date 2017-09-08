"""
This is to make plots for UEB APP output
"""
import os
from plot_time_series_domain import plot_time_series_domain_average
from plot_time_series import plot_time_series
from plot_multiple_time_series import *

tag = 'App'
year = '2009'
watershed = 'Animas'

workDir = r'C:\Users\jamy\Desktop\{}_{}_{}'.format(watershed, year, tag)
workDir = ''
if workDir:
    os.chdir(workDir)

# point plot
plot_time_series('prcp0.nc', 'prcp', 'time',
                  x_index=19, y_index=29, shape=['time', 'y', 'x'],
                  cumulative_scale=24,
                  title='Time series of precipitation in {} {} {}'.format(year, watershed, tag),
                  ylabel='Precipitation(m/hr)',
                  y2label='Cumulative of precipitation (m)',
                  save_as='preciitation_{}_{}_{}.png'.format(year,watershed,tag))

plot_time_series('SWE.nc', 'SWE', 'time',
                  x_index=19, y_index=29, shape=['time', 'y', 'x'],
                  title='Time series of SWE in {} {} {}'.format(year, watershed, tag),
                  cumulative=False,
                  save_as='swe_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_series('SWIT.nc','SWIT', 'time',
                 x_index=19, y_index=29, shape=['time', 'y', 'x'],
                 cumulative_scale=6,
                 title='Time series of SWIT in {} {} {}'.format(year, watershed, tag),
                 ylabel='SWIT(m/hr)',
                 y2label='Cumulative of SWIT (m)',
                 save_as='swit_{}_{}_{}.png'.format(year, watershed, tag))

# aggregation
plot_time_series('aggout.nc','SWIT', 'time',
                 x_index=0, shape=['time', 'x'],
                 cumulative_scale=6,
                 title='Aggregation output of SWIT in {} {} {}'.format(year, watershed, tag),
                 ylabel='SWIT(m)',
                 y2label='Cumulative of SWIT (m)',
                 save_as='agg_swit_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_series('aggout.nc','SWE', 'time',
                  x_index=0, shape=['time', 'x'],
                  cumulative=False,
                  title='Aggregation output of SWE in {} {}'.format(year, tag),
                  ylabel='SWE(m)',
                  save_as='agg_swe_{}_{}_{}.png'.format(year, watershed, tag))

# domain average
plot_time_series_domain_average('prcp0.nc', 'prcp', time='time',
                                xaxis_index=2, yaxis_index=1,
                                cumulative=True,
                                cumulative_scale=3,
                                title='Domain average of Precipitation in {} {} {}'.format(year, watershed, tag),
                                ylabel='Precipitation (m/hr)',
                                y2label='Cumulative of domain average Precipitation (m)',
                                save_as='domain_ave_prec_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_series_domain_average('SWE.nc', 'SWE', time='time',
                                xaxis_index=2, yaxis_index=1,
                                cumulative=False,
                                title='Domain average of SWE in {} {}'.format(year, tag),
                                ylabe='SWE(m)',
                                save_as='domain_ave_swe_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_series_domain_average('SWIT.nc', 'SWIT', time='time',
                                xaxis_index=2, yaxis_index=1,
                                cumulative=True, cumulative_scale=6,
                                title='Domain average of SWIT in {} {} {}'.format(year, watershed, tag),
                                ylabel='SWIT (m)',
                                y2label='Cumulative of domain average SWIT (m)',
                                save_as='domain_ave_swit_{}_{}_{}.png'.format(year, watershed, tag))

# compare the App data and Jupyter data
code_dir = r'C:\Users\jamy\Desktop\2010_water year_Jupyter_version'
app_dir = r'C:\Users\jamy\Desktop\2010_water year_app_version'


# compare SWIT ave
code_SWIT = os.path.join(code_dir,'SWIT.nc')
app_SWIT = os.path.join(app_dir,'SWIT.nc')
time_data = get_time_value(file_path=app_SWIT, time_var='time', units=None, calendar=None)

# average
code_swit_data_ave = get_var_ave(file_path=code_SWIT, var_name='SWIT', axis_index=(1, 2))
app_swit_data_ave = get_var_ave(file_path=app_SWIT, var_name='SWIT', axis_index=(1, 2))
diff_swit_ave = [code - app for code , app in zip(code_swit_data_ave, app_swit_data_ave)]
plot_multiple_time_series(time_data, [code_swit_data_ave, app_swit_data_ave, diff_swit_ave], color_list=None,
                          month_interval=1, legend=True,
                          title='compare app and jupyter SWIT ave results',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['code results','app results','result difference'],
                          # save_as='compare_swit_ave_app_code.png',
                          )

# point
code_swit_data_point = get_var_point_data(file_path=code_SWIT, var_name='SWIT', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_swit_data_point = get_var_point_data(file_path=app_SWIT, var_name='SWIT', x_index=19, y_index=36, var_dim_list=['time','y','x'])
diff_swit_point = [code - app for code , app in zip(code_swit_data_point, app_swit_data_point)]

plot_multiple_time_series(time_data, [code_swit_data_point, app_swit_data_point, diff_swit_point], color_list=None,
                          month_interval=1, legend=True,
                          title='compare app and jupyter SWIT point results',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['code results','app results','result difference'],
                          # save_as='compare_swit_ave_app_code.png',
                          )

# compare SWE
code_SWE = os.path.join(code_dir, 'SWE.nc')
app_SWE = os.path.join(app_dir, 'SWE.nc')
time_data = get_time_value(file_path=app_SWE, time_var='time', units=None, calendar=None)

# average
code_swe_data_ave = get_var_ave(file_path=code_SWE, var_name='SWE', axis_index=(1, 2))
app_swe_data_ave = get_var_ave(file_path=app_SWE, var_name='SWE', axis_index=(1, 2))
diff_swe_ave = [code - app for code , app in zip(code_swe_data_ave, app_swe_data_ave)]
plot_multiple_time_series(time_data, [code_swe_data_ave, app_swe_data_ave, diff_swe_ave], color_list=None,
                          month_interval=1, legend=True,
                          title='compare app and jupyter SWE ave results',
                          xlabel='Time', ylabel='SWE (m)',
                          line_label_list=['code results','app results','result difference'],
                          # save_as='compare_swe_ave_app_code.png',
                          )

# point
code_swe_data_point = get_var_point_data(file_path=code_SWE, var_name='SWE', x_index=19, y_index=36, var_dim_list=['time', 'y', 'x'])
app_swe_data_point = get_var_point_data(file_path=app_SWE, var_name='SWE', x_index=19, y_index=36, var_dim_list=['time', 'y', 'x'])
diff_swe_point = [code - app for code , app in zip(code_swe_data_point, app_swe_data_point)]

plot_multiple_time_series(time_data, [code_swe_data_point, app_swe_data_point, diff_swe_point], color_list=None,
                          month_interval=1, legend=True,
                          title='compare app and jupyter SWIT point results',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['code results','app results','result difference'],
                          # save_as='compare_swit_ave_app_code.png',
                          )