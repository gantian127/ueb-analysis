"""
This is the formal script for snow cover area analysis

step4: get valid modis data and create processing binary files

step:
- calculate area based stats
- calculate pixel based stats

"""

import os
import numpy as np
import json

from matplotlib import pyplot as plt
import pandas as pd
import gdalnumeric

from snow_cover_utility import get_statistics



# default user settings apply to all steps ####################################################
# folders/files created by step 2 script
watershed = 'animas'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
modis_bin_folder = os.path.join(result_folder, 'modis_bin_folder')
swe_bin_folders = [os.path.join(result_folder, name) for name in ['snow17_bin_folder', 'ueb_bin_folder']]
valid_date_path = os.path.join(result_folder, 'valid_date.csv')


# step 1 calculate area stats ################################################
print 'step1: calculate area stats'

# calculate area based stats
valid_date = pd.DataFrame.from_csv(valid_date_path, header=0)
cal_folders = [swe_bin_folders[0], swe_bin_folders[1], modis_bin_folder]

for bin_folder in cal_folders:
    if os.path.isdir(bin_folder):
        bin_col_name = os.path.basename(bin_folder)
        area_stats = pd.DataFrame(columns=['time', 'file', 'snow', 'no_snow', 'no_data', 'percent_snow'])
        percent_col_name = 'percent_snow_' + bin_col_name
        valid_date[percent_col_name] = np.nan
        i = 0
        for time in valid_date.index:
            i += 1
            bin_path = valid_date[bin_col_name].ix[time]
            try:
                raster = gdalnumeric.LoadFile(bin_path)
                snow_count = (raster == 1).sum()
                nosnow_count = (raster == 0).sum()
                nodata_count = (raster == -999).sum()
                percent_snow = float(snow_count)/(nosnow_count+snow_count)
                area_stats.loc[i] = [time, bin_path, snow_count, nosnow_count,  nodata_count, percent_snow]
                valid_date[percent_col_name].ix[time] = percent_snow

            except Exception as e:
                area_stats.loc[i] = [time, bin_path, None, None, None, None]
                continue

        area_stats.to_csv(os.path.join(result_folder, '{}_area_stats.csv'.format(bin_col_name)))
        valid_date.to_csv(valid_date_path)

# TODO need to export as text.
result = []
for bin_folder in swe_bin_folders:
    if os.path.isdir(bin_folder):
        bin_col_name = os.path.basename(bin_folder)
        stats_result = get_statistics(valid_date['percent_snow_'+bin_col_name], valid_date['percent_snow_modis_bin_folder'])
        result.append(bin_col_name+json.dumps(stats_result))

with open(os.path.join(result_folder,'area_stat_results.txt'),'w') as f:
    for item in result:
        f.write("%s\n" % item)

print 'area stats is done'


# step 2: calculate pixel based stats #########################################

valid_date = pd.DataFrame.from_csv(valid_date_path, header=0)

for swe_bin_folder in swe_bin_folders:
    swe_bin_col = os.path.basename(swe_bin_folder)
    layer_stack = []
    if os.path.isdir(swe_bin_folder):
        # get compare grid layers
        for time in valid_date.index:
            swe_bin_path = valid_date[swe_bin_col].ix[time]
            modis_bin_path = valid_date['modis_bin_folder'].ix[time]
            if os.path.isfile(swe_bin_path) and os.path.isfile(modis_bin_path):
                raster_obs = gdalnumeric.LoadFile(modis_bin_path)
                raster_model = gdalnumeric.LoadFile(swe_bin_path)

                obs = np.where(raster_obs != -999, raster_obs, np.nan)
                model = np.where(raster_model != -999, raster_model, np.nan)
                compare = obs-model  # 0 means true, 1 means false, -1 means false
                layer_stack.append(compare)

        # stack layers and calculate oa values
        nan_mask = np.isnan(model)
        all_stack = np.stack(layer_stack)
        missing_data = np.where(nan_mask == False, np.isnan(all_stack).sum(axis=0), np.nan)
        mismatch_data = np.where(nan_mask == False, np.nansum(abs(all_stack), axis=0), np.nan)
        oa_data = 1 - mismatch_data.astype('float32') / (all_stack.shape[0]-missing_data)

        result = {
            'oa': oa_data,
            'missing': missing_data,
            'mismatch': mismatch_data,
            'all_stack': all_stack
        }

        for name, data in result.items():
            file_path = os.path.join(result_folder, '{}_{}'.format(name, swe_bin_col))
            np.save(file_path, data)

            if name != 'all_stack':
                fig = plt.imshow(data, interpolation='nearest')
                plt.colorbar()
                plt.title('plot of {}'.format(name))
                plt.savefig(file_path+'.png')
                plt.clf()


print 'oa calculate is done'
