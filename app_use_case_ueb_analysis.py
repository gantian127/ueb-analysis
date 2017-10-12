"""
This code is for the paper 2 use case data analysis to compare different resolution model run:
- domain average compare 600 vs 1200: swe, prcp, swit, mass balance
- cascade point compare 600 vs 1200: swe, prcp, swit, mass balance
- molas lake point compare 600 vs 1200: swe, prcp, swit, mass balance
- cascade point compare obs vs 1200: prcp, tmax, tmin, swe
- molas lake point compare obs vs 1200: prcp, tmax,tmin, swe

Results:
- 600 vs 1200 has no big difference for both domain and point results
- the observation swe is higher than simulation,
- the snotel vs daymet of prcp, tmax, tmin are similar.
- the difference of swe between obs and sim may be caused by terrain, temp, prcp, canopy, solar radiation etc.
"""

import os
import pandas as pd
from datetime import datetime
from plot_multiple_time_series import *


jupyter_dir = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year_jupyter_600'
app_dir = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water year_app_version'

# Domain average #######################################################################################
# compare prcp domain ave
jupyter_prcp = os.path.join(jupyter_dir,'prcp0.nc')
app_prcp = os.path.join(app_dir,'prcp0.nc')
jupyter_prcp_ave = get_var_ave(file_path=jupyter_prcp, var_name='prcp', axis_index=(1, 2))
app_prcp_ave = get_var_ave(file_path=app_prcp, var_name='prcp', axis_index=(1,2))
diff_prcp_ave = [jupyter - app for jupyter, app in zip(jupyter_prcp_ave, app_prcp_ave)]
time_data = get_time_value(file_path=jupyter_prcp, time_var='time', units=None, calendar=None)
fig, ax = plt.subplots(2,1)
plot_multiple_time_series(time_data, [jupyter_prcp_ave, app_prcp_ave],
                          ax=ax[0],
                          fig=fig,
                          color_list=None,
                          month_interval=1, legend=True,
                          title='Comparision of precipitation domain average',
                          xlabel='Time', ylabel='prcp (m/hr)',
                          line_label_list=['600m','1200m'],

                          )

plot_multiple_time_series(time_data, [diff_prcp_ave],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the results (600m-1200m)',
                          xlabel='Time', ylabel='prcp (m/hr)',
                          line_label_list=['difference'],
                          save_as='compare_prcp_ave_app_jupyter.png',
                          )

# compare SWIT domain ave
jupyter_SWIT = os.path.join(jupyter_dir,'SWIT.nc')
app_SWIT = os.path.join(app_dir,'SWIT.nc')
time_data = get_time_value(file_path=jupyter_SWIT, time_var='time', units=None, calendar=None)

jupyter_swit_data_ave = get_var_ave(file_path=jupyter_SWIT, var_name='SWIT', axis_index=(1, 2))
app_swit_data_ave = get_var_ave(file_path=app_SWIT, var_name='SWIT', axis_index=(1, 2))
diff_swit_ave = [jupyter - app for jupyter, app in zip(jupyter_swit_data_ave, app_swit_data_ave)]
fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(time_data,
                          [jupyter_swit_data_ave,
                           app_swit_data_ave,
                           # diff_swit_ave
                           ],
                          ax=ax[0],
                          fig=fig,
                          color_list=None,
                          month_interval=1, legend=True,
                          title='Comparision of rain plus melt for domain average',
                          xlabel='Time', ylabel='rain plus melt (m/hr)',
                          line_label_list=['600m', '1200m',
                                           # 'difference'
                                           ],
                          # save_as='compare_swit_ave_app_jupyter.png',
                          )

plot_multiple_time_series(time_data, [diff_swit_ave],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the results comparision ',
                          xlabel='Time', ylabel='rain plus melt (m/hr)',
                          line_label_list=['difference(600m-1200m)'],
                          legend=True,
                          save_as='compare_prcp_ave_app_jupyter.png',
                          )


# compare SWE domain ave
jupyter_SWE = os.path.join(jupyter_dir, 'SWE.nc')
app_SWE = os.path.join(app_dir, 'SWE.nc')
time_data = get_time_value(file_path=jupyter_SWE, time_var='time', units=None, calendar=None)

jupyter_swe_data_ave = get_var_ave(file_path=jupyter_SWE, var_name='SWE', axis_index=(1, 2))
app_swe_data_ave = get_var_ave(file_path=app_SWE, var_name='SWE', axis_index=(1, 2))
diff_swe_ave = [jupyter - app for jupyter, app in zip(jupyter_swe_data_ave, app_swe_data_ave)]
fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(time_data, [jupyter_swe_data_ave, app_swe_data_ave],
                          ax=ax[0],
                          fig=fig,
                          color_list=None,
                          month_interval=1, legend=True,
                          title='Comparision of Snow water equivalent for domain average',
                          xlabel='Time', ylabel='SWE (m)',
                          line_label_list=['600m','1200m','difference'],
                          # save_as='compare_swe_ave_app_jupyter.png',
                          )

