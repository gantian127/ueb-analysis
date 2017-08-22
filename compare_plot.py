import os
from plot_multiple_time_serise import *

tag = 'App'
year = '2009'
watershed = 'Animas'
workDir = r'C:\Users\jamy\Desktop\Plot_compare_{}_{}'.format(watershed, year)
os.chdir(workDir)

# compare SWIT and SWE
x_data = get_time_value(file_path='SWIT.nc', time_var='time', units=None, calendar=None)
y_data = get_var_point_data(file_path='SWIT.nc', var_name='SWIT', x_index=19, y_index=29, var_dim_list=['y','x','time'])
y2_data = get_var_point_data(file_path='SWISM.nc', var_name='SWISM', x_index=19, y_index=29,var_dim_list=['y','x','time'])
plot_multiple_time_serise(x_data, [y_data, y2_data], color_list=None, month_interval=1, legend=True,
                          title='comparison of SWIT and SWISM', xlabel=None, ylabel=None,save_as=None)

