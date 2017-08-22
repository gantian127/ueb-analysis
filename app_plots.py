"""
This is to make plots for UEB APP output
"""
import os
from plot_time_serise_domain import plot_time_serise_domain_average
from plot_time_serise import plot_time_serise


tag = 'App'
year = '2009'
watershed = 'Animas'
workDir = r'C:\Users\jamy\Desktop\{}_{}_{}'.format(watershed, year, tag)
os.chdir(workDir)

# point plot
plot_time_serise('prcp0.nc', 'prcp', 'time',
                  x_index=19, y_index=29, shape=['time', 'y', 'x'],
                  cumulative_scale=24,
                  title='Time serise of precipitation in {} {} {}'.format(year, watershed, tag),
                  ylabel='Precipitation(m/hr)',
                  y2label='Cumulative of precipitation (m)',
                  save_as='preciitation_{}_{}_{}.png'.format(year,watershed,tag))
29
plot_time_serise('SWE.nc', 'SWE', 'time',
                  x_index=19, y_index=29, shape=['time', 'y', 'x'],
                  title='Time serise of SWE in {} {} {}'.format(year, watershed, tag),
                  cumulative=False,
                  save_as='swe_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_serise('SWIT.nc','SWIT', 'time',
                 x_index=19, y_index=29, shape=['time', 'y', 'x'],
                 cumulative_scale=6,
                 title='Time serise of SWIT in {} {} {}'.format(year, watershed, tag),
                 ylabel='SWIT(m/hr)',
                 y2label='Cumulative of SWIT (m)',
                 save_as='swit_{}_{}_{}.png'.format(year, watershed, tag))

# aggregation
plot_time_serise('aggout.nc','SWIT', 'time',
                 x_index=0, shape=['time', 'x'],
                 cumulative_scale=6,
                 title='Aggregation output of SWIT in {} {} {}'.format(year, watershed, tag),
                 ylabel='SWIT(m)',
                 y2label='Cumulative of SWIT (m)',
                 save_as='agg_swit_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_serise('aggout.nc','SWE', 'time',
                  x_index=0, shape=['time', 'x'],
                  cumulative=False,
                  title='Aggregation output of SWE in {} {}'.format(year, tag),
                  ylabel='SWE(m)',
                  save_as='agg_swe_{}_{}_{}.png'.format(year, watershed, tag))

# domain average
plot_time_serise_domain_average('prcp0.nc', 'prcp', time='time',
                                xaxis_index=2, yaxis_index=1,
                                cumulative=True,
                                cumulative_scale=3,
                                title='Domain average of Precipitation in {} {} {}'.format(year, watershed, tag),
                                ylabel='Precipitation (m/hr)',
                                y2label='Cumulative of domain average Precipitation (m)',
                                save_as='domain_ave_prec_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_serise_domain_average('SWE.nc', 'SWE', time='time',
                                xaxis_index=2, yaxis_index=1,
                                cumulative=False,
                                title='Domain average of SWE in {} {}'.format(year, tag),
                                ylabe='SWE(m)',
                                save_as='domain_ave_swe_{}_{}_{}.png'.format(year, watershed, tag))

plot_time_serise_domain_average('SWIT.nc', 'SWIT', time='time',
                                xaxis_index=2, yaxis_index=1,
                                cumulative=True, cumulative_scale=6,
                                title='Domain average of SWIT in {} {} {}'.format(year, watershed, tag),
                                ylabel='SWIT (m)',
                                y2label='Cumulative of domain average SWIT (m)',
                                save_as='domain_ave_swit_{}_{}_{}.png'.format(year, watershed, tag))