"""
This is used to convert the RDHM xmrg parameter grids for comparions and checking purpose

requiremnet:
step 1 is done

purpose:
This is aimed to compare two source of parameter grids and check the difference.

"""

import os

import gdalnumeric
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# user settings  ####################################################################################################
# folder that include the processed grid tif folder
src1_name = 'ueb'
src2_name = 'snow17'
src1_folder = '/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/test/params1k.co_ueb/parameter_result'
src2_folder = '/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/test/params1k.co_snow17/parameter_result'

# result folder
result_folder = os.path.join(os.getcwd(), 'parameter_compare_{}_{}'.format(src1_name,src2_name))
if not os.path.isdir(result_folder):
    os.mkdir(result_folder)

# calculate stats for pe grid #################################################################
stats_result = pd.DataFrame(columns=['name', 'parameter', 'sum', 'mean', 'max', 'min'])
for file_name in os.listdir(src1_folder):
    src1_path = os.path.join(src1_folder, file_name)
    src2_path = os.path.join(src2_folder, file_name)
    if os.path.isfile(src1_path) and os.path.isfile(src2_path):

        src1_grid = gdalnumeric.LoadFile(src1_path)
        src2_grid = gdalnumeric.LoadFile(src2_path)
        diff_grid = src1_grid[0] - src2_grid[0]
        mask = src1_grid[1]
        for grid, name in zip([src1_grid[0], src2_grid[0], diff_grid], [src1_name, src2_name, 'diff']):
            mask_grid = np.ma.masked_array(grid, mask=(mask == 0))

            # calculate stats
            parameter = file_name[:-4]
            sum = mask_grid.sum()
            min = mask_grid.min()
            max = mask_grid.max()
            mean = mask_grid.mean()

            # make plots
            plt.clf()
            plt.imshow(mask_grid)
            plt.colorbar()
            if name == 'diff':
                plt.title('Plot of {} difference between {} and {}'.format(parameter, src1_name, src2_name))
            else:
                plt.title('Plot of {} from {}'.format(parameter, name))
            plt.savefig(os.path.join(result_folder, '{}_{}.png'.format(parameter,name)))

            stats_result.loc[len(stats_result)] = [name, parameter, sum, mean, max, min]
stats_result.to_csv(os.path.join(result_folder, 'stats_result.csv'))

print 'Parameter compare analysis is done!'