plot_multiple_time_series(time_data, [diff_swe_ave],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the results comparision ',
                          xlabel='Time', ylabel='swe (m)',
                          line_label_list=['difference (600m-1200m)'],
                          save_as='compare_prcp_ave_app_jupyter.png',
                          )

# mass balance for domain average 600m
time_data = get_time_value(file_path=jupyter_SWIT, time_var='time', units=None, calendar=None)
time_data_daily = [time_data[i] for i in range(0,len(time_data), 4)]

jupyter_prcp_data_ave_acc = get_cumulative(jupyter_prcp_ave, cumulative_scale=24)
jupyter_swit_data_ave_acc = get_cumulative(jupyter_swit_data_ave, cumulative_scale=6)
jupyter_swe_data_ave_daily = [jupyter_swe_data_ave[i] for i in range(0,len(jupyter_swe_data_ave), 4)]
jupyter_swit_data_acc_daily = [jupyter_swit_data_ave_acc[i] for i in range(0 ,len(jupyter_swit_data_ave_acc),4)]


plot_multiple_time_series(time_data_daily, [jupyter_prcp_data_ave_acc[:-1],
                                           jupyter_swit_data_acc_daily,
                                           jupyter_swe_data_ave_daily],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance for domain average (600m)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','snow water equivalent'],
                          )

# mass balance for domain average 1200m
time_data = get_time_value(file_path=app_SWIT, time_var='time', units=None, calendar=None)
time_data_daily = [time_data[i] for i in range(0,len(time_data), 4)]
time_data_prcp = get_time_value(file_path=app_prcp, time_var='time', units=None, calendar=None)

app_prcp_data_ave_acc = get_cumulative(app_prcp_ave, cumulative_scale=24)
app_swit_data_ave_acc = get_cumulative(app_swit_data_ave, cumulative_scale=6)
app_swe_data_ave_daily = [app_swe_data_ave[i] for i in range(0, len(app_swe_data_ave), 4)]
app_swit_data_acc_daily = [app_swit_data_ave_acc[i] for i in range(0, len(app_swit_data_ave_acc), 4)]


plot_multiple_time_series(time_data_daily, [app_prcp_data_ave_acc[:-1],
                                           app_swit_data_acc_daily,
                                           app_swe_data_ave_daily
                                                ],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance for domain average (1200m)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','snow water equivalent'],
                          )

# difference 600-1200 for accumulative swit and prcp
fig, ax = plt.subplots(2,1)
plot_multiple_time_series(time_data,
                          [[jupyter - app for jupyter, app in zip(jupyter_swit_data_ave_acc, app_swit_data_ave_acc)],
                           ],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of accumulative rain plus melt (600m vs 1200m)',
                          xlabel='Time', ylabel='rain plus melt (m)',
                          line_label_list=['difference of rain plus melt'],
                          )

plot_multiple_time_series(time_data_prcp,
                          [[jupyter - app for jupyter, app in zip(jupyter_prcp_data_ave_acc, app_prcp_data_ave_acc)],
                           ],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of accumulative precipitation (600m vs 1200m)',
                          xlabel='Time', ylabel='prcp (m)',
                          line_label_list=['difference of precipitation'],
                          )

# compare Cascade point 600 vs 1200 ###########################################################################################
# prcp cascade
jupyter_prcp_data_point = get_var_point_data(file_path=jupyter_prcp, var_name='prcp', x_index=39, y_index=72, var_dim_list=['time','y','x'])
app_prcp_data_point = get_var_point_data(file_path=app_prcp, var_name='prcp', x_index=19, y_index=36, var_dim_list=['time','y','x'])
diff_prcp_point = [jupyter - app for jupyter, app in zip(jupyter_prcp_data_point, app_prcp_data_point)]
time_data = get_time_value(file_path=jupyter_prcp, time_var='time', units=None, calendar=None)
fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(time_data,
                          [jupyter_prcp_data_point,
                           app_prcp_data_point,
                           # diff_swe_point
                           ],
                          color_list=None,
                          ax=ax[0],
                          fig=fig,
                          month_interval=1, legend=True,
                          title='Comparision of precipitation at Cascade station',
                          xlabel='Time', ylabel='precipitation(mm/hr)',
                          line_label_list=['600m','1200m',
                                           # 'difference'
                                           ],
                          # save_as='compare_swit_ave_app_jupyter.png',
                          )

plot_multiple_time_series(time_data, [diff_prcp_point],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the precipitation at Cascade station (600m vs 1200m)',
                          xlabel='Time', ylabel='precipitation (mm/hr)',
                          line_label_list=['difference'],
                          # save_as='compare_prcp_ave_app_jupyter.png',
                          )

