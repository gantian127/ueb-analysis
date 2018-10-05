"""
This is the 1st version sublimation analysis

step5: use terrain data to calculate sublimation stats

requirement:
- terrain tif of lai, dem, cc


results:
- bar plot: open/forest land type sublimation components compare
- scatter plot: elevation vs total ET, prec for different land type

# how lai, cc, hcan prepared
nlcd_type_dict = {
    11: 'water',[lai0]
    12: 'perennial ice snow',[lai0]
    21: 'developed open space',[lai0]
    22: 'developed Low intensity',[lai0]
    23: 'developed medium intensity',[lai0]
    24: 'developed high intensity',[lai0]
    31: 'bare rock', [lai0]
    41: 'deciduous forest', [lai 1, cc 0.5, hcan 8]
    42: 'evergreen forest', [lai 4.5, cc 0.7, hcan 15]
    43: 'mixed forest',  [lai 4, cc 0.8, hcan 10]
    52: 'shrub', [lai 1, cc 0.5, hcan 3]
    71: 'grasslands', [lai0]
    81: 'pasture',[lai0]
    82: 'cultivated crops', [lai0]
    90: 'woody wetlands', [lai0]
    95: 'emergent herbaceous wetlands',
}   # https://www.mrlc.gov/nlcd11_stat.php
"""


import os
import csv

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import gdalnumeric


# user settings  ####################################################################################################
watershed = 'McPhee'
folder_name = '{}_sublimation_analysis'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
stats_folder = os.path.join(result_folder, 'stats_folder')

terrain_folder = '/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/Sublimation_analysis/terrain/'
dem_file = os.path.join(terrain_folder, 'McPhee_dem_watershed_clip.tif')
lai_file = os.path.join(terrain_folder, 'ueb_lai.tif')
cc_file = os.path.join(terrain_folder, 'ueb_cc.tif')
aspect_file = os.path.join(terrain_folder, 'ueb_aspect.tif')

var_dict = {'ueb_Ec': 'canopy subilmation (mm)',
            'ueb_Es': 'ground sublimation (mm)',
            'uebPrec': 'precipitation (mm)',
            'ueb_tet': 'ET (mm)',
            'ueb_rmlt': 'rain plus melt (mm)',
            'total_sub': 'total sublimation (mm)',
            'water_loss': 'water loss (%)',
            }  # this needs to be the same as the tif_df.csv column name


# step 1 calculate land type sublimation water loss ##########################################
# create masks and calculate forest percentage
cc_array = gdalnumeric.LoadFile(os.path.join(terrain_folder, 'ueb_cc.tif'))
forest_area = (cc_array > 0.0)
open_area = (cc_array == 0.0)

forest_cover_info = {
    'forest pixels': forest_area.sum(),
    'open pixels': open_area.sum(),
    'forest_cover (%)': forest_area.sum()*100.0 / (forest_area.sum() + open_area.sum())
}

with open(os.path.join(stats_folder, 'forest_cover.csv'),'w') as f:
    writer = csv.writer(f)
    writer.writerows(forest_cover_info.items())

mask_dict = {
    'open': ~(cc_array == 0.0),
    'forest':  ~(cc_array > 0.0)
}

# calculate land type average
land_type_df = pd.DataFrame(index=mask_dict.keys())
for var in var_dict.keys():
    var_mean_path = os.path.join(stats_folder, 'annual_mean_{}.tif'.format(var))
    if os.path.isfile(var_mean_path):
        var_sum_array = gdalnumeric.LoadFile(var_mean_path)
        land_type_df[var] = np.nan
        for index, mask in mask_dict.items():
            mask_array = np.ma.array(var_sum_array, mask=mask)
            land_type_df[var].ix[index] = round(mask_array.mean(), 3)

land_type_df['water_loss_cal'] = 100 * land_type_df['total_sub'] / land_type_df['uebPrec']
land_type_df.to_csv(os.path.join(stats_folder, 'land_type_df_new.csv'))

# make bar plot for comparison
fig, ax = plt.subplots(figsize=(10, 6))
land_type_df[['uebPrec']].plot.bar(ax=ax, position=1, width=.2)
land_type_df[['ueb_Es', 'ueb_Ec']].plot.bar(ax=ax, position=0, width=.2, stacked=True, color=['orange', 'green'], rot=0)
for x, y, water_loss in zip([0.0, 1.0], land_type_df['total_sub'], land_type_df['water_loss_cal']):
    ax.text(x, y+3,'{}%'.format(round(water_loss, 2)))
ax.legend(['precipitation', 'ground sublimation', 'canopy sublimation'], loc='best')
ax.set_ylabel('water input/output (mm)')
fig.savefig(os.path.join(stats_folder, 'land_type_sub_bar.png'))


# step 2 elevation and Lai vs total sublimation ############################################################
# create index for land type
lai_array = gdalnumeric.LoadFile(lai_file)
forest_area_1 = (lai_array <= 1.0)
forest_area_2 = (lai_array > 1.0)
open_area = (lai_array == 0.0)

dem_array = gdalnumeric.LoadFile(dem_file)
dem_area = (dem_array[0] > 0)

forest_index_1 = (dem_area & forest_area_1)
forest_index_2 = (dem_area & forest_area_2)
open_index = (dem_area & open_area)

# create scatter plot for var vs elevation
for var, units in var_dict.items():
    var_mean_path = os.path.join(stats_folder, 'annual_mean_{}.tif'.format(var))
    if os.path.isfile(var_mean_path):
        var_sum_array = gdalnumeric.LoadFile(var_mean_path)
        fig, ax = plt.subplots(figsize=(8, 6))
        for index_array in [forest_index_1, forest_index_2, open_index]:
            index = index_array.flatten()
            dem_1d = dem_array[0].flatten()
            var_1d = var_sum_array.flatten()

            dem_values = dem_1d[index]
            var_values = var_1d[index]

            ax.plot(dem_values.tolist(), var_values.tolist(), 'o')
            ax.set_xlabel('Elevation(m)')
            ax.set_ylabel(units)
            ax.legend(['Lai<=1.0', 'Lai>1.0', 'Lai=0'])

        fig.savefig(os.path.join(stats_folder, 'scatter_{}.png'.format(var)))

print 'sublimation_analysis_5: land type sublimation analysis is done'




