"""
This is to analyze the 22yr UEB output point data for UEB+SAC workflow.

1 get model simulation data for prec, snow: ts, accumulated
4 get observation data for prec, snow : ts, accumulated
3 plot swit, swe, mass balance for observation and simulation(prcp,swe,swit)

This method uses the data of prcp, swit, swe from netCDF output files.
Note: only run successfully when the snow model data is small. file larger than 600MB will fail.


"""

import os
from datetime import datetime, timedelta
import pandas as pd
import urllib

from plot_multiple_time_series import *


watershed = 'Animas'
prcp_dir = r'D:\3_NASA_Project\Model output and plots\22yr_Animas_watershed\22yr_Animas_UEB_sections_model_results\ueb_model_run_22yr_work_1988_1994'
snow_dir = os.getcwd()#r'D:\3_NASA_Project\Model output and plots\22yr_Animas_watershed\22yr_Animas_UEB_sections_model_results\ueb_22yr_output_netcdf'

results_dir = r'C:\Users\jamy\Desktop\Nasa_analysis'
results_dir = os.path.join(results_dir, '{}_snow_analysis_point'.format(watershed))
if not os.path.isdir(results_dir):
    os.mkdir(results_dir)

start_time = '' #'1988-10-01'
end_time = '' #'1989-9-30'
time_step = 3

point_info = {
    'cascade': [19, 36],  # xindex, yindex
    'molaslake': [28, 45]
}

snotel_info = {
    'cascade': 'https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultiTimeSeriesGroupByStationReport/daily/start_of_period/386:CO:SNTL%7Cid=%22%22%7Cname/1987-10-01,2010-10-01/WTEQ::value,PREC::value?fitToScreen=false',
    'molaslake': 'https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultiTimeSeriesGroupByStationReport/daily/start_of_period/632:CO:SNTL%7Cid=%22%22%7Cname/1987-10-01,2010-10-01/WTEQ::value,PREC::value?fitToScreen=false'
}

# Get simulation Data ##################################################


# get prcp data
prcp_22yr = {}
for name, index in point_info.items():
    prcp = []
    time = []
    for i in range(0, 22):
        file_path = os.path.join(prcp_dir, 'prcp{}.nc'.format(i))

        var_point = get_var_point_data(file_path=file_path, var_name='ogrid', x_index=index[0], y_index=index[1],
                                       var_dim_list=['time', 'y', 'x'])
        time_data = get_time_value(file_path, 'time')
        prcp.extend(var_point)
        time.extend(time_data)

    prcp_acc = get_cumulative(prcp, cumulative_scale=time_step)

    prcp_df = pd.DataFrame(
        data={'time': time, 'prcp': prcp, 'prcp_acc': prcp_acc},
        columns=['time', 'prcp', 'prcp_acc']
    )
    prcp_df.to_csv(os.path.join(results_dir,'{}_prcp.csv'.format(name)))
    prcp_22yr[name] = prcp_df


# get snow point data
snow_22yr = {}
for name, index in point_info.items():
    swit_file = os.path.join(snow_dir, 'SWIT.nc')
    swe_file = os.path.join(snow_dir, 'SWE.nc')

    time_data = get_time_value(file_path=swit_file, time_var='time', units=None, calendar=None)
    swit_data_point = get_var_point_data(file_path=swit_file, var_name='SWIT', x_index=index[0], y_index=index[1],
                                   var_dim_list=['y', 'x', 'time'])
    swit_data_acc = get_cumulative(swit_data_point, cumulative_scale=time_step)
    swe_data_point = get_var_point_data(file_path=swe_file, var_name='SWE', x_index=index[0], y_index=index[1],
                                   var_dim_list=['y', 'x', 'time'])

    snow_df = pd.DataFrame(
        data={'time': [x-timedelta(hours=7) for x in time_data],
              'swit': swit_data_point,
              'swit_acc': swit_data_acc,
              'swe': swe_data_point},
        columns=['time','swit','swit_acc', 'swe'],
    )

    snow_df.to_csv(os.path.join(results_dir, '{}_snow.csv'.format(name)))

    snow_22yr[name] = snow_df

# Make simulation plots ########################################################
for name in point_info.keys():
    point_snow = snow_22yr[name]
    point_prcp = prcp_22yr[name]
    DF = pd.merge(point_snow, point_prcp, on='time')
    if start_time and end_time:
        DF = DF.ix[(DF.time >= start_time) & (DF.time <= end_time)]

    xlim = [datetime(DF.time[0].year, 1, 1), datetime(DF.time.iloc[-1].year, 12, 31)]
    time_format = '%Y'
    month_interval = 12

    # point plots
    plot_multiple_time_series(DF.time, [DF.swe],
                          title='{} station SWE'.format(name),
                          ylabel='SWE(m)',
                          month_interval=month_interval,
                          time_format=time_format,
                          xlim=xlim,
                          save_as=os.path.join(results_dir, '{}_swe.png'.format(name))
                          )

    plot_multiple_time_series(DF.time, [DF.swit],
                          month_interval=month_interval,
                          time_format=time_format,
                          title='{} station rain plus melt'.format(name),
                          ylabel='Rain plus melt (m/hr)',
                          xlim=xlim,
                          save_as=os.path.join(results_dir, '{}_swit.png'.format(name))
                          )

    plot_multiple_time_series(DF.time,
                          [DF.prcp_acc,
                           DF.swit_acc,
                           DF.swe
                           ],
                           title='{} station mass balance'.format(name),
                           line_label_list=['cumulative precipitation',
                                           'cumulative rain plus melt',
                                           'snow water equivalent'
                                            ],
                           legend=True,
                           month_interval=month_interval,
                           time_format=time_format,
                           xlim=xlim,
                           ylabel='cumulative depth(m)',
                           save_as=os.path.join(results_dir, '{}_mass_balance.png'.format(name))
                          )

