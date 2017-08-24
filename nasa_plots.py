"""
This is to make plots for NASA project output
"""
import os
from plot_time_series_domain import plot_time_series_domain_average
from plot_time_series import plot_time_series


tag = 'NASA'
year = '1989'
watershed = 'Animas'
workDir = r'C:\Users\jamy\Desktop\Plot_{}_{}_{}'.format(watershed, year, tag)
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
plot_time_series('aggout.nc','SWIT', 'time',
                 x_index=0, shape=['x', 'time'],
                 cumulative_scale=3,
                 title='Aggregation output of rain plus melt in {} {} {}'.format(year, watershed, tag),
                 ylabel='SWIT(m)',
                 y2label='Cumulative of SWIT (m)',
                 save_as='agg_swit_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_series('aggout.nc','SWE', 'time',
                  x_index=0, shape=['x', 'time'],
                  cumulative=False,
                  title='Aggregation output of SWE in {} {} {}'.format(year, watershed, tag),
                  ylabel='SWE(m)',
                  save_as='agg_swe_{}_{}_{}.png'.format(year, watershed, tag))

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

