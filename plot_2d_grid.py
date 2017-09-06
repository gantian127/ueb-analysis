"""
This is used to make 2D grid plot for netCDF variables
https://brushingupscience.wordpress.com/2016/06/21/matplotlib-animations-the-easy-way/
"""

import netCDF4
import numpy
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from plot_multiple_time_series import get_time_value


def plot_2d_grid(x_name, y_name, var_name, file_path,
                 time_index=0, var_shape=['time', 'x', 'y'],
                 ax=None, fig=None,
                 slice_obj=None,
                 time_name=None,
                 title=None,
                 xlabel=None,
                 ylabel=None,
                 cmap='viridis',
                 figsize=(10, 10),
                 save_as=None,
                 ):
    """
    this needs to be 3D plot include time, x, y
    plot_2d_grid(x_name='x',
                 y_name='y',
                 var_name='ogrid',
                 time_name='time',
                 file_path='prcp0.nc',
                 var_shape=['time','x','y'],
                 time_index=1000,
                 color=None,
                 slice_obj=None,
                 title=None,
                 xlabel=None,
                 ylabel=None,
                 figsize=None,
                 save_as=None)

    """

    # get root group
    group = netCDF4.Dataset(file_path, 'r')

    # get variables
    x = group.variables[x_name][:]
    y = group.variables[y_name][:]
    var = group.variables[var_name][:]
    if time_name:
        time = group.variables[time_name][:]
    group.close()

    # get plot data
    xx, yy = numpy.meshgrid(x, y)

    if slice_obj:
        var_mesh = var[slice_obj]
    elif time_index is not None and var_shape is not None:
        slice_obj = []
        for dim in var_shape:
            if dim == 'time':
                slice_obj.append(slice(time_index, time_index+1, 1))
            elif dim == 'x' or dim == 'y':
                slice_obj.append(slice(0, None, 1))

        var_mesh = numpy.squeeze(var[slice_obj])
    else:
        return 'please provide valid variable information'

    # make 2D mesh plot
    if ax is None or fig is None:
        fig, ax = plt.subplots(figsize=figsize)

    ax.set_aspect('equal', adjustable='box')
    plot = ax.pcolormesh(xx, yy, var_mesh, cmap=cmap, vmin=var_mesh.min(), vmax=var_mesh.max())
    fig.colorbar(plot)

    time_step = None
    if time_name is not None:
        time_step = get_time_value(file_path, time_name)[time_index]

    ax.set_title(title if title else '2D plot of {} '.format(var_name))
    if time_step is not None:
        plt.figtext(0.99, 0.01, 'Time at {}'.format(time_step), horizontalalignment='right')
    ax.set_xlabel(xlabel if xlabel else 'X coordinate')
    ax.set_ylabel(ylabel if ylabel else 'Y coordinate')
    plt.tight_layout()

    # save image as file
    if save_as is not None:
        try:
            fig.savefig(save_as)
        except Exception as e:
            return 'Warning: failed to save the plot as a file.'


def plot_2d_animation(file_path, x_name, y_name,
                      var_name, var_shape=['time', 'y', 'x'],
                      time_name=None, time_start_index=0, time_end_index=1,
                      interval=3,
                      title=None, xlabel=None, ylabel=None,
                      cmap='viridis',
                      figsize=None,
                      repeat=False,
                      ):
    """
    plot_2d_animation(file_path='prcp0.nc', x_name='x', y_name='y',
                      var_name='ogrid', var_shape=['time', 'y', 'x'],
                      time_name='time', time_start_index=1000, time_end_index=1010,
                      interval=300,
                      title='animation', xlabel='x', ylabel='y',
                      cmap='viridis',
                      repeat=False,
                      )

    plot_2d_animation(file_path='SWE.nc', x_name='x', y_name='y',
                  var_name='SWE', var_shape=['y', 'x', 'time'],
                  time_name='time', time_start_index=1060, time_end_index=1100,
                  interval=300,
                  title='animation', xlabel='x', ylabel='y',
                  cmap='viridis',
                  repeat=True,
                  )
    """
    # get root group
    group = netCDF4.Dataset(file_path, 'r')

    # get variables
    time = None
    x = group.variables[x_name][:]
    y = group.variables[y_name][:]
    var = group.variables[var_name][:]

    if var_shape != ['time', 'y', 'x']:  # transpose var with data
        transpose_index = [var_shape.index(dim) for dim in ['time', 'y', 'x']]
        var = var.transpose(transpose_index)

    var = var[time_start_index:time_end_index, :, :]

    if time_name is not None:
        time = get_time_value(file_path, time_name)[time_start_index:time_end_index]

    group.close()

    # initiate 1st plot
    xx, yy = numpy.meshgrid(x, y)
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_aspect('equal', adjustable='box')
    plot = ax.pcolormesh(xx, yy, var[0, :, :], cmap=cmap, vmin=var.min(), vmax=var.max())
    ax.set_title(title if title else 'Animation of {}'.format(var_name))
    ax.set_xlabel(xlabel if xlabel else 'X coordinate')
    ax.set_ylabel(ylabel if ylabel else 'Y coordinate')
    fig.colorbar(plot)
    if time is not None:
        plt.figtext(0.99, 0.01, 'Time at {}'.format(time[0]), horizontalalignment='right')
    plt.tight_layout()

    # define update function
    def update(frame):
        ax.pcolormesh(xx, yy, var[frame, :, :], cmap=cmap, vmin=var.min(), vmax=var.max())
        if time is not None:
            for text in fig.texts:
                fig.texts.remove(text)
            plt.figtext(0.99, 0.01, 'Time at {}'.format(time[frame]), horizontalalignment='right')

    anim = FuncAnimation(fig, update, frames=time_end_index - time_start_index,
                         interval=interval, repeat=repeat)

    return anim