print 'Analysis is done !'


# Get observation Data ##################################################
snotel_22yr = {}

for name, url in snotel_info.items():
    # instantaneous value at the start of the day for swe, prcp acc
    file_name = os.path.join(results_dir, '{}_snotel.csv'.format(name))
    urllib.urlretrieve(url, file_name)
    snotel_22yr[name] = pd.read_csv(file_name, header=54)
    snotel_22yr[name].columns = ['time', 'swe', 'prcp_acc']  #  prcp accumulative for each water year

    snotel_22yr[name]['time'] = pd.to_datetime(snotel_22yr[name].time)
    snotel_22yr[name]['swe_m'] = snotel_22yr[name].swe * 0.0254
    snotel_22yr[name]['prcp_acc_m'] = snotel_22yr[name].prcp_acc * 0.0254

    snotel_22yr[name]['prcp_m'] = ''

    for year in range(snotel_22yr[name]['time'][0].year, snotel_22yr[name]['time'].iloc[-1].year):
        df = snotel_22yr[name][['prcp_acc_m', 'time']].ix[
            (snotel_22yr[name].time >= '{}-10-01'.format(year)) &
            (snotel_22yr[name].time <= '{}-10-01'.format(year+1))
            ]

        data = df['prcp_acc_m'].tolist()
        index = df.index[:-1]
        new_data = [data[i + 1] - data[i] for i in range(0, len(data)) if i < len(data)-2]
        new_data.append(data[-1])

        snotel_22yr[name].loc[index, 'prcp_m'] = new_data



# Make sim vs obs plots ###############################################
for name in snotel_info.keys():
    obs_snow = snotel_22yr[name][['time', 'swe_m']]
    sim_snow = snow_22yr[name].set_index('time')[['swe']].resample('D').mean().reset_index()
    snow_df = pd.merge(sim_snow, obs_snow, on='time')

    sim_prcp_acc = prcp_22yr[name].set_index('time')[['prcp_acc']].resample('D').mean().reset_index()
    obs_prcp = snotel_22yr[name][['time', 'prcp_m']]

    prcp_df = pd.merge(sim_prcp_acc, obs_prcp, on='time')
    prcp_df['prcp_acc_m'] = prcp_df['prcp_m'].cumsum()


    xlim = [datetime(prcp_df.time[0].year, 1, 1), datetime(prcp_df.time.iloc[-1].year, 12, 31)]
    time_format = '%Y'
    month_interval = 12

    # point plots
    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_time_series(snow_df.time, [snow_df.swe_m, snow_df.swe],
                              ax=ax[0], fig=fig,
                              title='{} station SWE obs vs sim'.format(name),
                              ylabel='SWE(m)',
                              month_interval=month_interval,
                              time_format=time_format,
                              xlim=xlim,
                              line_label_list=['obs', 'sim'],
                              legend=True,
                              )

    plot_multiple_time_series(snow_df.time, [snow_df.swe-snow_df.swe_m],
                              ax=ax[1], fig=fig,
                              title='{} station SWE error'.format(name),
                              ylabel='SWE(m)',
                              line_label_list=['sim - obs'],
                              legend=True,
                              month_interval=month_interval,
                              time_format=time_format,
                              xlim=xlim,
                              save_as=os.path.join(results_dir, '{}_swe_obs_sim.png'.format(name))
                              )

    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_time_series(prcp_df.time, [prcp_df.prcp_acc_m, prcp_df.prcp_acc],
                              ax=ax[0], fig=fig,
                              title='{} station accumulative precipitation obs vs sim'.format(name),
                              ylabel='accumulative precipitation(m)',
                              month_interval=month_interval,
                              time_format=time_format,
                              xlim=xlim,
                              line_label_list=['obs', 'sim'],
                              legend=True,
                              )

    plot_multiple_time_series(prcp_df.time, [prcp_df.prcp_acc_m - prcp_df.prcp_acc],
                              ax=ax[1], fig=fig,
                              title='{} station accumulative precipitation error'.format(name),
                              ylabel='accumulative precipitation(m)',
                              line_label_list=['sim - obs'],
                              month_interval=month_interval,
                              time_format=time_format,
                              xlim=xlim,
                              legend=True,
                              save_as=os.path.join(results_dir, '{}_acc_prcp_obs_sim.png'.format(name))

                              )

print 'Analysis is Done'
