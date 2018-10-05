"""
This is the 1st version sublimation analysis

step3: get variable stack array and array stats

requirement:
- get variable tif files converted from xmrg results.

step:
- get varaible array, all years sum and annual mean array
- export all years sum and annual mean array
- calculate domain average for sum and annual mean array

"""

import os

import gdalnumeric
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from snow_cover_utility import array_to_raster

# user settings ####################################################
watershed = 'McPhee'
folder_name = '{}_sublimation_analysis'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)

start_time = '1989/10/01'
end_time = '2009/10/01'  # this will exclude the end_time date e.g will only include data before 10/01.
yr = 20.0
dt = 6.0


var_list = ['ueb_Ec', 'ueb_Es', 'uebPrec', 'ueb_tet', 'ueb_rmlt',
            'snow17_rmlt', 'snow17_tet', 'snow17_xmrg'] # this needs to be the same as the tif_df.csv column name
calculate_total_sublimation = True  # calculate total sublimation and water loss
domain_ave_plot = True  # make plot of to compare two models mass balance

tif_df_path = os.path.join(result_folder, 'tif_df.csv')
stats_folder = os.path.join(result_folder, 'stats_folder')
if not os.path.isdir(stats_folder):
    os.mkdir(stats_folder)

# step1 get variable array, sum and annual mean ############################################################
var_array_dict = {}
var_array_sum_dict = {}
var_array_annual_mean_dict = {}

# get exiting variable array
tif_df = pd.DataFrame.from_csv(tif_df_path, header=0)
if start_time and end_time:
    tif_df = tif_df[(tif_df.index >= start_time) & (tif_df.index < end_time)]

for var in var_list:
    var_stack_list = []
    var_tif_folder = os.path.join(result_folder, 'tif_folder_{}'.format(var))
    print 'calculate {}'.format(var)
    if os.path.isdir(var_tif_folder):
        for time in tif_df.index:
            tif_path = os.path.join(var_tif_folder, tif_df[var].ix[time])
            tif_array = gdalnumeric.LoadFile(tif_path)
            var_stack_list.append(tif_array)

        # create stack array
        var_array = np.stack(var_stack_list)
        var_array_dict[var] = var_array
        np.save(os.path.join(stats_folder, '{}_tif_array'.format(var)), var_array)

        # create stack sum
        if var in ['ueb_Ec', 'ueb_Es']:
            mask = ~(tif_array == -99999.0)
            var_array_sum_dict[var] = np.where(mask, dt * np.nansum(var_array, axis=0), -99999.0)
            var_array_annual_mean_dict[var] = np.where(mask, dt * np.nansum(var_array, axis=0)/yr, -99999.0)
        else:
            mask = ~(tif_array < 0)
            var_array_sum_dict[var] = np.where(mask, np.nansum(var_array, axis=0), -99999.0)
            var_array_annual_mean_dict[var] = np.where(mask, np.nansum(var_array, axis=0)/yr, -99999.0)
    else:
        print 'No folder for {}'.format(var_tif_folder)

# calculate total sublimation and water loss array
if calculate_total_sublimation:
    var_array_sum_dict['total_sub'] = np.where(mask, var_array_sum_dict['ueb_Ec'] + var_array_sum_dict['ueb_Es'], -99999.0)
    var_array_annual_mean_dict['total_sub'] = np.where(mask, (var_array_sum_dict['ueb_Ec'] + var_array_sum_dict['ueb_Es'])/yr, -99999.0)
    var_array_sum_dict['water_loss'] = np.where(mask, 100*var_array_sum_dict['total_sub']/var_array_sum_dict['uebPrec'], -99999.0)
    var_array_annual_mean_dict['water_loss'] = np.where(mask, 100*var_array_annual_mean_dict['total_sub']/var_array_annual_mean_dict['uebPrec'], -99999.0)

# step 2 export array sum and annual mean as tif #############################################################
for var in var_array_sum_dict.keys():
    array_to_raster(output_path=os.path.join(stats_folder, 'sum_{}.tif'.format(var)),
                    source_path=tif_path,
                    array_data=var_array_sum_dict[var],
                    no_data=-99999.0)

    array_to_raster(output_path=os.path.join(stats_folder, 'annual_mean_{}.tif'.format(var)),
                    source_path=tif_path,
                    array_data=var_array_annual_mean_dict[var],
                    no_data=-99999.0)

# step3 calculate the domain average  #######################################################
# calculate the
domain_ave_df = pd.DataFrame(index=var_array_sum_dict.keys(), columns=['sum', 'annual_mean'])
for var in domain_ave_df.index:
    result = []
    for data_array in [var_array_sum_dict[var], var_array_annual_mean_dict[var]]:
        mask_array = np.ma.array(data_array, mask=~mask)
        result.append(round(mask_array.mean(), 3))

    domain_ave_df.ix[var] = result

domain_ave_df.to_csv(os.path.join(stats_folder, 'domain_ave.csv'))

if domain_ave_plot:
    data = domain_ave_df.round(2)
    for var in ['sum', 'annual_mean']:
        prec = [data.ix['uebPrec'][var], data.ix['snow17_xmrg'][var]]
        adj_prec = [0, round(data.ix['snow17_rmlt'][var] - data.ix['snow17_xmrg'][var], 2)]
        sub = [data.ix['total_sub'][var], 0]
        tet = [data.ix['ueb_tet'][var], data.ix['snow17_tet'][var]]

        plt.figure(figsize=(8,6))
        ind = [1, 2]
        width = .2
        left_bar = [x-width/2 for x in ind]
        right_bar = [x+width/2 for x in ind]

        p1 = plt.bar(left_bar, prec, width=width, color='dodgerblue')
        p2 = plt.bar(left_bar, adj_prec, width=width, bottom=prec, color='skyblue')
        p3 = plt.bar(right_bar, tet, width=width, color='g')
        p4 = plt.bar(right_bar, sub, width=width, bottom=tet, color='palegreen')

        plt.xticks(ind, ('UEB', 'SNOW-17'))
        plt.ylabel('water input/output (mm)')
        plt.legend((p1[0], p2[0], p3[0], p4[0]),
                   ('Precipitation', 'Adjusted water', 'ET', 'Sublimation'))
        plt.savefig(os.path.join(stats_folder, 'domain_ave_bar.png'))

print 'sublimation_analysis_3: variable array and array stats tif is done'