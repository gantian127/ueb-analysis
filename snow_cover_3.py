"""
This is the formal script for snow cover area analysis

step3:  calculate cloud cover -> get valid modis and swe data to create binary files

step:
- calculate cloud cover and snow grid count for modis
- get valid snow date: snow17, ueb or modis has snow (>0m or 0%) and modis cloud cover less than threshold
- create swe binary
- create modis binary

"""

import os
import subprocess
import shlex
import numpy as np
import shutil

import pandas as pd
import gdalnumeric
from snow_cover_utility import array_to_raster


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
snow_date['modis_snow_count'] = ''

# calculate the modis cloud cover and check whether it has snow
for time in snow_date.index:
    modis_proj_path = snow_date['modis_proj_folder'].ix[time]
    if os.path.isfile(modis_proj_path):
        try:
            raster = gdalnumeric.LoadFile(modis_proj_path)
            cloud_count = (raster[0] == 250).sum()
            total_count = raster.shape[1] * raster.shape[2]
            nodata_count = (raster[0] == 255).sum()
            snow_count = ((raster[0] >= modis_threshold) & (raster[0] <= 100)).sum()
            cloud_cover = float(cloud_count) / (total_count - nodata_count)
            snow_date['modis_cloud_cover'].ix[time] = cloud_cover
            snow_date['modis_snow_count'].ix[time] = snow_count
        except Exception as e:
            continue

snow_date.to_csv(model_snow_date_path)


# step2: get valid date #######################################################################
# this is to find the date that snow17, ueb or modis has snow (>0m or 0%) and modis cloud cover less than threshold
print ' step 2 get valid date'
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)
modis_date = snow_date[(snow_date['modis_snow_count'] > 0)].index

for model_swe in ['snow17_swe', 'ueb_swe']:
    if model_swe in snow_date.columns:
        swe_date = snow_date[snow_date[model_swe] > 0].index
        modis_date = modis_date.union(swe_date)

valid_date = snow_date.ix[modis_date][snow_date['modis_cloud_cover'] <= cloud_threshold]

valid_date.to_csv(valid_date_path)


# step3: create binary grid ##############################################################
print 'step3 create swe binary'

# load data
valid_date = pd.DataFrame.from_csv(valid_date_path, header=0)

# create swe binary file
swe_func = '(A>={})'.format(swe_threshold)

for swe_proj_folder in swe_proj_folders:
    if os.path.isdir(swe_proj_folder):
        # create dataframe column and folder
        proj_col_name = os.path.basename(swe_proj_folder)
        bin_col_name = proj_col_name.replace('proj', 'bin')
        valid_date[bin_col_name] = 'invalid'
        swe_bin_folder = os.path.join(result_folder, bin_col_name)
        if not os.path.isdir(swe_bin_folder):
            os.mkdir(swe_bin_folder)

        # create binary file if the file is not created
        for time in valid_date.index:
            swe_proj_path = valid_date[proj_col_name].ix[time]
            if os.path.isfile(swe_proj_path):
                swe_bin_name = os.path.basename(swe_proj_path).replace('_proj', '_bin')
                swe_bin_path = os.path.join(swe_bin_folder, swe_bin_name)
                if not os.path.isfile(swe_bin_path):
                    cmd_swe_bin = 'gdal_calc.py -A {} --calc="{}" --outfile={} --NoDataValue=-999 --type=Int16'.format(swe_proj_path, swe_func, swe_bin_path)
                    try:
                        subprocess.call(shlex.split(cmd_swe_bin))
                        valid_date[bin_col_name].ix[time] = swe_bin_path
                    except Exception as e:
                        continue
                else:
                    valid_date[bin_col_name].ix[time] = swe_bin_path

        valid_date.to_csv(valid_date_path)


# step4  create modis binary file  ##################################################################################
print 'step4 create modis bianry file'

valid_date = pd.DataFrame.from_csv(valid_date_path, header=0)

# load data
if os.path.isdir(modis_proj_folder):
    # create dataframe column and folder
    bin_col_name = 'modis_bin_folder'
    valid_date[bin_col_name] = 'invalid'
    modis_bin_folder = os.path.join(result_folder, bin_col_name)
    if not os.path.isdir(modis_bin_folder):
        os.mkdir(modis_bin_folder)

    # create binary file
    modis_func = '((A>={})*(A<=100)+-999*(A==250))'.format(modis_threshold)  # when there is cloud, assign as no data values
    for time in valid_date.index:
        modis_proj_path = valid_date['modis_proj_folder'].ix[time]
        if os.path.isfile(modis_proj_path):
            modis_bin_name = os.path.basename(modis_proj_path).replace('_clip', '_bin')
            modis_bin_path = os.path.join(modis_bin_folder, modis_bin_name)

            if not os.path.isfile(modis_bin_path):
                cmd_modis_bin = 'gdal_calc.py -A {} --calc="{}" --outfile={} --NoDataValue=-999 --type=Int16'.format(modis_proj_path, modis_func, modis_bin_path)
                try:
                    subprocess.call(shlex.split(cmd_modis_bin))
                    valid_date[bin_col_name].ix[time] = modis_bin_path
                except Exception as e:
                    continue

                # fill cloud cover area by interpolation
                modis_proj_array = gdalnumeric.LoadFile(modis_proj_path)
                cloud_cover_pixel = (modis_proj_array[0] == 250).sum()
                if cloud_cover_pixel > 0:

                    for i in range(10):
                        cmd_interp_bin = 'gdal_fillnodata.py -md 2 {} {}'.format(modis_bin_path, modis_bin_path)

                        try:
                            subprocess.call(shlex.split(cmd_interp_bin))
                        except Exception as e:
                            valid_date[bin_col_name].ix[time] = ''
                            continue

                        modis_bin_array = gdalnumeric.LoadFile(modis_bin_path)
                        mask = np.ma.masked_where(modis_proj_array[1] == 0, modis_bin_array)  # remember to use the proj tif 2nd layer as the mask for binary tif creation
                        cloud_cover_pixel = (mask == -999).sum()
                        if cloud_cover_pixel == 0:
                            break

                    if cloud_cover_pixel > 0:
                        valid_date.drop(time)
                        print 'drop bin file at {}'.format(modis_bin_path)
                    else:
                        print modis_bin_path
                        print os.path.isfile(modis_bin_path)
                        os.remove(modis_bin_path)
                        new_bin_array = np.where(modis_proj_array[1] != 0, modis_bin_array, -999)
                        array_to_raster(output_path=modis_bin_path,
                                        source_path=modis_proj_path,
                                        array_data=new_bin_array)
                        print 'cloud cover interpolation for {}'.format(modis_bin_path)

            else:
                valid_date[bin_col_name].ix[time] = modis_bin_path

    valid_date.to_csv(valid_date_path)

else:
    print 'failed to create modis binary file'

print 'snow_cover_3: swe and modis binary file is done'