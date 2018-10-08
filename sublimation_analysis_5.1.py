"""
This is the 1st version sublimation analysis

step5.1: use terrain data to calculate sublimation stats
         step5 is calculating for land type stats based on all years data stacked together and get the annual mean
         step5.1 is calculating for land type stats based on each year data stacked together and get the annual mean and SEM

requirement:
- terrain tif of lai, dem, cc


results:
- bar plot: open/forest land type sublimation components compare


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

start_year = 1989  # year for start date 1989-10-01
end_year = 2009   # year for end date 2009-9-30

terrain_folder = '/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/Sublimation_analysis/analysis_22yr/terrain/'
lai_file = os.path.join(terrain_folder, 'ueb_lai.tif')

var_dict = {'ueb_Ec': 'canopy subilmation (mm)',
            'ueb_Es': 'ground sublimation (mm)',
            'uebPrec': 'precipitation (mm)',
            'ueb_tet': 'ET (mm)',
            'ueb_rmlt': 'rain plus melt (mm)',
            'total_sub': 'total sublimation (mm)',
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

df_dict = {
    'open': pd.DataFrame(columns=var_dict.keys(), index=range(start_year, end_year)),
    'forest': pd.DataFrame(columns=var_dict.keys(), index=range(start_year, end_year)),
}

# calculate land type average for each year
for year in range(start_year, end_year):
    for var in var_dict.keys():
        var_sum_path = os.path.join(stats_folder, 'sum_{}_{}.tif'.format(var, year))
        if os.path.isfile(var_sum_path):
            var_sum_array = gdalnumeric.LoadFile(var_sum_path)
            for land_type, mask in mask_dict.items():
                mask_array = np.ma.array(var_sum_array, mask=mask)
                df_dict[land_type][var].ix[year] = round(mask_array.mean(), 3)


# calculate the df stats
for land_type, df in df_dict.items():
    df['water_loss'] = 100 * df['total_sub'] / df['uebPrec']
    year_index = df.index
    df.ix['sum'] = df.ix[year_index].sum()
    df.ix['mean'] = df.ix[year_index].mean()
    df.ix['sem'] = df.ix[year_index].sem()
    df.to_csv(os.path.join(stats_folder, '{}_df.csv'.format(land_type)))

# make bar plot
prec = [df_dict['forest'].ix['mean']['uebPrec'], df_dict['open'].ix['mean']['uebPrec']]
total_prec_err = [df_dict['forest'].ix['sem']['uebPrec'], df_dict['open'].ix['sem']['uebPrec']]

Ec = [df_dict['forest'].ix['mean']['ueb_Ec'], df_dict['open'].ix['mean']['ueb_Ec']]
Es = [df_dict['forest'].ix['mean']['ueb_Es'], df_dict['open'].ix['mean']['ueb_Es']]
total_ET_err = [df_dict['forest'].ix['sem']['total_sub'], df_dict['open'].ix['sem']['total_sub']]
total_ET = [df_dict['forest'].ix['mean']['total_sub'], df_dict['open'].ix['mean']['total_sub']]

water_loss = []
for land_type in ['forest', 'open']:
    water_loss.append(round(100*df_dict[land_type].ix['mean']['total_sub'] / df_dict[land_type].ix['mean']['uebPrec'], 2))


plt.figure(figsize=(8, 6))
ind = [1, 2]
width = .2
left_bar = [x - width / 2 for x in ind]
right_bar = [x + width / 2 for x in ind]

p1 = plt.bar(left_bar, prec, width=width, color='dodgerblue',yerr=total_prec_err)
p3 = plt.bar(right_bar, Es, width=width, color='orange')
p4 = plt.bar(right_bar, Ec, width=width, bottom=Es, color='palegreen', yerr=total_ET_err)

for x, y1, y2, water_loss in zip(right_bar, total_ET, total_ET_err, water_loss):
    plt.text(x, y1+y2+3, '{}%'.format(round(water_loss, 2)))

plt.xticks(ind, ('Forest', 'Open'))
plt.ylabel('water input/output (mm)')
plt.legend((p1[0], p3[0], p4[0]),
           ('Precipitation', 'ground sublimation', 'canopy sublimation'))
plt.savefig(os.path.join(stats_folder, 'land_type_sub_bar.png'))

print 'sublimation_analysis_5.1: land type sublimation analysis is done'