# swe cascade
time_data = get_time_value(file_path=jupyter_SWE, time_var='time', units=None, calendar=None)
jupyter_swe_data_point = get_var_point_data(file_path=jupyter_SWE, var_name='SWE', x_index=39, y_index=72, var_dim_list=['time','y','x'])
app_swe_data_point = get_var_point_data(file_path=app_SWE, var_name='SWE', x_index=19, y_index=36, var_dim_list=['time','y','x'])
diff_swe_point = [jupyter - app for jupyter , app in zip(jupyter_swe_data_point, app_swe_data_point)]

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(time_data,
                          [jupyter_swe_data_point,
                           app_swe_data_point,
                           # diff_swe_point
                           ],
                          color_list=None,
                          ax=ax[0],
                          fig=fig,
                          month_interval=1, legend=True,
                          title='Comparision of SWE at Cascade station',
                          xlabel='Time', ylabel='swe (m)',
                          line_label_list=['600m','1200m',
                                           # 'difference'
                                           ],
                          # save_as='compare_swit_ave_app_jupyter.png',
                          )

plot_multiple_time_series(time_data, [diff_swe_point],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the SWE at Cascade station (600m vs 1200m)',
                          xlabel='Time', ylabel='swe (m)',
                          line_label_list=['difference'],
                          # save_as='compare_prcp_ave_app_jupyter.png',
                          )

# swit cascade
jupyter_swit_data_point = get_var_point_data(file_path=jupyter_SWIT, var_name='SWIT', x_index=39, y_index=72, var_dim_list=['time','y','x'])
app_swit_data_point = get_var_point_data(file_path=app_SWIT, var_name='SWIT', x_index=19, y_index=36, var_dim_list=['time','y','x'])
diff_swit_point = [jupyter - app for jupyter, app in zip(jupyter_swit_data_point, app_swit_data_point)]

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(time_data,
                          [jupyter_swit_data_point,
                           app_swit_data_point,
                           # diff_swe_point
                           ],
                          color_list=None,
                          ax=ax[0],
                          fig=fig,
                          month_interval=1, legend=True,
                          title='Comparision of rain plus melt at Cascade station',
                          xlabel='Time', ylabel='rain plus melt(m/hr)',
                          line_label_list=['600m','1200m',
                                           # 'difference'
                                           ],
                          # save_as='compare_swit_ave_app_jupyter.png',
                          )

plot_multiple_time_series(time_data, [diff_swit_point],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the rain plus melt point results (600m-1200m)',
                          xlabel='Time', ylabel='rain plus melt (m/hr)',
                          line_label_list=['difference'],
                          # save_as='compare_prcp_ave_app_jupyter.png',
                          )


# mass balance for cascade point 600m
time_data = get_time_value(file_path=jupyter_SWIT, time_var='time', units=None, calendar=None)
time_data_prcp = get_time_value(file_path=jupyter_prcp, time_var='time', units=None, calendar=None)
jupyter_swit_point = get_var_point_data(file_path=jupyter_SWIT, var_name='SWIT', x_index=39, y_index=72, var_dim_list=['time','y','x'])
jupyter_prcp_point = get_var_point_data(file_path=jupyter_prcp, var_name='prcp', x_index=39, y_index=72, var_dim_list=['time','y','x'])
jupyter_swe_point = get_var_point_data(file_path=jupyter_SWE,var_name='SWE', x_index=39, y_index=72, var_dim_list=['time','y','x'])


jupyter_prcp_data_acc = get_cumulative(jupyter_prcp_point, cumulative_scale=24)
jupyter_swit_data_acc = get_cumulative(jupyter_swit_point, cumulative_scale=6)
jupyter_swe_point_daily = [jupyter_swe_point[i] for i in range(0, len(jupyter_swe_point),4)]
jupyter_swit_data_acc_daily = [jupyter_swit_data_acc[i] for i in range(0, len(jupyter_swit_data_acc),4)]


plot_multiple_time_series(time_data, [jupyter_swit_data_acc, jupyter_swe_point],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance comparison with hourly data (600m)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative rain plus melt','snow water equivalent'],
                          # save_as='compare_swit_prcp_molaslake.png',
                          )

plot_multiple_time_series(time_data_prcp[:-1], [jupyter_prcp_data_acc[:-1],
                                                jupyter_swit_data_acc_daily,
                                                jupyter_swe_point_daily
                                                ],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance comparison daily data (600m)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','snow water equivalent'],
                          save_as='compare_swit_prcp_molaslake.png',
                          )


