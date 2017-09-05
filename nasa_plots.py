"""
This is to make plots for NASA project output
"""
import os
from plot_time_series_domain import plot_time_series_domain_average
from plot_time_series import plot_time_series
from plot_2d_grid import plot_2d_grid, plot_2d_animation
import matplotlib.pyplot as plt


tag = 'NASA'
year = '1989'
watershed = 'Animas'
workDir = r'D:\3_NASA_Project\Model output and plots\Plot_{}_{}_{}'.format(watershed, year, tag)
os.chdir(workDir)

# point time series
for point in [[28, 45, 'molas lake'],[19, 36, 'Cascade']]:
    plot_time_series('concat_Animas1990P.nc', 'ogrid', 'time',
                      x_index=point[0], y_index=point[1], shape=['time', 'y', 'x'],
                      cumulative=False,
                      title='Concan Time series of precipitation in {} {} {} {}'.format(year, watershed, point[2], tag),
                      ylabel='Precipitation(m/hr)',
                      month_interval=2,
                      save_as= 'concan_precipitation_1989'#'preciitation_{}_{}_{}.png'.format(year,watershed,tag)
                     )

    plot_time_series('prcp0.nc', 'ogrid', 'time',
                     x_index=point[0], y_index=point[1], shape=['time', 'y', 'x'],
                      cumulative_scale=3,
                      title='Time series of precipitation in {} {} {} {}'.format(year, watershed, point[2], tag),
                      ylabel='Precipitation(m/hr)',
                      y2label='Cumulative of precipitation (m)',
                      save_as='precipitation_{}_{}_{}_{}.png'.format(year,watershed, point[2], tag))

    plot_time_series('temp0.nc', 'otgrid', 'time',
                     x_index=point[0], y_index=point[1], shape=['time', 'y', 'x'],
                      cumulative=False,
                      title='Time series of temperature in {} {} {} {}'.format(year, watershed, point[2], tag),
                      ylabel='Temperature (C)',
                      save_as='temperature_{}_{}_{}_{}.png'.format(year, watershed, point[2], tag))

    plot_time_series('SWE.nc', 'SWE', 'time',
                     x_index=point[0], y_index=point[1], shape=['y', 'x', 'time'],
                      title='Time series of SWE in {} {} {} {}'.format(year, watershed, point[2],tag),
                      cumulative=False,
                      save_as='swe_{}_{}_{}_{}.png'.format(year, watershed, point[2], tag))

    plot_time_series('SWIT.nc','SWIT', 'time',
                     x_index=point[0], y_index=point[1], shape=['y','x','time'],
                     cumulative_scale=3,
                     title='Time series of rain plus melt in {} {} {} {}'.format(year, watershed, point[2], tag),
                     ylabel='SWIT(m/hr)',
                     y2label='Cumulative of SWIT (m)',
                     save_as='swit_{}_{}_{}_{}.png'.format(year, watershed, point[2], tag))

# aggregation plot
fig, ax = plt.subplots(2, 1,figsize=(15,10))
plot_time_series('aggout.nc','SWIT', 'time',
                 x_index=0, shape=['x', 'time'],
                 fig=fig, ax=ax[0],
                 cumulative_scale=3,
                 title='Aggregation output of rain plus melt in {} {} {}'.format(year, watershed, tag),
                 ylabel='SWIT(m)',
                 y2label='Cumulative of SWIT (m)',
                 # save_as='agg_swit_{}_{}_{}.png'.format(year, watershed, tag)
                 )

plot_time_series('aggout.nc','SWE', 'time',
                  x_index=0, shape=['x', 'time'],
                  fig=fig,ax=ax[1],
                  cumulative=False,
                  title='Aggregation output of SWE in {} {} {}'.format(year, watershed, tag),
                  ylabel='SWE(m)',
                  # save_as='agg_swe_{}_{}_{}.png'.format(year, watershed, tag)
                 )

fig.savefig('aggregation.png')
plt.tight_layout()

# domain average
plot_time_series_domain_average('prcp0.nc', 'ogrid', time='time',
                                xaxis_index=2, yaxis_index=1,
                                cumulative=True,
                                cumulative_scale=3,
                                title='Domain average of Precipitation in {} {} {}'.format(year, watershed, tag),
                                ylabel='Precipitation (m/hr)',
                                y2label='Cumulative of domain average Precipitation (m)',
                                save_as='domain_ave_prec_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_series_domain_average('SWE.nc', 'SWE', time='time',
                                xaxis_index=1, yaxis_index=0,
                                cumulative=False,
                                title='Domain average of SWE in {} {}'.format(year, tag),
                                ylabe='SWE(m)',
                                save_as='domain_ave_swe_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_series_domain_average('SWIT.nc', 'SWIT', time='time',
                                xaxis_index=1, yaxis_index=0,
                                cumulative=True, cumulative_scale=3,
                                title='Domain average of rain plus melt in {} {} {}'.format(year, watershed, tag),
                                ylabel='SWIT (m)',
                                y2label='Cumulative of domain average SWIT (m)',
                                save_as='domain_ave_swit_{}_{}_{}.png'.format(year, watershed, tag))


# 2D plot and animation
plot_2d_grid(x_name='x',
             y_name='y',
             var_name='ogrid',
             time_name='time',
             file_path='prcp0.nc',
             var_shape=['time', 'x', 'y'],
             time_index=1000,
             slice_obj=None,
             title=None,
             xlabel=None,
             ylabel=None,
             figsize=None,
             save_as=None)

fig, ax = plt.subplots()
plot_2d_grid(x_name='x',
             y_name='y',
             var_name='ogrid',
             time_name='time',
             file_path='prcp0.nc',
             var_shape=['time', 'x', 'y'],
             fig=fig,
             ax=ax,
             time_index=1000,
             slice_obj=None,
             title=None,
             xlabel=None,
             ylabel=None,
             figsize=None,
             save_as=None)


plot_2d_animation(file_path='prcp0.nc', x_name='x', y_name='y',
                  var_name='ogrid', var_shape=['time', 'y', 'x'],
                  time_name='time', time_start_index=1000, time_end_index=1010,
                  interval=300,
                  title='animation', xlabel='x', ylabel='y',
                  cmap='viridis',
                  repeat=False,
                  )

anim = plot_2d_animation(file_path='SWE.nc', x_name='x', y_name='y',
                  var_name='SWE', var_shape=['y', 'x', 'time'],
                  time_name='time', time_start_index=1060, time_end_index=1100,
                  interval=300,
                  title='Animation of SWE at Animas 1989-1990', xlabel='x', ylabel='y',
                  cmap='viridis',
                  repeat=True,
                  figsize=(10,10),
                  )

# This is for displaying animation on Jupyternotebook
# import matplotlib
# from IPython.display import HTML
# matplotlib.rcParams['animation.writer']='avconv'
# HTML(anim.to_html5_video())
# set the jupternote book output size: "Cell"-> Current output -> toggle scrolling