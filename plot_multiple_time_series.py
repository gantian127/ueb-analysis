import netCDF4
import numpy
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_cumulative(var_data, cumulative_scale):
    var_data_acc = []

    for index in range(0, var_data.size):
        if index == 0:
            var_data_acc.append(0)
        else:
            var_data_acc.append(var_data[index - 1] * cumulative_scale + var_data_acc[index - 1])

    return var_data_acc


def get_var_ave(file_path, var_name, axis_index=None):

    # get root group
    group = netCDF4.Dataset(file_path, 'r')

    # get variable data
    var = group.variables[var_name]
    if axis_index is not None:
        var_data_ave = var[:].mean(axis=axis_index)
    else:
        return 'Please provide the index for y or x axis in the array.'

    group.close()

    return var_data_ave


def get_var_point_data(file_path, var_name, x_index, y_index, slice_obj=None, xdim_name='x', ydim_name='y', var_dim_list=['time','y','x'], ravel=True):
    """
    y_data = get_var_point_data(file_path='SWIT.nc', var_name='SWIT', x_index=19, y_index=29)
    y2_data = get_var_point_data(file_path='SWE.nc', var_name='SWE', x_index=19, y_index=29)
    """
    # get root group
    group = netCDF4.Dataset(file_path, 'r')

    # get variable data
    var = group.variables[var_name]
    var_data = var[:]
    if ma.is_masked(var_data):
        var_data = var_data.data

    if slice_obj is None:
        slice_obj = []
        for dim in var_dim_list:
            if dim == xdim_name:
                slice_obj.append(slice(x_index, x_index + 1, 1))
            elif dim == ydim_name:
                slice_obj.append(slice(y_index, y_index + 1, 1))
            else:
                slice_obj.append(slice(0, None, 1))

    var_point_data = var_data[slice_obj]

    if ravel:
        var_point_data = var_point_data.ravel()

    group.close()

    return var_point_data


def get_time_value(file_path, time_var, slice_obj=None, units=None, calendar=None):
    """
    x_data = get_time_value(file_path='SWIT.nc', time_var='time', units=None, calendar=None)
    """

    # get root group
    group = netCDF4.Dataset(file_path, 'r')

    # get time data
    time = group.variables[time_var]
    if slice_obj is not None:
        time_data = time[:][slice_obj].ravel()
    else:
        time_data = time[:]

    time_value = []
    time_units = units if units else getattr(time, 'units', None)
    time_calendar = calendar if calendar else getattr(time, 'calendar', None)
    group.close()

    if time_units and time_calendar:
        time_value = [netCDF4.num2date(value, units=time_units, calendar=time_calendar) for value in
                    time_data]

    return time_value  # a list of datetime objects


def plot_multiple_time_series(x_data, y_data_list,
                              figsize=(15,5),
                              color_list=None,
                              linesytle_list=None,
                              month_interval=1,
                              title=None, xlabel=None, ylabel=None,
                              legend=False,
                              legend_loc=None,
                              line_label_list=None,
                              save_as=None):
    """
    plot_multiple_time_series(x_data, [y_data,y2_data], color_list=None, time_format=None, month_interval=1,title=None, xlabel=None, ylabel=None)
    """

    fig, ax = plt.subplots(figsize=figsize)
    cmap = plt.cm.get_cmap('viridis')
    color_map = cmap(numpy.linspace(0, 1, len(y_data_list)))

    for i in range(0, len(y_data_list)):
        plt.plot(x_data, y_data_list[i],
                color=color_list[i] if color_list else color_map[i],
                label=line_label_list[i] if line_label_list else 'line {}'.format(i+1),
                linestyle=linesytle_list[i] if linesytle_list else 'solid')

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=month_interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
    ax.set_xlabel(xlabel if xlabel else 'Time')
    ax.set_ylabel(ylabel if ylabel else 'Variable')
    plt.title(title if title else 'Time series plot')

    if legend:
        plt.legend(loc=legend_loc if legend_loc else 'best')

    if save_as is not None:
        try:
            fig.savefig(save_as)
        except Exception as e:
            return 'Warning: failed to save the plot as a file. Please check the file name.'

    return fig


# # test the work
# import os
# tag = 'App'
# year = '2009'
# watershed = 'Animas'
# workDir = r'C:\Users\jamy\Desktop\Plot_{}_{}_{}'.format(watershed, year, tag)
# os.chdir(workDir)
#
# x_data = get_time_value(file_path='SWIT.nc', time_var='time', units=None, calendar=None)
# y_data = get_var_point_data(file_path='SWIT.nc', var_name='SWIT', x_index=19, y_index=29)
# y2_data = get_var_point_data(file_path='SWE.nc', var_name='SWE', x_index=19, y_index=29)
# plot_multiple_time_series(x_data, [y_data,y2_data], color_list=None, month_interval=1, legend=True, title=None, xlabel=None, ylabel=None,save_as='File.png')