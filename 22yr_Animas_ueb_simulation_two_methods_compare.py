"""
This is to analyze the 22yr Animas UEB output
- Method 1: run 22yr model with multiple small time sections
- Method 2: run 22yr with single run

Results:
- There is no big difference between the two methods
- On average, single run tends to have a higher swe
- On average, single run tends to have a lower swit acc and swit


"""

import os
from plot_multiple_time_series import *
from datetime import datetime

source_dir = r'C:\Users\jamy\Desktop\22yr_Animas_UEB_sections_model_results\ueb_22yr_output_netcdf'
if source_dir:
    os.chdir(source_dir)

# prcp data ###################################
prcp_dir = r'C:\Users\jamy\Desktop\22yr_Animas_UEB_sections_model_results\ueb_model_run_22yr_work_1988_1994'
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


# get 22yr prcp data
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

# get multiple run  data ################################################
snow = {}
for year in [1988, 1993, 1998, 2001, 2004]:
    snow[year] = {}
    for var in ['SWE', 'SWIT']:
        file_path = '{}{}.nc'.format(var, year)
        print file_path
        time_value = get_time_value(file_path, 'time')
        var_ave = get_var_ave(file_path, var, axis_index=(0, 1))

        var_point_cascade = get_var_point_data(file_path, var, x_index=19, y_index=36, var_dim_list=['y', 'x', 'time'])
        var_point_molas = get_var_point_data(file_path, var, x_index=28, y_index=45, var_dim_list=['y', 'x', 'time'])
        snow[year][var] = {
                               'time': time_value,
                               'var_ave': var_ave,
                               'var_point_cascade': var_point_cascade,
                               'var_point_molas': var_point_molas
                            }
        if var == 'SWIT':
            var_acc = get_cumulative(var_ave, cumulative_scale=3)
            snow[year][var]['var_acc'] = var_acc

# subset snow data to remove overlap (remove the next year first year)
for last_year, next_year in [
    (1988, 1993),
    (1993, 1998),
    (1998, 2001),
    (2001, 2004)
]:
    for var in ['SWE', 'SWIT']:
        time_last_year = snow[last_year][var]['time']
        time_next_year = snow[next_year][var]['time']
        subset_index = time_next_year.index(time_last_year[-1])

        for element, data in snow[next_year][var].items():
            snow[next_year][var][element] = data[subset_index + 1:]

# 22yr snow data
snow_22yr = {
    'SWE': {
        'time': [],
        'var_ave': [],
        'var_point_cascade': [],
        'var_point_molas': [],
    },

    'SWIT': {
        'time': [],
        'var_ave': [],
        'var_point_cascade': [],
        'var_point_molas': [],
        'var_acc_year': [],
        'var_acc': []
    }
}

for year in [1988, 1993, 1998, 2001, 2004]:
    for var in ['SWE', 'SWIT']:
        snow_22yr[var]['time'].extend(snow[year][var]['time'])
        snow_22yr[var]['var_ave'].extend(snow[year][var]['var_ave'])
        snow_22yr[var]['var_point_cascade'].extend(snow[year][var]['var_point_cascade'])
        snow_22yr[var]['var_point_molas'].extend(snow[year][var]['var_point_molas'])
        if var == 'SWIT':
            snow_22yr[var]['var_acc_year'].extend(snow[year][var]['var_acc'])

snow_22yr['SWIT']['var_acc'] = get_cumulative(snow_22yr['SWIT']['var_ave'], cumulative_scale=3)





# 22yr multiple files
plot_multiple_time_series(prcp_22yr['time'], [prcp_22yr['var_ave']],
                          month_interval=12,
                          time_format='%Y',
                          title='Animas watershed precipitation (domain average)',
                          ylabel='Precipitation (m/hr)',
                          xlim=[datetime(1988, 1, 1),
                                datetime(2010, 12, 31)],
                          save_as='22yr_ueb_Animas_prcp.png'
                          )

