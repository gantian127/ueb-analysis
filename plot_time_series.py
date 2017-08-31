import netCDF4
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# plot time series (& cumulative) for a point
def plot_time_series(file_path, variable, time,
                     ax=None, fig=None,
                     x_index=0, y_index=0, shape=['time','y','x'],
                     cumulative=True, cumulative_scale=1,
                     title=None, ylabel=None, xlabel=None, y2label=None,
                     ts_color='b', acc_ts_color='r', month_interval=1,
                     figsize=(15, 5), save_as=None, **kwargs):
    # get root group
    group = netCDF4.Dataset(file_path, 'r')

    # get time data
    time = group.variables[time]
    time_data = time[:]
    time_size = time_data.size
    time_units = time.units if getattr(time,'units', None) else 'hours since 2000-01-01 00:00:00 UTC'
    time_calendar = time.calendar if getattr(time,'calendar', None) else 'standard'
    time_obj = [netCDF4.num2date(value, units=time_units, calendar=time_calendar) for value in
                time_data]

    # get variable data
    var = group.variables[variable]
    var_unit = var.units if getattr(var,'units', None) else ''
    slice_obj = []
    for dim in shape:
        if 'time' == dim:
            slice_obj.append(slice(0, time_size, 1))
        if 'x' == dim:
            slice_obj.append(slice(x_index, x_index+1, 1))
        if 'y' == dim:
            slice_obj.append(slice(y_index, y_index+1, 1))

    var_data = var[:][slice_obj].ravel()
    group.close()

    # make normal time series plot
    if ax is None or fig is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.plot(time_obj, var_data, color=ts_color)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=month_interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
    ax.set_xlabel(xlabel if xlabel else 'Time')
    ax.set_ylabel(ylabel if ylabel else '{} in {}'.format(variable, var_unit))
    ax.set_title(title if title else 'Time series of {}'.format(variable))

    # make cumulative plot
    if cumulative:
        ax1 = ax.twinx()
        var_data_acc = []
        for index in range(0, var_data.size):
            if index == 0:
                var_data_acc.append(0)
            else:
                var_data_acc.append(var_data[index-1]*cumulative_scale+var_data_acc[index-1])

        # var_data_acc = numpy.cumsum(var_data)
        ax1.plot(time_obj, var_data_acc, color=acc_ts_color)
        ax1.set_ylabel(y2label if ylabel else 'Cummulative of {}'.format(variable))

    # save image as file
    if save_as is not None:
        try:
            fig.savefig(save_as)
        except Exception as e:
            return 'Warning: failed to save the plot as a file.'

    return fig, var

# # plot for single point for NASA data
# import os
# os.chdir(r'C:\Users\jamy\Desktop\test')
#
# plot_time_series('prcp0.nc','ogrid','time',
#                        x_index=19, y_index=29, shape=['time','y','x'],
#                        cumulative_scale=3,
#                        ylabel='Precip(m/hr)', title='Time series of precipitation',
#                        y2label='Cumulative of precipitation (m)')
#
# plot_time_series('prcp0.nc','ogrid','time',
#                        x_index=19, y_index=29, shape=['time','y','x'],
#                        cumulative_scale=3,
#                        ylabel='Precip(m/hr)', title='Time series of precipitation',
#                        y2label='Cumulative of precipitation (m)')
#
# plot_time_series('SWE.nc','SWE','time',
#                           x_index=19, y_index=29, shape=['y','x','time'], cumulative=False)
#
# plot_time_series('SWIT.nc','SWIT','time',
#                           x_index=19, y_index=29, shape=['y','x','time'],
#                           cumulative_scale=6,
#                           ylabel='SWIT(m/hr)', y2label='Cumulative of SWIT (m)')
#
# plot_time_series('aggout.nc','SWIT', 'time',
#                           x_index=0, shape=['x','time'],
#                           cumulative_scale=6, title = 'aggout SWIT',
#                           ylabel='SWIT(m)', y2label='Cumulative of SWIT (m)')
#
# plot_time_series('aggout.nc','SWE', 'time',
#                           x_index=0, shape=['x','time'],
#                           cumulativ=False,
#                           title = 'aggout SWE',
#                           ylabel='SWE(m)', y2label='Cumulative of SWE (m)')