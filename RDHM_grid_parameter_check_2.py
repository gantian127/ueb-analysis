"""
This is used to convert the RDHM xmrg parameter grids for comparions and checking purpose

requiremnet:
step1 is done

purpose:
this is aimed to check about the pe monthly grids and its value.
This is also used to calculate the weighted peadj

"""

import os

import gdalnumeric
import numpy as np
import matplotlib.pyplot as plt
from time import strptime
import pandas as pd



# user settings  ####################################################################################################
parameter_folder = '/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/test/params1k.co/parameter_result'  # folder that includes the processed parameter tif files
result_folder = os.path.join(os.getcwd(), 'pe_analysis')

if not os.path.isdir(result_folder):
    os.mkdir(result_folder)

# calculate stats for pe grid #################################################################
# get pe_mon grid path
pe_path_list = [os.path.join(parameter_folder,file_path) for file_path in os.listdir(parameter_folder) if 'pe_' in os.path.basename(file_path)]

# process Pe grid for stats
stats_result = pd.DataFrame(columns=['name', 'sum', 'mean', 'max', 'min', 'month'])
for clip_path in pe_path_list:
    raw_grid = gdalnumeric.LoadFile(clip_path)
    mask_grid = np.ma.masked_array(raw_grid[0], mask=(raw_grid[1] == 0))
    name = os.path.basename(clip_path).replace('.tif', '')

    # calculate stats
    month = strptime(name[-3:], '%b').tm_mon
    sum = mask_grid.sum()
    min = mask_grid.min()
    max = mask_grid.max()
    mean = mask_grid.mean()

    # make plots
    plt.clf()
    plt.imshow(mask_grid)
    plt.colorbar()
    plt.title('Plot of {}'.format(name))
    plt.savefig(os.path.join(result_folder, name+'.png'))

    stats_result.loc[len(stats_result)] = [name, sum, mean, max, min, month]
stats_result.to_csv(os.path.join(result_folder, 'stats_result.csv'))

print 'PE grid analysis done!'