plot_multiple_time_series(snow_22yr['SWIT']['time'], [snow_22yr['SWIT']['var_ave']],
                          month_interval=12,
                          time_format='%Y',
                          title='Animas watershed rain plus melt (domain average) - multiple',
                          ylabel='Rain plus melt (m/hr)',
                          xlim=[datetime(1988, 1, 1),
                                datetime(2010, 12, 31)],
                          save_as='22yr_ueb_Animas_swit.png')

plot_multiple_time_series(snow_22yr['SWE']['time'], [snow_22yr['SWE']['var_ave']],
                          title='Animas watershed 22yr SWE (domain average) - multiple',
                          ylabel='SWE(m)',
                          month_interval=12,
                          time_format='%Y',
                          xlim=[datetime(1988, 1, 1),
                                datetime(2010, 12, 31)],
                          save_as='22yr_ueb_Animas_swe.png'
                          )

plot_multiple_time_series(snow_22yr['SWIT']['time'],
                          [prcp_22yr['var_acc'][:len(snow_22yr['SWIT']['var_acc'])],
                           snow_22yr['SWIT']['var_acc'],
                           snow_22yr['SWE']['var_ave']
                           ],
                           title='Animas watershed 22yr simulation (domain average) - multiple',
                           line_label_list=['cumulative precipitation',
                                           'cumulative rain plus melt',
                                           'snow water equivalent'
                                            ],
                           legend=True,
                           month_interval=12,
                           time_format="%Y",
                           xlim=[datetime(1988, 1, 1),
                                 datetime(2010, 12, 31)],
                           ylabel='cumulative depth(m)',
                           save_as='22yr_ueb_Animas_mass_balance.png'
                          )


# 22yr one file ################################################
# get swit, swe (failed of memory error > 600mb)
# time_data = get_time_value(file_path='SWIT22yr.nc', time_var='time', units=None, calendar=None)
# swit_data_ave = get_var_ave(file_path='SWIT22yr.nc', var_name='SWIT', axis_index=(0, 1))
# swit_data_acc = get_cumulative(swit_data_ave, cumulative_scale=3)
# swe_data_ave = get_var_ave(file_path='SWE22yr.nc', var_name='SWE', axis_index=(0,1))

# get aggout file
time_data = get_time_value(file_path='aggout22yr.nc', time_var='time')
swit_data_aggout = get_aggout_var_data(file_path='aggout22yr.nc', var_name='SWIT')
swe_data_aggout = get_aggout_var_data(file_path='aggout22yr.nc', var_name ='SWE')
swit_data_aggout_acc = get_cumulative(swit_data_aggout, cumulative_scale=3)


# 22yr single run plots
plot_multiple_time_series(time_data, [swe_data_aggout],
                          title='Animas watershed 22yr SWE (domain average)',
                          ylabel='SWE(m)',
                          month_interval=12,
                          time_format='%Y',
                          xlim=[datetime(1988, 1, 1),
                                datetime(2010, 12, 31)],
                          save_as='22yr_ueb_Animas_swe_single_run.png'
                          )

plot_multiple_time_series(time_data, [swit_data_aggout],
                          month_interval=12,
                          time_format='%Y',
                          title='Animas watershed rain plus melt (domain average)',
                          ylabel='Rain plus melt (m/hr)',
                          xlim=[datetime(1988, 1, 1),
                                datetime(2010, 12, 31)],
                          save_as='22yr_ueb_Animas_swit_single_run.png')

plot_multiple_time_series(time_data,
                          [prcp_22yr['var_acc'][:len(time_data)],
                           swit_data_aggout_acc,
                           swe_data_aggout
                           ],
                           title='Animas watershed 22yr simulation (domain average)',
                           line_label_list=['cumulative precipitation',
                                           'cumulative rain plus melt',
                                           'snow water equivalent'
                                            ],
                           legend=True,
                           month_interval=12,
                           time_format="%Y",
                           xlim=[datetime(1988, 1, 1),
                                 datetime(2010, 12, 31)],
                           ylabel='cumulative depth(m)',
                           save_as='22yr_ueb_Animas_mass_balance_single_run.png'
                          )