# mass balance for cascade point 1200m
time_data = get_time_value(file_path=app_SWIT, time_var='time', units=None, calendar=None)
time_data_prcp = get_time_value(file_path=app_prcp, time_var='time', units=None, calendar=None)
app_swit_point = get_var_point_data(file_path=app_SWIT, var_name='SWIT', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_prcp_point = get_var_point_data(file_path=app_prcp, var_name='prcp', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_swe_point = get_var_point_data(file_path=app_SWE, var_name='SWE', x_index=19, y_index=36, var_dim_list=['time','y','x'])


app_prcp_data_acc = get_cumulative(app_prcp_point, cumulative_scale=24)
app_swit_data_acc = get_cumulative(app_swit_point, cumulative_scale=6)
app_swe_point_daily = [app_swe_point[i] for i in range(0, len(app_swe_point),4)]
app_swit_data_acc_daily = [app_swit_data_acc[i] for i in range(0, len(app_swit_data_acc),4)]


plot_multiple_time_series(time_data, [app_swit_data_acc, app_swe_point],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance comparison with hourly data(1200m)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative rain plus melt','snow water equivalent'],
                          # save_as='compare_swit_prcp_molaslake.png',
                          )

plot_multiple_time_series(time_data_prcp[:-1], [app_prcp_data_acc[1:],
                                                app_swit_data_acc_daily,
                                                app_swe_point_daily
                                                ],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance comparison with daily data(1200m)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','snow water equivalent'],
                          save_as='compare_swit_prcp_molaslake.png',
                          )


# compare observation data at cascade 1200m ##############################################################################
obs_prcp = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\386_17_WATERYEAR=2010.csv'
obs_swe = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\386_26_WATERYEAR=2010.csv'
obs_temp = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\386_1_WATERYEAR=2010.csv'
app_SWE = os.path.join(app_dir, 'SWE.nc')
app_prcp= os.path.join(app_dir,'prcp0.nc')
app_tmax= os.path.join(app_dir,'tmax0.nc')
app_tmin = os.path.join(app_dir,'tmin0.nc')

# prcp obs vs sim cascade
app_time = get_time_value(file_path=app_prcp, time_var='time', units=None, calendar=None)
app_prcp_point = get_var_point_data(file_path=app_prcp, var_name='prcp', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_prcp_data_acc = get_cumulative(app_prcp_point, cumulative_scale=24)
app_prcp_daily = [app_prcp_data_acc[i]-app_prcp_data_acc[i-1] for i in range(1, len(app_prcp_data_acc))]
start_date_str = datetime.strftime(app_time[0], '%Y-%m-%d')
end_date_str = datetime.strftime(app_time[-1], '%Y-%m-%d')

raw_prcp = pd.read_csv(obs_prcp, skiprows=4, header=None)
obs_time = raw_prcp[1].tolist()
obs_prcp_acc = [x*0.0254 for x in raw_prcp[3].tolist()]
obs_prcp_acc = obs_prcp_acc[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]
obs_prcp_daily = [obs_prcp_acc[i]-obs_prcp_acc[i-1] for i in range(1, len(obs_prcp_acc))]

diff_prcp_acc = [x-y for x, y in zip(obs_prcp_acc, app_prcp_data_acc)]
diff_prcp_point = [x-y for x, y in zip(obs_prcp_daily, app_prcp_daily)]

fig,ax = plt.subplots(2,1)
plot_multiple_time_series(app_time, [obs_prcp_acc, app_prcp_data_acc],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of accumulative precipitation (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='prcp(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

plot_multiple_time_series(app_time, [diff_prcp_acc],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of accumulative precipitation (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='prcp(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

fig,ax = plt.subplots(2,1)
plot_multiple_time_series(app_time[:-1], [obs_prcp_daily, app_prcp_daily],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of daily precipitation (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='prcp(m/day)',
                          line_label_list=['snotel','daymet','difference'],
                          )

plot_multiple_time_series(app_time[:-1], [diff_prcp_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of daily precipitation (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='prcp(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )


# swe obs vs sim cascade
app_time = get_time_value(file_path=app_SWE, time_var='time', units=None, calendar=None)
app_swe_point = get_var_point_data(file_path=app_SWE, var_name='SWE', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_time_daily = [app_time[i] for i in range(0, len(app_swe_point), 4)]
app_swe_point_daily = [app_swe_point[i] for i in range(0, len(app_swe_point), 4)]
start_date_str = datetime.strftime(app_time_daily[0], '%#m/%#d/%Y')
end_date_str = datetime.strftime(app_time_daily[-1], '%#m/%#d/%Y')

raw_swe = pd.read_csv(obs_swe, skiprows=3, header=None)
obs_time = raw_swe[1].tolist()
obs_swe = [ float(x) for x in raw_swe[4].tolist()]
obs_swe = obs_swe[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]

diff_swe = [x - y for x, y in zip(obs_swe, app_swe_point_daily)]
fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time_daily, [obs_swe, app_swe_point_daily],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of SWE at Cascade (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='swe(m)',
                          line_label_list=['snotel','daymet'],
                          )


plot_multiple_time_series(app_time_daily, [diff_swe],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of swe (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='swe(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

# tmax tmin obs vs sim cascade
app_time = get_time_value(file_path=app_tmax, time_var='time', units=None, calendar=None)
app_tmax_point = get_var_point_data(file_path=app_tmax, var_name='tmax', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_tmin_point = get_var_point_data(file_path=app_tmin, var_name='tmin', x_index=19, y_index=36, var_dim_list=['time','y','x'])
start_date_str = datetime.strftime(app_time[0], '%Y-%m-%d')
end_date_str = datetime.strftime(app_time[-1], '%Y-%m-%d')

raw_temp = pd.read_csv(obs_temp, skiprows=4, header=None)
obs_time = raw_temp[1].tolist()
obs_tmax = raw_temp[4].tolist()
obs_tmin = raw_temp[5].tolist()
obs_tmax = obs_tmax[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]
obs_tmin = obs_tmin[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]

diff_tmax_point = [x-y for x, y in zip(obs_tmax, app_tmax_point)]
diff_tmin_point = [x-y for x, y in zip(obs_tmin, app_tmin_point)]

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time, [obs_tmax, app_tmax_point],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of max temperature (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet'],
                          )


plot_multiple_time_series(app_time, [diff_tmax_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of max temperature (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet','difference'],
                          )

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time, [obs_tmin, app_tmin_point],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of min temperature (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet'],
                          )


plot_multiple_time_series(app_time, [diff_tmin_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of min temperature (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet','difference'],
                          )


# compare observation data at cascade 600m ##############################################################################
obs_prcp = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\386_17_WATERYEAR=2010.csv'
obs_swe = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\386_26_WATERYEAR=2010.csv'
obs_temp = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\386_1_WATERYEAR=2010.csv'
app_SWE = os.path.join(jupyter_dir, 'SWE.nc')
app_prcp= os.path.join(jupyter_dir,'prcp0.nc')
app_tmax= os.path.join(jupyter_dir,'tmax0.nc')
app_tmin = os.path.join(jupyter_dir,'tmin0.nc')

# prcp obs vs sim cascade
app_time = get_time_value(file_path=app_prcp, time_var='time', units=None, calendar=None)
app_prcp_point = get_var_point_data(file_path=app_prcp, var_name='prcp', x_index=39, y_index=72, var_dim_list=['time','y','x'])
app_prcp_data_acc = get_cumulative(app_prcp_point, cumulative_scale=24)
app_prcp_daily = [app_prcp_data_acc[i]-app_prcp_data_acc[i-1] for i in range(1, len(app_prcp_data_acc))]
start_date_str = datetime.strftime(app_time[0], '%Y-%m-%d')
end_date_str = datetime.strftime(app_time[-1], '%Y-%m-%d')

raw_prcp = pd.read_csv(obs_prcp, skiprows=4, header=None)
obs_time = raw_prcp[1].tolist()
obs_prcp_acc = [x*0.0254 for x in raw_prcp[3].tolist()]
obs_prcp_acc = obs_prcp_acc[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]
obs_prcp_daily = [obs_prcp_acc[i]-obs_prcp_acc[i-1] for i in range(1, len(obs_prcp_acc))]

diff_prcp_acc = [x-y for x, y in zip(obs_prcp_acc, app_prcp_data_acc)]
diff_prcp_point = [x-y for x, y in zip(obs_prcp_daily, app_prcp_daily)]

fig,ax = plt.subplots(2,1)
plot_multiple_time_series(app_time, [obs_prcp_acc, app_prcp_data_acc],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of accumulative precipitation (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='prcp(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

plot_multiple_time_series(app_time, [diff_prcp_acc],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of accumulative precipitation (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='prcp(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

fig,ax = plt.subplots(2,1)
plot_multiple_time_series(app_time[:-1], [obs_prcp_daily, app_prcp_daily],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of daily precipitation (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='prcp(m/day)',
                          line_label_list=['snotel','daymet','difference'],
                          )

plot_multiple_time_series(app_time[:-1], [diff_prcp_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of daily precipitation (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='prcp(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )


# swe obs vs sim cascade
app_time = get_time_value(file_path=app_SWE, time_var='time', units=None, calendar=None)
app_swe_point = get_var_point_data(file_path=app_SWE, var_name='SWE', x_index=39, y_index=72, var_dim_list=['time','y','x'])
app_time_daily = [app_time[i] for i in range(0, len(app_swe_point), 4)]
app_swe_point_daily = [app_swe_point[i] for i in range(0, len(app_swe_point), 4)]
start_date_str = datetime.strftime(app_time_daily[0], '%#m/%#d/%Y')
end_date_str = datetime.strftime(app_time_daily[-1], '%#m/%#d/%Y')

raw_swe = pd.read_csv(obs_swe, skiprows=3, header=None)
obs_time = raw_swe[1].tolist()
obs_swe = [ float(x) for x in raw_swe[4].tolist()]
obs_swe = obs_swe[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]

diff_swe = [x - y for x, y in zip(obs_swe, app_swe_point_daily)]
fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time_daily, [obs_swe, app_swe_point_daily],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of SWE at Cascade (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='swe(m)',
                          line_label_list=['snotel','daymet'],
                          )


plot_multiple_time_series(app_time_daily, [diff_swe],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of swe (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='swe(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

# tmax tmin obs vs sim cascade
app_time = get_time_value(file_path=app_tmax, time_var='time', units=None, calendar=None)
app_tmax_point = get_var_point_data(file_path=app_tmax, var_name='tmax', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_tmin_point = get_var_point_data(file_path=app_tmin, var_name='tmin', x_index=19, y_index=36, var_dim_list=['time','y','x'])
start_date_str = datetime.strftime(app_time[0], '%Y-%m-%d')
end_date_str = datetime.strftime(app_time[-1], '%Y-%m-%d')

raw_temp = pd.read_csv(obs_temp, skiprows=4, header=None)
obs_time = raw_temp[1].tolist()
obs_tmax = raw_temp[4].tolist()
obs_tmin = raw_temp[5].tolist()
obs_tmax = obs_tmax[obs_time.index(start_date_str)+1: obs_time.index(end_date_str)+2]
obs_tmin = obs_tmin[obs_time.index(start_date_str)+1: obs_time.index(end_date_str)+2]

diff_tmax_point = [x-y for x, y in zip(obs_tmax, app_tmax_point)]
diff_tmin_point = [x-y for x, y in zip(obs_tmin, app_tmin_point)]

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time, [obs_tmax, app_tmax_point],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of max temperature (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet'],
                          )

plot_multiple_time_series(app_time, [obs_tmin, app_tmin_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of min temperature (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet'],
                          )


fig, ax = plt.subplots(2, 1)

plot_multiple_time_series(app_time, [diff_tmin_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of min temperature (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['difference'],
                          )
plot_multiple_time_series(app_time, [diff_tmax_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of max temperature (snotel vs daymet) at Cascade',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['difference'],
                          )



# compare Molas lake point 600 vs 1200 (Not finished) ###########################################################################################
# prcp
jupyter_prcp_data_point = get_var_point_data(file_path=jupyter_prcp, var_name='prcp', x_index=39, y_index=72, var_dim_list=['time','y','x'])
app_prcp_data_point = get_var_point_data(file_path=app_prcp, var_name='prcp', x_index=19, y_index=36, var_dim_list=['time','y','x'])
diff_prcp_point = [jupyter - app for jupyter, app in zip(jupyter_prcp_data_point, app_prcp_data_point)]
time_data = get_time_value(file_path=jupyter_prcp, time_var='time', units=None, calendar=None)
fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(time_data,
                          [jupyter_prcp_data_point,
                           app_prcp_data_point,
                           # diff_swe_point
                           ],
                          color_list=None,
                          ax=ax[0],
                          fig=fig,
                          month_interval=1, legend=True,
                          title='Comparision of precipitation at Cascade station',
                          xlabel='Time', ylabel='precipitation(mm/hr)',
                          line_label_list=['600m','1200m',
                                           # 'difference'
                                           ],
                          # save_as='compare_swit_ave_app_jupyter.png',
                          )

plot_multiple_time_series(time_data, [diff_prcp_point],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the precipitation at Cascade station (600m vs 1200m)',
                          xlabel='Time', ylabel='precipitation (mm/hr)',
                          line_label_list=['difference'],
                          # save_as='compare_prcp_ave_app_jupyter.png',
                          )

# swe
jupyter_swe_data_point = get_var_point_data(file_path=jupyter_SWE, var_name='SWE', x_index=39, y_index=72, var_dim_list=['time','y','x'])
app_swe_data_point = get_var_point_data(file_path=app_SWE, var_name='SWE', x_index=19, y_index=36, var_dim_list=['time','y','x'])
diff_swe_point = [jupyter - app for jupyter , app in zip(jupyter_swe_data_point, app_swe_data_point)]

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(time_data,
                          [jupyter_swe_data_point,
                           app_swe_data_point,
                           # diff_swe_point
                           ],
                          color_list=None,
                          ax=ax[0],
                          fig=fig,
                          month_interval=1, legend=True,
                          title='Comparision of SWE at Cascade station',
                          xlabel='Time', ylabel='swe (m)',
                          line_label_list=['600m','1200m',
                                           # 'difference'
                                           ],
                          # save_as='compare_swit_ave_app_jupyter.png',
                          )

plot_multiple_time_series(time_data, [diff_swe_point],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the SWE at Cascade station (600m vs 1200m)',
                          xlabel='Time', ylabel='swe (m)',
                          line_label_list=['difference'],
                          # save_as='compare_prcp_ave_app_jupyter.png',
                          )

# swit
jupyter_swit_data_point = get_var_point_data(file_path=jupyter_SWIT, var_name='SWIT', x_index=39, y_index=72, var_dim_list=['time','y','x'])
app_swit_data_point = get_var_point_data(file_path=app_SWIT, var_name='SWIT', x_index=19, y_index=36, var_dim_list=['time','y','x'])
diff_swit_point = [jupyter - app for jupyter, app in zip(jupyter_swit_data_point, app_swit_data_point)]

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(time_data,
                          [jupyter_swit_data_point,
                           app_swit_data_point,
                           # diff_swe_point
                           ],
                          color_list=None,
                          ax=ax[0],
                          fig=fig,
                          month_interval=1, legend=True,
                          title='Comparision of SWIT at Cascade station',
                          xlabel='Time', ylabel='SWIT(m/hr)',
                          line_label_list=['600m','1200m',
                                           # 'difference'
                                           ],
                          # save_as='compare_swit_ave_app_jupyter.png',
                          )

plot_multiple_time_series(time_data, [diff_swit_point],
                          ax=ax[1],
                          fig=fig,
                          title='Difference of the SWE point results (600m-1200m)',
                          xlabel='Time', ylabel='swe (m)',
                          line_label_list=['difference'],
                          # save_as='compare_prcp_ave_app_jupyter.png',
                          )


# mass balance for molas lake point 600m
time_data = get_time_value(file_path=jupyter_SWIT, time_var='time', units=None, calendar=None)
time_data_prcp = get_time_value(file_path=jupyter_prcp, time_var='time', units=None, calendar=None)
jupyter_swit_point = get_var_point_data(file_path=jupyter_SWIT, var_name='SWIT', x_index=38, y_index=72, var_dim_list=['time','y','x'])
jupyter_prcp_point = get_var_point_data(file_path=jupyter_prcp, var_name='prcp', x_index=38, y_index=72, var_dim_list=['time','y','x'])
jupyter_swe_point = get_var_point_data(file_path=jupyter_SWE,var_name='SWE', x_index=38, y_index=72, var_dim_list=['time','y','x'])


jupyter_prcp_data_acc = get_cumulative(jupyter_prcp_point, cumulative_scale=24)
jupyter_swit_data_acc = get_cumulative(jupyter_swit_point, cumulative_scale=6)
jupyter_swe_point_daily = [jupyter_swe_point[i] for i in range(0, len(jupyter_swe_point),4)]
jupyter_swit_data_acc_daily = [jupyter_swit_data_acc[i] for i in range(0, len(jupyter_swit_data_acc),4)]


plot_multiple_time_series(time_data, [jupyter_swit_data_acc, jupyter_swe_point],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance comparison with observation',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative rain plus melt','snow water equivalent'],
                          # save_as='compare_swit_prcp_molaslake.png',
                          )

plot_multiple_time_series(time_data_prcp[:-1], [jupyter_prcp_data_acc[:-1],
                                                jupyter_swit_data_acc_daily,
                                                jupyter_swe_point_daily
                                                ],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance comparison with observation',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','snow water equivalent'],
                          save_as='compare_swit_prcp_molaslake.png',
                          )


# mass balance for molas lake point 1200m
time_data = get_time_value(file_path=app_SWIT, time_var='time', units=None, calendar=None)
time_data_prcp = get_time_value(file_path=app_prcp, time_var='time', units=None, calendar=None)
app_swit_point = get_var_point_data(file_path=app_SWIT, var_name='SWIT', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_prcp_point = get_var_point_data(file_path=app_prcp, var_name='prcp', x_index=19, y_index=36, var_dim_list=['time','y','x'])
app_swe_point = get_var_point_data(file_path=app_SWE, var_name='SWE', x_index=19, y_index=36, var_dim_list=['time','y','x'])


app_prcp_data_acc = get_cumulative(app_prcp_point, cumulative_scale=24)
app_swit_data_acc = get_cumulative(app_swit_point, cumulative_scale=6)
app_swe_point_daily = [app_swe_point[i] for i in range(0, len(app_swe_point),4)]
app_swit_data_acc_daily = [app_swit_data_acc[i] for i in range(0, len(app_swit_data_acc),4)]


plot_multiple_time_series(time_data, [app_swit_data_acc, app_swe_point],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance comparison with observation',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative rain plus melt','snow water equivalent'],
                          # save_as='compare_swit_prcp_molaslake.png',
                          )

plot_multiple_time_series(time_data_prcp[:-1], [app_prcp_data_acc[1:],
                                                app_swit_data_acc_daily,
                                                app_swe_point_daily
                                                ],
                          color_list=None, month_interval=1, legend=True,
                          title='Mass balance comparison with observation',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','snow water equivalent'],
                          save_as='compare_swit_prcp_molaslake.png',
                          )


# compare observation data at molas lake ##############################################################################
obs_prcp = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\632_17_WATERYEAR=2010.csv'
obs_swe = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\632_26_WATERYEAR=2010.csv'
obs_temp = r'D:\3_NASA_Project\UEB_web_app_use_case\2010_water_year snotel observation\632_1_WATERYEAR=2010.csv'
app_SWE = os.path.join(app_dir, 'SWE.nc')
app_prcp= os.path.join(app_dir,'prcp0.nc')
app_tmax= os.path.join(app_dir,'tmax0.nc')
app_tmin = os.path.join(app_dir,'tmin0.nc')

# prcp obs vs sim molas lake
app_time = get_time_value(file_path=app_prcp, time_var='time', units=None, calendar=None)
app_prcp_point = get_var_point_data(file_path=app_prcp, var_name='prcp', x_index=28, y_index=45, var_dim_list=['time','y','x'])
app_prcp_data_acc = get_cumulative(app_prcp_point, cumulative_scale=24)
app_prcp_daily = [app_prcp_data_acc[i]-app_prcp_data_acc[i-1] for i in range(1, len(app_prcp_data_acc))]
start_date_str = datetime.strftime(app_time[0], '%Y-%m-%d')
end_date_str = datetime.strftime(app_time[-1], '%Y-%m-%d')

raw_prcp = pd.read_csv(obs_prcp, skiprows=4, header=None)
obs_time = raw_prcp[1].tolist()
obs_prcp_acc = [x*0.0254 for x in raw_prcp[3].tolist()]
obs_prcp_acc = obs_prcp_acc[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]
obs_prcp_daily = [obs_prcp_acc[i]-obs_prcp_acc[i-1] for i in range(1, len(obs_prcp_acc))]

diff_prcp_acc = [x-y for x, y in zip(obs_prcp_acc, app_prcp_data_acc)]
diff_prcp_point = [x-y for x, y in zip(obs_prcp_daily, app_prcp_daily)]

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time, [obs_prcp_acc, app_prcp_data_acc],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of accumulative precipitation (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='prcp(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

plot_multiple_time_series(app_time, [diff_prcp_acc],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of accumulative precipitation (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='prcp(m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

fig,ax = plt.subplots(2,1)
plot_multiple_time_series(app_time[:-1], [obs_prcp_daily, app_prcp_daily],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of daily precipitation (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='prcp(m/day)',
                          line_label_list=['snotel','daymet','difference'],
                          )

plot_multiple_time_series(app_time[:-1], [diff_prcp_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of daily precipitation (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='prcp(m/day)',
                          line_label_list=['snotel','daymet','difference'],
                          )


# swe obs vs sim Molas lake
app_time = get_time_value(file_path=app_SWE, time_var='time', units=None, calendar=None)
app_swe_point = get_var_point_data(file_path=app_SWE, var_name='SWE', x_index=28, y_index=45, var_dim_list=['time','y','x'])
app_time_daily = [app_time[i] for i in range(0, len(app_swe_point), 4)]
app_swe_point_daily = [app_swe_point[i] for i in range(0, len(app_swe_point), 4)]
start_date_str = datetime.strftime(app_time_daily[0], '%Y-%m-%d')
end_date_str = datetime.strftime(app_time_daily[-1], '%Y-%m-%d')

raw_swe = pd.read_csv(obs_swe, skiprows=4, header=None)
obs_time = raw_swe[1].tolist()
obs_swe = [float(x)*0.0254 for x in raw_swe[3].tolist()]
obs_swe = obs_swe[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]

diff_swe = [x - y for x, y in zip(obs_swe, app_swe_point_daily)]
fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time_daily, [obs_swe, app_swe_point_daily],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of swe (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='swe(m)',
                          line_label_list=['snotel','daymet'],
                          )


plot_multiple_time_series(app_time_daily, [diff_swe],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of swe (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='swe (m)',
                          line_label_list=['snotel','daymet','difference'],
                          )

# tmax tmin obs vs sim Molas lake
app_time = get_time_value(file_path=app_tmax, time_var='time', units=None, calendar=None)
app_tmax_point = get_var_point_data(file_path=app_tmax, var_name='tmax', x_index=28, y_index=45, var_dim_list=['time','y','x'])
app_tmin_point = get_var_point_data(file_path=app_tmin, var_name='tmin', x_index=28, y_index=45, var_dim_list=['time','y','x'])
start_date_str = datetime.strftime(app_time[0], '%#m/%#d/%#Y')
end_date_str = datetime.strftime(app_time[-1], '%#m/%#d/%#Y')

raw_temp = pd.read_csv(obs_temp, skiprows=3, header=None)
obs_time = raw_temp[1].tolist()
obs_tmax = raw_temp[4].tolist()
obs_tmin = raw_temp[5].tolist()
obs_tmax = obs_tmax[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]
obs_tmin = obs_tmin[obs_time.index(start_date_str): obs_time.index(end_date_str)+1]

diff_tmax_point = [x-y for x, y in zip(obs_tmax, app_tmax_point)]
diff_tmin_point = [x-y for x, y in zip(obs_tmin, app_tmin_point)]

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time, [obs_tmax, app_tmax_point],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of max temperature (snotel vs daymet)at Molas Lake',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet'],
                          )


plot_multiple_time_series(app_time, [diff_tmax_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of max temperature (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet','difference'],
                          )

fig, ax = plt.subplots(2, 1)
plot_multiple_time_series(app_time, [obs_tmin, app_tmin_point],
                          ax=ax[0],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Comparison of min temperature (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet'],
                          )


plot_multiple_time_series(app_time, [diff_tmin_point],
                          ax=ax[1],
                          fig=fig,
                          color_list=None, month_interval=1, legend=True,
                          title='Difference of min temperature (snotel vs daymet) at Molas Lake',
                          xlabel='Time', ylabel='temp(degree C)',
                          line_label_list=['snotel','daymet','difference'],
                          )