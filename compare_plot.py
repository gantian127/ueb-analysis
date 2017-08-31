import os
from plot_multiple_time_series import *

tag = 'NASA'
year = '1989'
watershed = 'Animas'
workDir = r'C:\Users\jamy\Desktop\Plot_{}_{}_{}'.format(watershed, year,tag)
os.chdir(workDir)

# compare domain average SWIT and SWE
time_data = get_time_value(file_path='SWIT.nc', time_var='time', units=None, calendar=None)
swit_data_ave = get_var_ave(file_path='SWIT.nc', var_name='SWIT', axis_index=(0, 1))
prcp_data_ave = get_var_ave(file_path='prcp0.nc', var_name='ogrid', axis_index=(2, 1))
swit_data_acc = get_cumulative(swit_data_ave, cumulative_scale=3)
prcp_data_acc = get_cumulative(prcp_data_ave, cumulative_scale=3)
swe_data_ave = get_var_ave(file_path='SWE.nc', var_name='SWE', axis_index=(0,1))
plot_multiple_time_series(time_data, [prcp_data_acc[2:2906], swit_data_acc, swe_data_ave], color_list=None, month_interval=1, legend=True,
                          title='Cumulative precipitation vs. Cumulative rain plus melt (domain average)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','average swe'],
                          save_as='compare_swit_prcp2.png',

                          )


# compare cumulative SWIT vs Prce and SWE
time_data = get_time_value(file_path='SWIT.nc', time_var='time', units=None, calendar=None)
swit_point = get_var_point_data(file_path='SWIT.nc', var_name='SWIT', x_index=19, y_index=36, var_dim_list=['y','x','time'])
prcp_point = get_var_point_data(file_path='prcp0.nc', var_name='ogrid', x_index=19, y_index=36, var_dim_list=['time','y','x'])
swit_data_acc = get_cumulative(swit_point, cumulative_scale=3)
prcp_data_acc = get_cumulative(prcp_point, cumulative_scale=3)
plot_multiple_time_series(time_data, [prcp_data_acc[2:2906], swit_data_acc, swe_data_ave], color_list=None, month_interval=1, legend=True,
                          title='Cumulative precipitation vs. Cumulative rain plus melt (Cascade)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','average swe'],
                          save_as='compare_swit_prcp_cascade.png',
                          )


# compare cumulative SWIT vs Prce and SWE
time_data = get_time_value(file_path='SWIT.nc', time_var='time', units=None, calendar=None)
swit_point = get_var_point_data(file_path='SWIT.nc', var_name='SWIT', x_index=28, y_index=45, var_dim_list=['y','x','time'])
prcp_point = get_var_point_data(file_path='prcp0.nc', var_name='ogrid', x_index=28, y_index=45, var_dim_list=['time','y','x'])
swit_data_acc = get_cumulative(swit_point, cumulative_scale=3)
prcp_data_acc = get_cumulative(prcp_point, cumulative_scale=3)
plot_multiple_time_series(time_data, [prcp_data_acc[2:2906], swit_data_acc, swe_data_ave], color_list=None, month_interval=1, legend=True,
                          title='Cumulative precipitation vs. Cumulative rain plus melt (Molas Lake)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','average swe'],
                          save_as='compare_swit_prcp_molaslake.png',
                          )

# test subplots
fig, ax = plt.subplots(2,1,figsize=(15,10))

swit_data_ave = get_var_ave(file_path='SWIT.nc', var_name='SWIT', axis_index=(0, 1))
time_data = get_time_value(file_path='SWIT.nc', time_var='time', units=None, calendar=None)
swit_point = get_var_point_data(file_path='SWIT.nc', var_name='SWIT', x_index=19, y_index=36, var_dim_list=['y','x','time'])
prcp_point = get_var_point_data(file_path='prcp0.nc', var_name='ogrid', x_index=19, y_index=36, var_dim_list=['time','y','x'])
swit_data_acc = get_cumulative(swit_point, cumulative_scale=3)
prcp_data_acc = get_cumulative(prcp_point, cumulative_scale=3)
swe_data_ave = get_var_ave(file_path='SWE.nc', var_name='SWE', axis_index=(0,1))
plot_multiple_time_series(time_data, [prcp_data_acc[2:2906], swit_data_acc, swe_data_ave],
                          fig=fig,ax=ax[0],
                          color_list=None, month_interval=1, legend=True,
                          title='Cumulative precipitation vs. Cumulative rain plus melt (Cascade)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','average swe'],
                          )

time_data = get_time_value(file_path='SWIT.nc', time_var='time', units=None, calendar=None)
swit_point = get_var_point_data(file_path='SWIT.nc', var_name='SWIT', x_index=28, y_index=45, var_dim_list=['y','x','time'])
prcp_point = get_var_point_data(file_path='prcp0.nc', var_name='ogrid', x_index=28, y_index=45, var_dim_list=['time','y','x'])
swit_data_acc = get_cumulative(swit_point, cumulative_scale=3)
prcp_data_acc = get_cumulative(prcp_point, cumulative_scale=3)
plot_multiple_time_series(time_data, [prcp_data_acc[2:2906], swit_data_acc, swe_data_ave],
                          fig=fig, ax=ax[1],
                          color_list=None, month_interval=1, legend=True,
                          title='Cumulative precipitation vs. Cumulative rain plus melt (Molas Lake)',
                          xlabel='Time', ylabel='water input/output (m)',
                          line_label_list=['cumulative precipitation','cumulative rain plus melt','average swe'],
                          )

plt.tight_layout()