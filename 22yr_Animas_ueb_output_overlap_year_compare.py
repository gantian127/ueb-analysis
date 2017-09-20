"""
This is used to compare the overlap year results for difference sections of the 22yr Animas watershed.

Results:
The graph shows that there is minor difference for the overlap year
The minor difference only happens at the beginning of the year.
This is caused by the initial site condition difference.

Conclusion:
It is suggested to use the last year data for the overlap year.
e.g. 1988-1994, 1993-1998, This will remove the 1993-1994 data in the 1993-1998 results.

Note:
To run the code, this only support one loop comparison because of the memory leak problem
"""


import os
from datetime import datetime
from plot_multiple_time_series import *


source_dir = r'C:\Users\jamy\Desktop\ueb_22yr_output_netcdf'
if source_dir:
    os.chdir(source_dir)


for last_year, next_year in [
                             # (1988, 1993),
                             # (1993, 1998),
                             # (1998, 2001),
                             (2001, 2004)
                             ]:
    print last_year, next_year
    compare_time = datetime(next_year, 10, 1, 7)
    for var in ['SWE', 'SWIT']:
        last_year_file = '{}{}.nc'.format(var, last_year)
        next_year_file = '{}{}.nc'.format(var, next_year)

        # last year
        time_last_year = get_time_value(last_year_file, 'time')
        start = get_time_index(last_year_file, 'time', compare_time)
        var_point_last_year = get_var_point_data(file_path=last_year_file, var_name=var, x_index=19, y_index=36,
                                                 var_dim_list=['y', 'x', 'time'])
        var_last_year = var_point_last_year[start:]
        time_value_last_year = time_last_year[start:]

        # next year
        time_next_year = get_time_value(next_year_file, 'time')
        end = get_time_index(next_year_file, 'time', time_value_last_year[-1])
        var_point_next_year = get_var_point_data(file_path=next_year_file, var_name=var, x_index=19, y_index=36,
                                                 var_dim_list=['y', 'x', 'time'])
        var_next_year = var_point_next_year[:end + 1]
        time_value_next_year = time_next_year[:end + 1]

        # difference and plot
        if len(time_value_next_year) == len(time_value_last_year):
            diff = [x - y for x, y in zip(var_last_year, var_next_year)]

            plot_multiple_time_series(time_value_next_year, [var_last_year,
                                                             var_next_year,
                                                             diff
                                                          ],
                                      line_label_list=['last', 'next', 'diff'],
                                      legend=True,
                                      title='Plot of {} from {} to {}'. format(var,
                                                                                 time_value_next_year[0],
                                                                                 time_value_next_year[-1]),
                                      save_as='Plot_of_{}_{}_{}.png'. format(var,
                                                                                 last_year,
                                                                                 next_year),)
        else:
            print 'failed for {} {}'.format(time_value_next_year[0], time_value_next_year[-1])