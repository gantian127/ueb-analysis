"""
This is the 3rd version formal script for snow cover area analysis

step5:  use project tif files get binary files and calculate 2D graph stats to see under estimate and over estimate places

requirements:
- matplotlib version 2.1.2
- pandas version 0.22.0
- need to run step4 to get the refined pixel count file

step:
- get binary array and type pixel stack
- calculate stats and make plots

results:
- snow error:
  ueb has no special pattern but has jummping grid
  snow17 has terrain pattern. The pattern is most like where snow happens a lot.

- dry error:
  ueb and snow17 both has terrain pattern. Mainly related to aspect and slope
  snow17 has more clear pattern. The pattern is most like where dry area happens a lot
"""

import os
import gdalnumeric
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from snow_cover_utility import array_to_raster

# default user settings apply to all steps ####################################################
# folders/files created by step 3 script
watershed = 'MPHC2'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')
modis_proj_folder = os.path.join(result_folder, 'modis_proj_folder')
swe_proj_folders = [os.path.join(result_folder, name) for name in ['snow17_proj_folder', 'ueb_proj_folder']]
stats_folder = os.path.join(result_folder, 'stats_folder')
valid_pixel_count_path = [os.path.join(stats_folder, 'refine_pixel_count_{}.csv'.format(name)) for name in ['snow17', 'ueb']]

# time for analysis:
start_time = '2000/10/01'
end_time = '2010/06/30'

# threshold for processing
swe_threshold = 1  # mm

plt.ioff()

# step1: get binary array and type pixel stack ##############################################################

# load data
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)
for pixel_count_path in valid_pixel_count_path:
    if os.path.isfile(pixel_count_path):
        pixel_count = pd.DataFrame.from_csv(pixel_count_path, header=0)
        if start_time and end_time:
            valid_index = pixel_count.index[(pixel_count.index >= start_time) & (pixel_count.index <= end_time)]
        else:
            valid_index = pixel_count.index
        break
print len(valid_index)


for swe_proj_folder in swe_proj_folders:
    swe_col_name = os.path.basename(swe_proj_folder)
    model = swe_col_name.split('_')[0]

    if os.path.isdir(swe_proj_folder) and os.path.isdir(modis_proj_folder):
        # get different stack array #########################################################################
        print 'step1: get stack array '
        A_stack = []
        B_stack = []
        C_stack = []
        D_stack = []
        cloud_stack = []
        for time in valid_index:
            modis_proj_path = os.path.join(modis_proj_folder, snow_date['modis_proj_folder'].ix[time])
            swe_proj_path = os.path.join(swe_proj_folder, snow_date[swe_col_name].ix[time])

            if os.path.isfile(swe_proj_path) and os.path.isfile(modis_proj_path):
                try:
                    # get modis binary
                    modis = gdalnumeric.LoadFile(modis_proj_path)
                    modis_bin = np.where(modis[1] != 0, modis[0], -999)
                    modis_bin[modis_bin > 100] = -999
                    modis_bin[modis_bin > 0] = 1

                    # get swe binary
                    swe = gdalnumeric.LoadFile(swe_proj_path)
                    swe_bin = np.where(modis_bin != -999, swe, -999)
                    swe_bin[swe_bin >= swe_threshold] = 1
                    swe_bin[(swe_bin >= 0) & (swe_bin < swe_threshold)] = 0

                    # create type grid:
                    grid_list = []
                    for swe_value in [0, 1]:
                        for modis_value in [0, 1]:
                            grid = np.zeros_like(modis_bin)
                            mask = (modis[1] == 0)
                            grid[mask] = -999
                            grid[(swe_bin == swe_value) & (modis_bin == modis_value)] = 1
                            grid_list.append(grid)
                    A_stack.append(grid_list[0])
                    B_stack.append(grid_list[1])
                    C_stack.append(grid_list[2])
                    D_stack.append(grid_list[3])

                    # create cloud grid:
                    grid = np.zeros_like(modis_bin)
                    mask = (modis[1] == 0)
                    grid[mask] = -999
                    cloud_index = (modis[0] == 250)
                    grid[cloud_index] = 1
                    cloud_stack.append(grid)

                except Exception as e:
                    print 'fail at {}'.format(time)
                    continue
            else:
                print 'data not exit at {}'.format(time)

        # calculate stats and make plots ##############################################################
        print 'step2: calculate type stats '
        stack_sum_dict = {}
        for data_type, stack in zip(['A', 'B', 'C', 'D', 'Cloud'], [A_stack, B_stack, C_stack, D_stack, cloud_stack]):
            try:
                file_path = os.path.join(stats_folder, '{}_{}'.format(data_type, model))
                stack_array = np.stack(stack)
                np.save(file_path, stack_array)

                stack_sum = np.where(mask == False, np.nansum(stack_array, axis=0), -999)
                np.save(file_path+'_sum', stack_sum)
                stack_sum_dict[data_type] = stack_sum

                ma = np.ma.masked_equal(stack_sum, -999, copy=False)
                plt.imshow(ma, interpolation='nearest')
                plt.colorbar()
                plt.title('plot of sum of {} type pixels'.format(data_type))
                plt.savefig(file_path + '.png')
                plt.clf()

                # export result as raster data
                array_to_raster(output_path=file_path + '.tif',
                                source_path=swe_proj_path,
                                array_data=stack_sum,
                                no_data=-1)
            except Exception as e:
                continue

        # calculate accurate data and evaluation #########################################################
        print 'step3: calculate error stats '
        snow = np.where(mask == False, (stack_sum_dict['B'] + stack_sum_dict['D']), -999.0)
        dry = np.where(mask == False, (stack_sum_dict['A'] + stack_sum_dict['C']), -999.0)
        snow_error = np.where(mask == False, stack_sum_dict['B']*1.0/snow, -999.0)
        dry_error = np.where(mask == False, stack_sum_dict['C']*1.0/dry, -999.0)

        for data_type, stack in zip(['snow', 'dry', 'snow error', 'dry error'], [snow, dry, snow_error, dry_error]):
            try:
                file_path = os.path.join(stats_folder, '{}_{}'.format(data_type, model))
                np.save(file_path, stack)
                ma = np.ma.masked_equal(stack, -999, copy=False)
                plt.imshow(ma, interpolation='nearest')
                plt.colorbar()
                if data_type in ['snow error', 'dry error']:
                    plt.clim(0, 1)
                plt.title('plot of {} for {} model'.format(data_type, model))
                plt.savefig(file_path + '.png')
                plt.clf()

                # export result as raster data
                array_to_raster(output_path=file_path + '.tif',
                                source_path=swe_proj_path,
                                array_data=stack,
                                no_data=-1)
            except Exception as e:
                print 'failed for {} grid'.format(data_type)
                continue

    else:
        print 'no {}'.format(swe_col_name)

    print 'snow_analysis_5: 2D graph analysis is done'
