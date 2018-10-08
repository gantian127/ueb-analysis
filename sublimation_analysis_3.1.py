"""
This is the 1st version sublimation analysis

step3.1: get variable stack array and array stats
         step3 is adding all multiple years as one stack and calculate the annual mean
         step3.1 is adding each year as one stack and calculate the annual mean and the standard error of mean

requirement:
- get variable tif files converted from xmrg results.

step:
- get variable array, all years sum and annual mean array
- export each years sum
- calculate domain average using each year sum tif.
- calculate annual mean and standard error of mean using multiple year domain average for each year

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

start_year = 1989   # the year for start time e.g. '1989-10-01'
end_year = 2009  # the year for end time  e.gl '2009-9-30'
dt = 6.0

var_list = ['ueb_Ec', 'ueb_Es', 'uebPrec', 'ueb_tet', 'ueb_rmlt',
            'snow17_rmlt', 'snow17_tet', 'snow17_xmrg'] # this needs to be the same as the tif_df.csv column name

get_annual_array = False
calculate_total_sublimation = True  # calculate total sublimation and water loss
domain_ave_plot = True  # make plot of to compare two models mass balance

tif_df_path = os.path.join(result_folder, 'tif_df.csv')
stats_folder = os.path.join(result_folder, 'stats_folder')
if not os.path.isdir(stats_folder):
    os.mkdir(stats_folder)

# step1 get annual array and sum tif  ############################################################
if get_annual_array:
    for year in range(start_year, end_year):
        start_time = '{}-10-01'.format(year)
        end_time = '{}-10-01'.format(year+1)

        var_array_dict = {}
        var_array_sum_dict = {}

        # get exiting variable array
        tif_df = pd.DataFrame.from_csv(tif_df_path, header=0)
        if start_time and end_time:
            tif_df = tif_df[(tif_df.index >= start_time) & (tif_df.index < end_time)]

        for var in var_list:
            var_stack_list = []
            var_tif_folder = os.path.join(result_folder, 'tif_folder_{}'.format(var))
            print 'calculate {} in {}'.format(var, year)

            if os.path.isdir(var_tif_folder):
                numpy_array_file = os.path.join(stats_folder, '{}_tif_array_{}.npy'.format(var, year))
                for time in tif_df.index:
                    tif_path = os.path.join(var_tif_folder, tif_df[var].ix[time])
                    tif_array = gdalnumeric.LoadFile(tif_path)
                    var_stack_list.append(tif_array)

                # create stack array
                var_array = np.stack(var_stack_list)
                var_array_dict[var] = var_array
                np.save(numpy_array_file, var_array)

                # create stack sum
                if var in ['ueb_Ec', 'ueb_Es']:
                    mask = ~(tif_array == -99999.0)
                    var_array_sum_dict[var] = np.where(mask, dt * np.nansum(var_array, axis=0), -99999.0)
                else:
                    mask = ~(tif_array < 0)
                    var_array_sum_dict[var] = np.where(mask, np.nansum(var_array, axis=0), -99999.0)

            else:
                print 'No folder for {}'.format(var_tif_folder)

        # calculate total sublimation and water loss array
        if calculate_total_sublimation:
            var_array_sum_dict['total_sub'] = np.where(mask, var_array_sum_dict['ueb_Ec'] + var_array_sum_dict['ueb_Es'], -99999.0)
            var_array_sum_dict['water_loss'] = np.where(mask, 100*var_array_sum_dict['total_sub']/var_array_sum_dict['uebPrec'], -99999.0)

        # export array sum as tif
        for var in var_array_sum_dict.keys():
            sum_tif_path = os.path.join(stats_folder, 'sum_{}_{}.tif'.format(var, year))
            if not os.path.isfile(sum_tif_path):
                array_to_raster(output_path=sum_tif_path,
                                source_path=tif_path,
                                array_data=var_array_sum_dict[var],
                                no_data=-99999.0)


# step2 get mean from array sum tif  ##############################################
# make sure to add the total_sub and water_loss variable
if calculate_total_sublimation:
    var_list.extend(['total_sub', 'water_loss'])

# get domain average for annual sum
domain_ave_df = pd.DataFrame(index=range(start_year, end_year), columns=var_list)
for year in domain_ave_df.index:
    for var in domain_ave_df.columns:
        sum_tif_path = os.path.join(stats_folder, 'sum_{}_{}.tif'.format(var, year))
        if os.path.isfile(sum_tif_path):
            data_array = gdalnumeric.LoadFile(sum_tif_path)
            mask = (data_array == -99999.0)
            mask_array = np.ma.array(data_array,mask=mask)
            domain_ave_df.ix[year][var] = round(mask_array.mean(), 3)
        else:
            print 'no {}'.format(sum_tif_path)

domain_ave_df.to_csv(os.path.join(stats_folder, 'domain_ave_df.csv'))

# get the annual mean stats
annual_stats_df = pd.DataFrame(index=domain_ave_df.columns)
annual_stats_df['sum'] = domain_ave_df.sum()
annual_stats_df['annual_mean'] = domain_ave_df.mean()
annual_stats_df['sem'] = domain_ave_df.sem()
annual_stats_df.to_csv(os.path.join(stats_folder, 'annual_stats_df.csv'))


# step 3  make the plot  #########################################################
if domain_ave_plot:
    data = annual_stats_df.round(2)
    for var in ['annual_mean']:
        prec = [data.ix['uebPrec'][var], data.ix['snow17_xmrg'][var]]
        adj_prec = [0, round(data.ix['snow17_rmlt'][var] - data.ix['snow17_xmrg'][var], 2)]
        total_prec_err = [data.ix['uebPrec']['sem'], data.ix['snow17_rmlt']['sem']]

        sub = [data.ix['total_sub'][var], 0]
        tet = [data.ix['ueb_tet'][var], data.ix['snow17_tet'][var]]
        total_ET_err = [data.ix['total_sub']['sem']+data.ix['ueb_tet']['sem'], data.ix['snow17_tet']['sem']]

        plt.figure(figsize=(8, 6))
        ind = [1, 2]
        width = .2
        left_bar = [x-width/2 for x in ind]
        right_bar = [x+width/2 for x in ind]

        p1 = plt.bar(left_bar, prec, width=width, color='dodgerblue')
        p2 = plt.bar(left_bar, adj_prec, width=width, bottom=prec, color='skyblue', yerr=total_prec_err)
        p3 = plt.bar(right_bar, tet, width=width, color='g')
        p4 = plt.bar(right_bar, sub, width=width, bottom=tet, color='palegreen', yerr=total_ET_err)

        plt.xticks(ind, ('UEB', 'SNOW-17'))
        plt.ylabel('water input/output (mm)')
        plt.legend((p1[0], p2[0], p3[0], p4[0]),
                   ('Precipitation', 'Adjusted water', 'ET', 'Sublimation'))
        plt.savefig(os.path.join(stats_folder, 'domain_ave_bar.png'.format(var)))

print 'sublimation_analysis_3.1: variable array and array stats tif is done'