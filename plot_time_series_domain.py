import netCDF4
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# plot time series (& cumulative) for a point
def plot_time_series_domain_average(file_path, variable, time,
                                    ax=None, fig=None,
                                    xaxis_index=None, yaxis_index=None,
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
    time_calendar = time.calendar if getattr(time,'calendar',None) else 'standard'
    time_obj = [netCDF4.num2date(value, units=time_units, calendar=time_calendar) for value in
                time_data]

    # get variable data
    var = group.variables[variable]
    var_unit = var.units if getattr(var, 'units', None) else ''
    var_data = var[:]
    if xaxis_index is not None and yaxis_index is not None:
        var_data_mean = var_data.mean(axis=(xaxis_index, yaxis_index))
    else:
        return 'Please provide the index for y or x axis in the array.'

    group.close()

    # make normal time series plot
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.plot(time_obj, var_data_mean, color=ts_color)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=month_interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
    ax.set_xlabel(xlabel if xlabel else 'Time')
    ax.set_ylabel(ylabel if ylabel else '{} in {}'.format(variable, var_unit))
    ax.set_title(title if title else 'Time series of {}'.format(variable))

    # make cumulative plot
    if cumulative:
        ax1 = ax.twinx()
        var_data_acc = []
        for index in range(0, var_data_mean.size):
            if index == 0:
                var_data_acc.append(0)
            else:
                var_data_acc.append(var_data_mean[index-1]*cumulative_scale+var_data_acc[index-1])

        # var_data_acc = numpy.cumsum(var_data)
        ax1.plot(time_obj, var_data_acc, color=acc_ts_color)
        ax1.set_ylabel(y2label if ylabel else 'Cummulative of {}'.format(variable))

    # save image as file
    if save_as is not None:
        try:
            fig.savefig(save_as)
        except Exception as e:
            return 'Warning: failed to save the plot as a file. Please check the file name.'

    # return fig, var_data_acc

# # plot for single point for NASA data
# import os
# os.chdir(r'C:\Users\jamy\Desktop\test')
#
# # plot domain average
# a, b = plot_time_series_domain_average('prcp0.nc', 'ogrid', time='time', xaxis_index=2, yaxis_index=1,
#                         cumulative=True, cumulative_scale=3, title='Domain average of Precipitation',
#                         ylabel='Precipitation (m/hr)', y2label='Cumulative of domain average Precipitation (m)')
#
# a1, b1 = plot_time_series_domain_average('SWE.nc', 'SWE', time='time', xaxis_index=1, yaxis_index=0,
#                      cumulative=False, title='Domain average of SWE')
#
# a2, b2 = plot_time_series_domain_average('SWIT.nc', 'SWIT', time='time', xaxis_index=1, yaxis_index=0,
#                         cumulative=True, cumulative_scale=6, title='Domain average of SWIT',
#                         ylabel='SWIT (m/hr)', y2label='Cumulative of domain average SWIT (m)')