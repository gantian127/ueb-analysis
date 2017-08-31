# plot variable time serise
import netCDF4
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

prcp = netCDF4.Dataset('prcp0.nc','r')
ogrid = prcp.variables['ogrid']
time = prcp.variables['time']
x = prcp.variables['x']
y = prcp.variables['y']
ogrid_data = ogrid[:,30,20]
ogrid_data_acc = numpy.cumsum(ogrid_data)
time_data = time[:]
time_obj = [netCDF4.num2date(value,units='hours since 2009-07-01 00:00:00 UTC', calendar='standard') for value in time_data]

# make plot
fig, ax = plt.subplots()
ax1 = ax.twinx()
ax.plot(time_obj, ogrid_data)
ax1.plot(time_obj,ogrid_data_acc)

# axis formatting
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
ax.set_xlabel('time')
ax.set_ylabel('y_label')

# plot
plt.title('Precipitation in Animas Watershed')
plt.xlabel('Time')
plt.ylabel('Precipitation(m/hr)')


# subplots on one figure
fig, axarr = plt.subplots(2, 2, sharey=True, sharex=True) # this will return 1 figure obj with 4 axis objects that share both x and y axis
plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)  # setp() is used to set the property of an artist objects
# set property of artist object


# make animation
# get root group
group = netCDF4.Dataset('prcp0.nc', 'r')

# get variables
x = group.variables['x'][:]
y = group.variables['y'][:]
var = group.variables['ogrid'][1000:1030, :, :]
# time = get_time_var('file_path')
#     time = group.variables[time_name][:]
group.close()

xx, yy = numpy.meshgrid(x, y)
fig, ax = plt.subplots()
plot = ax.pcolormesh(xx, yy, var[0, :, :], cmap='viridis', vmin=var.min(), vmax=var.max())
ax.set_title('hi')
fig.colorbar(plot)


def update(frame):
    ax.pcolormesh(xx, yy, var[frame, :, :], cmap='viridis', vmin=var[frame, :, :].min(), vmax=var[frame, :, :].max())
    ax.set_title(str(frame))


anim = FuncAnimation(
    fig, update, frames=20, interval=1)

plt.show()






