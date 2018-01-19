"""
This is aimed to make plot to validate whether the UEB model sublimation is working as expected

- time series for precp, temp, swe, swit, canopy sublimation, ground sublimation
- mass balance plots

Results: for no snow time e.g. July, 1993 there is still ground sublimation.
"""


import pandas as pd
import os
from datetime import datetime
import urllib
from plot_SAC_utility import *


results_dir = 'ueb_sublimation_test'
if not os.path.isdir(results_dir):
    os.mkdir(results_dir)


point_info = {
    'molaslake': 'C:\Users\jamy\Desktop\Nasa_analysis\molaslake.txt',
    'cascade': 'C:\Users\jamy\Desktop\Nasa_analysis\cascade.txt'
}

start_time = '1993-07-01'
end_time = '1993-08-01'

var_plot_list = [
    (['Ta', 'Tc'], 'C'),
    ('SWIT', 'm/hr'),
    (['P', 'Pr', 'Ps'], 'm/hr'),
    (['SWE', 'Wc'], 'm'),
    ('SWE', 'm'),
    ('Wc', 'm'),
    (['Es', 'Ec'], 'm/hr'),
    ('cumes', 'm'),
    ('cump', 'm'),
    ('cumMr', 'm')
]


# read data as dataframe
for point_name, point_file in point_info.items():

    # get model simulation data frame
    point_df = pd.read_csv(point_file, sep='\s+')
    point_df['time'] = point_df['Year'].map(str) + ' ' + point_df['Month'].map(str) + ' ' + point_df['Day'].map(
        str) + ' ' + point_df['dHour'].map(int).map(str)
    point_df['time'] = point_df['time'].apply(lambda x: datetime.strptime(x, '%Y %m %d %H'))
    point_df['error'] = point_df['cump'] - point_df['cumes'] - point_df['cumMr'] - point_df['SWE']
    if start_time and end_time:
        point_df = point_df.ix[(point_df.time >= start_time) & (point_df.time <= end_time)]

    # time series plot
    for var, unit in var_plot_list:
        try:
            Y = []
            if type(var) is list:
                for var_name in var:
                    Y.append(point_df[var_name].tolist())
            else:
                Y.append(point_df[var].tolist())

            label = ','.join(var) if type(var) is list else var

            fig, ax = plt.subplots(figsize=(15, 5))
            plot_multiple_X_Y(point_df.time,
                              Y,
                              fig=fig, ax=ax,
                              label_list=var if type(var) is list else [var],
                              )

            refine_plot(ax,
                        title='Plot of {} for {} '.format(label, point_name),
                        ylabel='{}({})'.format(label, unit),
                        xlabel='time',
                        interval=1,
                        )

            path = os.path.join(os.getcwd(), results_dir, 'Plot_of_{}_for_{}.png'.format(label, point_name))
            fig.savefig(path)

        except Exception as e:
            print 'Failed to plot {}'.format(var)

print 'Plot finished !'