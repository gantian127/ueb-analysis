"""
This is to analyze the 22yr UEB output for UEB+SAC workflow

Results:


"""

import os
from plot_multiple_time_series import *
from datetime import datetime, timedelta
import pandas as pd


watershed = 'Animas'
prcp_dir = r'D:\3_NASA_Project\Model output and plots\22yr_Animas_watershed\22yr_Animas_UEB_sections_model_results\ueb_model_run_22yr_work_1988_1994'
snow_dir = r'D:\3_NASA_Project\Model output and plots\22yr_Animas_watershed\22yr_Animas_UEB_sections_model_results\ueb_22yr_output_netcdf'


results_dir = os.path.join(os.getcwd(), '{}_snow_analysis_point'.format(watershed))
if not os.path.isdir(results_dir):
    os.mkdir(results_dir)

start_time = '' #'1988-10-01'
end_time = '' #'1989-9-30'
time_step = 3

point_info = {
    'cascade': [19, 36],  # xindex, yindex
    'molaslake': [28, 45]
}

# Get simulation Data ##################################################
# get prcp data
prcp_22yr = {}
for name, index in point_info.items():
    prcp = []
    time = []
    for i in range(0, 22):
        file_path = os.path.join(prcp_dir, 'prcp{}.nc'.format(i))
        print file_path

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

# Get observation Data ##################################################
#TODO

# Make plots ########################################################
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