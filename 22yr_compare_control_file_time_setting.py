"""
This is used to compare the start and end time setting for UEB model 1988-1994
One is start 2010 10 01 7
One is start 2010 9 30 18

Results:
The Sept 30 one has an average of higher swe and lower swit (~0.01m/yr)

"""

import os
from plot_multiple_time_series import *


source_dir = r'C:\Users\jamy\Desktop\22yr_Animas_UEB_sections_model_results\ueb_model_run_1988_1994_new_start_date'
if source_dir:
    os.chdir(source_dir)

for var in [
            'SWE',
            'SWIT'
            ]:
    new_file = '{}.nc'.format(var)
    old_file = '{}_oct.nc'.format(var)

    # old data
    time_data_old = get_time_value(old_file, 'time')
    var_point_old = get_var_point_data(file_path=old_file, var_name=var, x_index=19, y_index=36,
                                             var_dim_list=['y', 'x', 'time'])

    # new data
    time_data_new = get_time_value(new_file, 'time')
    var_point_new = get_var_point_data(file_path=new_file, var_name=var, x_index=19, y_index=36,
                                             var_dim_list=['y', 'x', 'time'])

    # difference and plot
    if len(time_data_old) == len(time_data_new):
        diff = [x - y for x, y in zip(var_point_old, var_point_new)]
        plot_multiple_time_series(time_data_new, [var_point_old,
                                                  var_point_new,
                                                  diff
                                                      ],
                                  line_label_list=['Oct 1st', 'Sept 30', 'Oct 1st - Sept 30 (sum={})'.format(sum(diff))],
                                  legend=True,
                                  month_interval=12,
                                  title='Plot of {} comparison for different time setting'. format(var),
                                  save_as='Plot_of_{}comparison_for_time_setting.png'. format(var)
                                  )