"""
This is used to compare the overlap year results for difference sections of the 22yr Animas watershed.

Results:
Point compare:
The graph shows that there is minor difference for the overlap year
The minor difference only happens at the beginning of the year.
This is caused by the initial site condition difference.

Domain average:
There is a bigger difference for swit and swe when compare the last year and next year difference
There is minor difference for swit and swe when compare the last year with the 22yr single run results
There is a bigger difference for swit and swe when compare the next year and 22yr single run results.


Conclusion:
It is suggested to use the last year data for the overlap year.
e.g. 1988-1994, 1993-1998, This will remove the 1993-1994 data in the 1993-1998 results.


"""


import os
from datetime import datetime
from plot_multiple_time_series import *


source_dir = r'C:\Users\jamy\Desktop\22yr_Animas_UEB_sections_model_results\ueb_22yr_output_netcdf'
if source_dir:
    os.chdir(source_dir)


for last_year, next_year in [
                             (1988, 1993),
                             (1993, 1998),
                             (1998, 2001),
                             (2001, 2004)
                             ]:
    print last_year, next_year
    compare_time = datetime(next_year, 10, 1, 7)
    for var in ['SWE', 'SWIT']:
        last_year_file = '{}{}.nc'.format(var, last_year)
        next_year_file = '{}{}.nc'.format(var, next_year)
        last_year_agg = 'aggout{}.nc'.format(last_year)
        next_year_agg = 'aggout{}.nc'.format(next_year)

        # last year
        time_last_year = get_time_value(last_year_file, 'time')
        start = get_time_index(last_year_file, 'time', compare_time)
        print start
        var_point_last_year = get_var_point_data(file_path=last_year_file, var_name=var, x_index=19, y_index=36,
                                                 var_dim_list=['y', 'x', 'time'])
        var_last_year = var_point_last_year[start:]
        time_value_last_year = time_last_year[start:]


        start_agg = get_time_index(last_year_agg, 'time', compare_time)
        time_aggout_last_year_data = get_time_value(last_year_agg, 'time')[start:]
        aggout_var_last_year_data = get_aggout_var_data(last_year_agg, var)[start:]

        # next year
        time_next_year = get_time_value(next_year_file, 'time')
        end = get_time_index(next_year_file, 'time', time_value_last_year[-1])
        var_point_next_year = get_var_point_data(file_path=next_year_file, var_name=var, x_index=19, y_index=36,
                                                 var_dim_list=['y', 'x', 'time'])
        var_next_year = var_point_next_year[:end + 1]
        time_value_next_year = time_next_year[:end + 1]

        end_agg = get_time_index(next_year_agg, 'time', time_aggout_last_year_data[-1])
        time_aggout_next_year_data = get_time_value(next_year_agg, 'time')[:end + 1]
        aggout_var_next_year_data = get_aggout_var_data(next_year_agg, var)[:end + 1]

        # 22yr single file
        start_22yr = get_time_index('aggout22yr.nc', 'time', time_aggout_next_year_data[0])
        end_22yr = get_time_index('aggout22yr.nc', 'time', time_aggout_next_year_data[-1])
        aggout_22yr_data_subset = get_aggout_var_data('aggout22yr.nc', var)[start_22yr:end_22yr+1]
        time_aggout_22yr_data_subset = get_time_value('aggout22yr.nc', 'time')[start_22yr:end_22yr+1]

        # last - next (cascade station)
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

        # last - next (domain average)
        if len(time_aggout_last_year_data) == len(time_aggout_next_year_data):
            diff_agg = [x - y for x, y in zip(aggout_var_last_year_data, aggout_var_next_year_data)]

            fig, ax = plt.subplots(2,1,figsize=(15,10))
            plot_multiple_time_series(time_aggout_last_year_data, [aggout_var_last_year_data,
                                                             aggout_var_next_year_data,
                                                          ],
                                      ax=ax[0],
                                      fig=fig,
                                      line_label_list=['last', 'next'],
                                      legend=True,
                                      title='Plot of domain average {} from {} to {}'. format(var,
                                                                                       time_aggout_last_year_data[0],
                                                                                       time_aggout_last_year_data[-1]),
                                      # save_as='Plot_of_domain_average_{}_{}_{}.png'. format(var,
                                      #                                            last_year,
                                      #                                            next_year),
                                      )
            plot_multiple_time_series(time_aggout_last_year_data, [diff_agg],
                                      line_label_list=['diff(last-next)'],
                                      ax=ax[1],
                                      fig=fig,
                                      legend=True,
                                      title='Plot of domain average diff for {} from {} to {}'. format(var,
                                                                                       time_aggout_last_year_data[0],
                                                                                       time_aggout_last_year_data[-1]),
                                      save_as='Plot_of_domain_average_{}_{}_{}.png'. format(var,
                                                                                 last_year,
                                                                                 next_year),)

        # last - aggout 22yr (domain average)
        if len(time_aggout_last_year_data) == len(time_aggout_22yr_data_subset):
            diff_agg2 = [x-y for x, y in zip(aggout_var_last_year_data, aggout_22yr_data_subset)]
            fig, ax = plt.subplots(2, 1, figsize=(15, 10))

            plot_multiple_time_series(time_aggout_last_year_data, [aggout_var_last_year_data,
                                                                   aggout_22yr_data_subset,
                                                          ],
                                      fig=fig,
                                      ax=ax[0],
                                      line_label_list=['last', '22yr_subset'],
                                      legend=True,
                                      title='Plot of domain average {} from {} to {}'. format(var,
                                                                                       time_aggout_last_year_data[0],
                                                                                       time_aggout_last_year_data[-1]),
                                      # save_as='Plot_of_domain_average_{}_{}_{}.png'. format(var,
                                      #                                            last_year,
                                      #                                            next_year),
                                      )
            plot_multiple_time_series(time_aggout_last_year_data, [diff_agg2],
                                      fig=fig,
                                      ax=ax[1],
                                      line_label_list=['diff(last-22yr)'],
                                      legend=True,
                                      title='Plot of domain average diff for {} from {} to {}'. format(var,
                                                                                       time_aggout_last_year_data[0],
                                                                                       time_aggout_last_year_data[-1]),
                                      save_as='Plot_of_domain_average_diff_last_22yr_{}_{}_{}.png'. format(var,
                                                                                 last_year,
                                                                                 next_year),)


        # next - aggout 22yr (domain average)
        if len(time_aggout_last_year_data) == len(time_aggout_22yr_data_subset):
            diff_agg3 = [x - y for x, y in zip(aggout_var_next_year_data, aggout_22yr_data_subset)]
            fig, ax = plt.subplots(2, 1, figsize=(15, 10))

            plot_multiple_time_series(time_aggout_next_year_data, [aggout_var_next_year_data,
                                                                   aggout_22yr_data_subset,
                                                                   ],
                                      fig=fig,
                                      ax=ax[0],
                                      line_label_list=['next', '22yr_subset'],
                                      legend=True,
                                      title='Plot of domain average {} from {} to {}'.format(var,
                                                                                             time_aggout_last_year_data[
                                                                                                 0],
                                                                                             time_aggout_last_year_data[
                                                                                                 -1]),
                                      # save_as='Plot_of_domain_average_{}_{}_{}.png'. format(var,
                                      #                                            last_year,
                                      #                                            next_year),
                                      )
            plot_multiple_time_series(time_aggout_next_year_data, [diff_agg3],
                                      fig=fig,
                                      ax=ax[1],
                                      line_label_list=['diff(next-22yr)'],
                                      legend=True,
                                      title='Plot of domain average diff for {} from {} to {}'.format(var,
                                                                                                      time_aggout_last_year_data[0],
                                                                                                      time_aggout_last_year_data[-1]),
                                      save_as='Plot_of_domain_average_diff_next_22yr_{}_{}_{}.png'.format(var,
                                                                                                          last_year,
                                                                                                          next_year), )

        else:
            print 'failed for {} {}'.format(time_aggout_last_year_data[0], time_aggout_last_year_data[-1])