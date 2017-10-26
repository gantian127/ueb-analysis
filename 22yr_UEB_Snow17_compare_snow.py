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

results_dir = os.path.join(os.getcwd(), '{}_snow_analysis'.format(watershed))
if not os.path.isdir(results_dir):
    os.mkdir(results_dir)

start_time = '' #'1988-10-01'
end_time = '' #'1989-9-30'


# Process Data ##################################################
# get prcp data
prcp = {}
for i in range(0, 22):
    file_path = os.path.join(prcp_dir, 'prcp{}.nc'.format(i))
    year = 1988+i
    print file_path
    time_value = get_time_value(file_path, 'time')
    var_ave = get_var_ave(file_path, var_name='ogrid', axis_index=(2, 1))
    var_acc = get_cumulative(var_ave, cumulative_scale=3)
    var_point_cascade = get_var_point_data(file_path=file_path, var_name='ogrid', x_index=19, y_index=36,
                                           var_dim_list=['time','y','x'])
    var_point_molas = get_var_point_data(file_path=file_path, var_name='ogrid', x_index=28, y_index=45,
                                           var_dim_list=['time', 'y', 'x'])
    prcp[year] = {
        'time': time_value,
        'var_ave': var_ave,
        'var_acc': var_acc,
        'var_point_cascade': var_point_cascade,
        'var_point_molas': var_point_molas
    }


prcp_22yr = {
        'time': [],
        'var_ave': [],
        'var_acc_year': [],
        'var_acc': [],
        'var_point_cascade': [],
        'var_point_molas': [],
}

for year in range(1988, 2010):
    prcp_22yr['time'].extend(prcp[year]['time'])
    prcp_22yr['var_ave'].extend(prcp[year]['var_ave'])
    prcp_22yr['var_acc_year'].extend(prcp[year]['var_acc'])
    prcp_22yr['var_point_cascade'].extend(prcp[year]['var_point_cascade'])
    prcp_22yr['var_point_molas'].extend(prcp[year]['var_point_molas'])

prcp_22yr['var_acc'] = get_cumulative(prcp_22yr['var_ave'], cumulative_scale=3)


# get 22yr aggout snow data
ori_dir = os.getcwd()
os.chdir(snow_dir)
time_data = get_time_value(file_path='aggout22yr.nc', time_var='time')
swit_data_aggout = get_aggout_var_data(file_path='aggout22yr.nc', var_name='SWIT')
swe_data_aggout = get_aggout_var_data(file_path='aggout22yr.nc', var_name ='SWE')
swit_data_aggout_acc = get_cumulative(swit_data_aggout, cumulative_scale=3)


# get 22yr snow station data
# time_data = get_time_value(file_path='SWIT22yr.nc', time_var='time', units=None, calendar=None)
# swit_data_ave = get_var_ave(file_path='SWIT22yr.nc', var_name='SWIT', axis_index=(0, 1))
# swit_data_acc = get_cumulative(swit_data_ave, cumulative_scale=3)
# swe_data_ave = get_var_ave(file_path='SWE22yr.nc', var_name='SWE', axis_index=(0,1))
# os.chdir(ori_dir)

# Write data to file #################################################
prcp = pd.DataFrame(data=prcp_22yr)
prcp.to_csv(os.path.join(results_dir, 'prcp_domain_average.csv'))

snow = pd.DataFrame(data={
                        'time': [x - timedelta(hours=7) for x in time_data],
                        'swit': swit_data_aggout,
                        'swit_acc': swit_data_aggout_acc,
                        'swe': swe_data_aggout,
                        },
                   columns=['time', 'swit', 'swit_acc', 'swe'],
)

snow.to_csv(os.path.join(results_dir, 'snow_domain_average.csv'))

DF = pd.merge(snow, prcp, on='time')
if start_time and end_time:
    DF = DF.ix[(DF.time >= start_time) & (DF.time <= end_time)]
DF.to_csv(os.path.join(results_dir, 'all_data.csv'))


# Make plots ########################################################
xlim = [datetime(DF.time[0].year, 1, 1), datetime(DF.time.iloc[-1].year, 12, 31)]
time_format = '%Y/%m'
month_interval = 1


# Domain average
plot_multiple_time_series(DF.time, [DF.swe],
                          title='{} watershed SWE (domain average)'.format(watershed),
                          ylabel='SWE(m)',
                          month_interval=month_interval,
                          time_format=time_format,
                          xlim=xlim,
                          save_as=os.path.join(results_dir, '{}_swe_domain_average.png'.format(watershed))
                          )

plot_multiple_time_series(DF.time, [DF.swit],
                          month_interval=month_interval,
                          time_format=time_format,
                          title='{} watershed rain plus melt (domain average)'.format(watershed),
                          ylabel='Rain plus melt (m/hr)',
                          xlim=xlim,
                          save_as=os.path.join(results_dir, '{}_swit_domain_average.png'.format(watershed))
                          )

plot_multiple_time_series(DF.time,
                          [DF.var_acc,
                           DF.swit_acc,
                           DF.swe
                           ],
                           title='Animas watershed 22yr simulation (domain average)',
                           line_label_list=['cumulative precipitation',
                                           'cumulative rain plus melt',
                                           'snow water equivalent'
                                            ],
                           legend=True,
                           month_interval=month_interval,
                           time_format=time_format,
                           xlim=xlim,
                           ylabel='cumulative depth(m)',
                           save_as=os.path.join(results_dir, '{}_mass_balance_domain_average.png'.format(watershed))
                          )

print 'Analysis is done !'