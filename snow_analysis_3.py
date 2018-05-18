"""
This is the 3rd version formal script for snow cover area analysis

step3:  use project tif files get binary files and calculate stats and make analysis plots

requirements:
- matplotlib version 2.1.2
- pandas version 0.22.0

step:
- create binary array for modis and swe, count the different pixels
- calculate the stats based on the pixel count:
  a) valid date stats
  b) monthly stats and plots
  c) annual stats and plots

"""

import os
import gdalnumeric
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar

# default user settings apply to all steps ####################################################
# folders/files created by step 2 script
watershed = 'MPHC2'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')
modis_proj_folder = os.path.join(result_folder, 'modis_proj_folder')
swe_proj_folders = [os.path.join(result_folder, name) for name in ['snow17_proj_folder', 'ueb_proj_folder']]

# threshold for processing
swe_threshold = 1  # mm

# time for analysis:
start_time = '2000/10/01'
end_time = '2010/06/30'

# new csv file path
stats_folder = os.path.join(result_folder, 'stats_folder')
if not os.path.isdir(stats_folder):
    os.mkdir(stats_folder)

stat_result_path = os.path.join(stats_folder, 'stat_result.csv')

plt.ioff()

# step1: get binary array and count pixel count ##############################################################
print 'step1: calculate pixel count '

# load data
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)
df_col_name = ['watershed', 'watershed_out', 'invalid', 'cloud',
               'modis_snow', 'modis_dry','swe_snow', 'swe_dry', 'A', 'B', 'C', 'D','weight']

for swe_proj_folder in swe_proj_folders:
    swe_col_name = os.path.basename(swe_proj_folder)

    if os.path.isdir(swe_proj_folder) and os.path.isdir(modis_proj_folder):
        # initiate data frame
        pixel_count = pd.DataFrame(index=snow_date.index, columns=df_col_name)
        pixel_count_path = os.path.join(stats_folder, 'pixel_count_{}.csv'.format(swe_col_name.split('_')[0]))

        # get pixel count
        for time in snow_date.index:
            modis_proj_path = os.path.join(modis_proj_folder, snow_date['modis_proj_folder'].ix[time])
            swe_proj_path = os.path.join(swe_proj_folder, snow_date[swe_col_name].ix[time])

            if os.path.isfile(swe_proj_path) and os.path.isfile(modis_proj_path):
                try:
                    # count watershed, watershed_out, invalid pixels
                    modis = gdalnumeric.LoadFile(modis_proj_path)
                    modis_bin = np.where(modis[1] != 0, modis[0], -999)
                    count_watershed = (modis[1] == 255).sum()
                    count_watershed_out = (modis[1] == 0).sum()
                    count_invalid = (modis_bin > 100).sum()
                    count_cloud = (modis_bin == 250).sum()

                    # get moids binary
                    modis_bin[modis_bin > 100] = -999
                    modis_bin[modis_bin > 0] = 1

                    # count modis snow, no snow pixels
                    count_modis_snow = (modis_bin == 1).sum()
                    count_modis_dry = (modis_bin == 0).sum()

                    # calculate weight
                    weight = float(count_modis_dry+count_modis_snow)/(count_invalid+count_modis_dry+count_modis_snow)

                    # get swe binary
                    swe = gdalnumeric.LoadFile(swe_proj_path)
                    swe_bin = np.where(modis_bin != -999, swe, -999)
                    swe_bin[swe_bin >= swe_threshold] = 1
                    swe_bin[(swe_bin >= 0) & (swe_bin < swe_threshold)] = 0

                    # count swe snow, no snow pixels
                    count_swe_snow = (swe_bin == 1).sum()
                    count_swe_dry = (swe_bin == 0).sum()

                    # compare swe_bin and modis_bin: count A(dry,dry), B(dry,snow), C(snow,dry), D(snow,snow)
                    compare_cd = np.where(swe_bin == 1, modis_bin, 999)
                    compare_ab = np.where(swe_bin == 0, modis_bin, 999)
                    a = (compare_ab == 0).sum()
                    b = (compare_ab == 1).sum()
                    c = (compare_cd == 0).sum()
                    d = (compare_cd == 1).sum()

                    # assign to dataframe
                    pixel_count.at[time, df_col_name] = [
                     count_watershed, count_watershed_out, count_invalid, count_cloud,
                     count_modis_snow, count_modis_dry,
                     count_swe_snow, count_swe_dry, a, b, c, d, round(weight, 4),
                    ]

                except Exception as e:
                    pixel_count.drop(index=time, inplace=True)
                    print 'fail at pixel count {}'.format(time)
                    continue
            else:
                pixel_count.drop(index=time, inplace=True)
                print 'invalid project tif file path at {}'.format(time)

        pixel_count.to_csv(pixel_count_path)

print 'snow_analysis_3: pixel count is finished'