# 2 method comparison ###########################################################
diff_swe = [x-y for x, y in zip(swe_data_aggout, snow_22yr['SWE']['var_ave'])]
diff_swit = [x-y for x,y in zip(swit_data_aggout, snow_22yr['SWIT']['var_ave'])]
diff_swit_acc = [x-y for x, y in zip(swit_data_aggout_acc, snow_22yr['SWIT']['var_acc'])]

# swe
fig, ax = plt.subplots(2,1,figsize=(15,10))
plot_multiple_time_series(time_data,
                          [swe_data_aggout,
                           snow_22yr['SWE']['var_ave'],
                           ],
                           ax=ax[0],
                           fig=fig,
                           title='Animas watershed 22yr swe difference (domain average)',
                           line_label_list=['single run',
                                            'multiple run',
                                            ],
                           legend=True,
                           month_interval=12,
                           time_format="%Y",
                           xlim=[datetime(1988, 1, 1),
                                 datetime(2010, 12, 31)],
                           ylabel='swe(m)',
                           save_as='22yr_ueb_Animas_swe_diff.png'
                          )

plot_multiple_time_series(time_data,
                          [
                           diff_swe
                           ],
                           ax=ax[1],
                           fig=fig,
                           title='Animas watershed 22yr swe difference (domain average)',
                           line_label_list=['diff(single - multiple)'],
                           legend=True,
                           month_interval=12,
                           time_format="%Y",
                           xlim=[datetime(1988, 1, 1),
                                 datetime(2010, 12, 31)],
                           ylabel='swe(m)',
                           save_as='22yr_ueb_Animas_swe_diff.png'
                          )

#swit
fig, ax = plt.subplots(2,1,figsize=(15,10))
plot_multiple_time_series(time_data,
                          [swit_data_aggout,
                           snow_22yr['SWIT']['var_ave'],
                           ],
                           ax=ax[0],
                           fig=fig,
                           title='Animas watershed 22yr rain plus melt difference (domain average)',
                           line_label_list=['single run',
                                            'multiple run',
                                            ],
                           legend=True,
                           month_interval=12,
                           time_format="%Y",
                           xlim=[datetime(1988, 1, 1),
                                 datetime(2010, 12, 31)],
                           ylabel='swit(m/hr)',
                           save_as='22yr_ueb_Animas_swit_diff.png'
                          )

plot_multiple_time_series(time_data,
                          [
                           diff_swit
                           ],
                           ax=ax[1],
                           fig=fig,
                           title='Animas watershed 22yr swit difference (domain average)',
                           line_label_list=['diff(single - multiple)'],
                           legend=True,
                           month_interval=12,
                           time_format="%Y",
                           xlim=[datetime(1988, 1, 1),
                                 datetime(2010, 12, 31)],
                           ylabel='swit(m/hr)',
                           save_as='22yr_ueb_Animas_swit_diff.png'
                          )

# swit acc
fig, ax = plt.subplots(2,1,figsize=(15,10))
plot_multiple_time_series(time_data,
                          [swit_data_aggout_acc,
                           snow_22yr['SWIT']['var_acc'],
                           ],
                           ax=ax[0],
                           fig=fig,
                           title='Animas watershed 22yr cummulative rain plus melt difference (domain average)',
                           line_label_list=['single run',
                                            'multiple run',
                                            ],
                           legend=True,
                           month_interval=12,
                           time_format="%Y",
                           xlim=[datetime(1988, 1, 1),
                                 datetime(2010, 12, 31)],
                           ylabel='cumulative depth(m/hr)',
                           save_as='22yr_ueb_Animas_swit_acc_diff.png'
                          )

plot_multiple_time_series(time_data,
                          [
                           diff_swit_acc
                           ],
                           ax=ax[1],
                           fig=fig,
                           title='Animas watershed 22yr swit difference (domain average)',
                           line_label_list=['diff(single - multiple)'],
                           legend=True,
                           month_interval=12,
                           time_format="%Y",
                           xlim=[datetime(1988, 1, 1),
                                 datetime(2010, 12, 31)],
                           ylabel='cumulative depth(m)',
                           save_as='22yr_ueb_Animas_swit_acc_diff.png'
                          )