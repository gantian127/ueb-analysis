"""
This is the formal script for snow cover area analysis

step3: get valid modis data and create processing binary files

step:
- calculate cloud cover
- create swe binary
- create modis binary

"""

import os
import subprocess
import shlex
import numpy as np

import pandas as pd
import gdalnumeric


# default user settings apply to all steps ####################################################
# folders/files created by step 2 script
watershed = 'animas'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')
modis_proj_folder = os.path.join(result_folder, 'modis_proj_folder')
swe_proj_folders = [os.path.join(result_folder, name) for name in ['snow17_proj_folder', 'ueb_proj_folder']]

# threshold for processing
swe_threshold = 10  # mm
modis_threshold = 50  # %
cloud_threshold = 0.1  # *100 percent

# new csv file path
stats_folder = os.path.join(result_folder,'stats_folder')
if not os.path.isdir(stats_folder):
    os.mkdir(stats_folder)
valid_date_path = os.path.join(stats_folder, 'valid_date.csv')


# step1: calculate cloud cover ##############################################################
print 'step1: calculate cloud cover '

# load data
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)
snow_date['modis_cloud_cover'] = ''

# calculate the modis cloud cover
for time in snow_date.index:
    modis_proj_path = snow_date['modis_proj_folder'].ix[time]
    if os.path.isfile(modis_proj_path):
        try:
            raster = gdalnumeric.LoadFile(modis_proj_path)
            cloud_count = (raster[0] == 250).sum()
            total_count = raster.shape[1] * raster.shape[2]
            nodata_count = (raster[0] == 255).sum()
            cloud_cover = float(cloud_count) / (total_count - nodata_count)
            snow_date['modis_cloud_cover'].ix[time] = cloud_cover

        except Exception as e:
            continue

snow_date.to_csv(model_snow_date_path)
print 'cloud cover calculation is done'




# get valid date #######################################################################
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)
valid_date = snow_date[snow_date['modis_cloud_cover'] <= cloud_threshold]
valid_date.to_csv(valid_date_path)


# step2: create binary grid ##############################################################
print 'step2 create swe binary'

# load data
valid_date = pd.DataFrame.from_csv(valid_date_path, header=0)

# create swe binary file
swe_func = '(A>={})'.format(swe_threshold)

for swe_proj_folder in swe_proj_folders:
    if os.path.isdir(swe_proj_folder):
        # create dataframe column and folder
        proj_col_name = os.path.basename(swe_proj_folder)
        bin_col_name = proj_col_name.replace('proj', 'bin')
        valid_date[bin_col_name] = ''
        swe_bin_folder = os.path.join(result_folder, bin_col_name)
        if not os.path.isdir(swe_bin_folder):
            os.mkdir(swe_bin_folder)

        for time in valid_date.index:
            swe_proj_path =valid_date[proj_col_name].ix[time]
            swe_bin_name = os.path.basename(swe_proj_path).replace('_proj', '_bin')
            swe_bin_path = os.path.join(swe_bin_folder, swe_bin_name)
            cmd_swe_bin = 'gdal_calc.py -A {} --calc="{}" --outfile={} --NoDataValue=-999 --type=Int16'.format(swe_proj_path, swe_func, swe_bin_path)

            try:
                subprocess.call(shlex.split(cmd_swe_bin))
                valid_date[bin_col_name].ix[time] = swe_bin_path
            except Exception as e:
                continue

        valid_date.to_csv(valid_date_path)

print 'swe binary file is done'


# step3  create modis binary file  ##################################################################################
print 'step3 create modis bianry file'

valid_date = pd.DataFrame.from_csv(valid_date_path, header=0)

# load data
if os.path.isdir(modis_proj_folder):
    # create dataframe column and folder
    bin_col_name = 'modis_bin_folder'
    valid_date[bin_col_name] = ''
    modis_bin_folder = os.path.join(result_folder, bin_col_name)
    if not os.path.isdir(modis_bin_folder):
        os.mkdir(modis_bin_folder)

    # create binary file
    modis_func = '((A>={})*(A<=100)+-999*(A==250))'.format(modis_threshold)  # when there is cloud, assign as no data values
    for time in valid_date.index:
        modis_proj_path = valid_date['modis_proj_folder'].ix[time]
        modis_bin_name = os.path.basename(modis_proj_path).replace('_proj', '_bin')
        modis_bin_path = os.path.join(modis_bin_folder, modis_bin_name)
        cmd_modis_bin = 'gdal_calc.py -A {} --calc="{}" --outfile={} --NoDataValue=-999 --type=Int16'.format(modis_proj_path, modis_func, modis_bin_path)

        try:
            subprocess.call(shlex.split(cmd_modis_bin))
            valid_date[bin_col_name].ix[time] = modis_bin_path
        except Exception as e:
            continue

    valid_date.to_csv(valid_date_path)
    print 'modis binary file is done'

else:
    print 'failed to create modis binary file'