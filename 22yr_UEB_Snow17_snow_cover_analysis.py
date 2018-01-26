"""
This is aimed to process the snow output and analyze the snow cover area results
see detailed logic in project plan folder ppt

- This file is mainly for testing. See other files to get the code for production procedure
- create a result folder and put the code under this folder
"""

import subprocess
import gzip
import os
import shlex
import pandas as pd
import shutil
import numpy as np
import gdalnumeric
import gdal
from plot_SAC_utility import get_statistics

# default user settings apply to all steps ####################################################
result_folder = r'/Projects/Tian_workspace/snow_analysis_test/snow_analysis_result/'
model_snow_date_path = './model_snow_date.csv'

# Step 0 get model snow date info #########################################
# user settings
from plot_SAC_utility import get_sim_dataframe
swe_ts_snow17 = 'DRGC2_we_snow17.ts'
swe_ts_ueb = 'DRGC2_we_ueb.ts'
snow_threshold = 10
start_time = '2006-10-01'
end_time = '2007-9-30'

# get date of snow for both models
snow17_df = get_sim_dataframe(swe_ts_snow17, sim_skip=136, start_time=start_time, end_time=end_time)
ueb_df = get_sim_dataframe(swe_ts_ueb, sim_skip=136, start_time=start_time, end_time=end_time)
snow17_snow_date = snow17_df[snow17_df >= snow_threshold]
ueb_snow_date = ueb_df[ueb_df >= snow_threshold]
snow_date = pd.concat([snow17_snow_date, ueb_snow_date], axis=1)
snow_date.columns = ['snow17_swe', 'ueb_swe']
snow_date.to_csv('./model_snow_date.csv')



# # step 1 get modis and swe data based on snow date #################################################
print 'step1: get modis and swe data with snow'
# user settings
result_folder = r'/Projects/Tian_workspace/snow_analysis_test/snow_analysis_result/'
model_snow_date_path = './model_snow_date.csv'

modis_gz_folder = r'/Projects/snow_fraction/'  # this is the folder that stores the original .gz data
swe_gz_folders = [
    r'/Projects/Tian_workspace/snow_analysis_test/WY2007/',  # snow17 swe xmrg .gz folder
    # 'ueb_folder',  # ueb swe xmrg .gz folder
]

modis_tif_folder = os.path.join(result_folder, 'modis_tif_folder')  #  folder that stores the modis with snow
swe_tif_folders = [os.path.join(result_folder, name) for name in ['snow17_tif_folder', 'ueb_tif_folder']]  # folder that stores swe tif with snow


# create tif folder:
swe_tif_folders.append(modis_tif_folder)
for folder in swe_tif_folders:
    if not os.path.isdir(folder):
        os.mkdir(folder)


# load snow date record
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)


# modis: unzip .gz file to assigned folder
col_name = os.path.basename(modis_tif_folder)
snow_date[col_name] = ''
for time in snow_date.index:
    year = str(time.year)
    day = '{:03d}'.format(time.dayofyear)
    gz_name = 'modscag.snow_fraction.{}.{}.mosaic.tif.gz'.format(year, day)
    gz_path = os.path.join(modis_gz_folder, year, day, gz_name)
    modis_tif_path = os.path.join(modis_tif_folder, gz_name[:-3])

    try:
        with gzip.open(gz_path, 'rb') as inf:
            with open(modis_tif_path, 'wb') as outf:
                content = inf.read()
                outf.write(content)
        snow_date[col_name].ix[time] = modis_tif_path
    except Exception as e:
        continue

print 'unzip modis .gz is done'


# model swe: unzip .gz file to assigned folder
for i in range(0, len(swe_gz_folders)):
    swe_gz_folder = swe_gz_folders[i]
    swe_tif_folder = swe_tif_folders[i]
    col_name = os.path.basename(swe_tif_folder)
    snow_date[col_name] = ''

    for time in snow_date.index:
        swe_gz_name = 'we{}06z.gz'.format(time.strftime('%m%d%Y'))
        swe_gz_path = os.path.join(swe_gz_folder, swe_gz_name)
        swe_tif_path = os.path.join(swe_tif_folder, swe_gz_name[:-3])
        try:
            with gzip.open(swe_gz_path, 'rb') as inf:
                with open(swe_tif_path, 'wb') as outf:
                    content = inf.read()
                    outf.write(content)
            snow_date[col_name].ix[time] = swe_tif_path
        except Exception as e:
            continue

print 'unzip swe .gz is done'

snow_date.to_csv(model_snow_date_path)



# # Step 2 data with same projection/resolution ##############################################

print 'step2 : convert swe xmrg as tif and reproject, reproject and resample modis'
# user settings
result_folder = r'/Projects/Tian_workspace/snow_analysis_test/snow_analysis_result/'
model_snow_date_path = './model_snow_date.csv'

modis_tif_folder = os.path.join(result_folder, 'modis_tif_folder')  #  folder that stores the modis with snow
swe_tif_folders = [os.path.join(result_folder, name) for name in ['snow17_tif_folder',
                                                                  # 'ueb_tif_folder'
                                                                  ]]  # folder that stores swe tif with snow

proj4_string = '+proj=stere +lat_0=90.0 +lat_ts=60.0 +lon_0=-105.0 +k=1 +x_0=0.0 +y_0=0.0 +a=6371200 +b=6371200 +units=m +no_defs'  # polar stereographic


# # load snow date info
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)

# model swe: xmrg -> to asc -> define coordinates
for swe_tif_path in swe_tif_folders :
    xmrg_col_name = os.path.basename(swe_tif_path)
    proj_col_name = os.path.basename(swe_tif_path)+'_proj'
    snow_date[proj_col_name] = ''

    for time in snow_date.index:
        swe_xmrg_path = snow_date[xmrg_col_name].ix[time]
        if os.path.isfile(swe_xmrg_path):
            swe_tif_path = swe_xmrg_path+'.asc'
            swe_proj_path = swe_xmrg_path+'_proj.asc'
            cmd_xmrgtoasc = 'xmrgtoasc -i {} -p ster -n -999'.format(swe_xmrg_path)
            cmd_reproj = 'gdalwarp -overwrite -t_srs "{}" {} {}'.format(proj4_string, swe_tif_path, swe_proj_path)

            # print cmd_xmrgtoasc, cmd_reproj
            try:
                for command in [cmd_xmrgtoasc, cmd_reproj]:
                    result1 = subprocess.call(shlex.split(command))
                snow_date[proj_col_name].ix[time] = swe_proj_path
            except Exception as e:
                continue

    snow_date.to_csv(model_snow_date_path)
print 'swe xmrg reprojection is done'



# ## modis sca: reproject -> clip -> resample
# # create a template clip shape file:
swe_proj_path = '/Projects/Tian_workspace/snow_analysis_test/snow_analysis_result/snow17_tif_folder/we0101200706z_proj.asc'
swe_template = gdal.Open(swe_proj_path )  # provide a path that is the projected swe tif file
x_size = swe_template.RasterXSize
y_size = swe_template.RasterYSize
swe_template = None

clipper_file_path = os.path.join(modis_tif_folder, 'modis_clipper.shp')
cmd_clipper = "gdal_polygonize.py {} -f 'ESRI Shapefile' {}".format(swe_proj_path, clipper_file_path)
subprocess.call(shlex.split(cmd_clipper))


# reprojection and clip
# x_size = 47
# y_size = 73
tif_col_name = os.path.basename(modis_tif_folder)
proj_col_name = tif_col_name+'_proj'
snow_date[proj_col_name] = ''

for time in snow_date.index:
    modis_tif_path = snow_date[tif_col_name].ix[time]
    if os.path.isfile(modis_tif_path):
        modis_proj_path = modis_tif_path[:-4]+'_proj.tif'
        modis_clip_path = modis_tif_path[:-4]+'_clip.tif'
        cmd_reproj = 'gdalwarp -overwrite -t_srs "{}" -tr 463 463 {} {}'.format(proj4_string, modis_tif_path, modis_proj_path)
        cmd_clip = "gdalwarp -overwrite -ts {} {} -cutline {} -crop_to_cutline -dstalpha {} {}".format(x_size, y_size, clipper_file_path, modis_proj_path, modis_clip_path)

        try:
            for command in [cmd_reproj, cmd_clip]:
                subprocess.call(shlex.split(command))
            snow_date[proj_col_name].ix[time] = modis_clip_path

        except Exception as e:
            continue

snow_date.to_csv(model_snow_date_path)

print 'modis reprojection, clip, resample is done'



# ## step3: calculate cloud cover ##############################################################
print 'step3: process binary file and calculate stats'
# user settings
result_folder = r'/Projects/Tian_workspace/snow_analysis_test/snow_analysis_result/'
model_snow_date_path = './model_snow_date.csv'


# load data
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)
snow_date['modis_cloud_cover'] = np.nan

# calculate the modis cloud cover
for time in snow_date.index:
    modis_proj_path = snow_date['modis_tif_folder_proj'].ix[time]
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



# ## step4: create binary grid ##############################################################
# user settings
cloud_threshold = 0.1
model_list = ['snow17']
swe_threshold = 10
modis_threshold = 50

# load data
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)
valid_date = snow_date[snow_date['modis_cloud_cover'] <= cloud_threshold]

# create swe binary file
swe_func = '(A>={})'.format(swe_threshold)
for model in model_list:
    swe_bin_folder = os.path.join(result_folder, '{}_bin_folder'.format(model))
    if not os.path.isdir(swe_bin_folder):
        os.mkdir(swe_bin_folder)

    col_name = '{}_bin'.format(model)
    valid_date[col_name] = np.nan

    for time in valid_date.index:
        swe_proj_path =valid_date['{}_tif_folder'.format(model)].ix[time]+'_proj.asc' #TODO remember to change column and file name
        swe_bin_name = os.path.basename(swe_proj_path).split('_')[0]+'_bin.asc'
        swe_bin_path = os.path.join(swe_bin_folder, swe_bin_name)
        cmd_swe_bin = 'gdal_calc.py -A {} --calc="{}" --outfile={} --NoDataValue=-999 --type=Int16'.format(swe_proj_path, swe_func, swe_bin_path)

        try:
            subprocess.call(shlex.split(cmd_swe_bin))
            valid_date[col_name].ix[time] = swe_bin_path
        except Exception as e:
            continue
    valid_date.to_csv('./valid_date.csv')

print 'swe binary file is done'

# create modis binary file
modis_bin_folder = os.path.join(result_folder, 'modis_bin_folder')
if not os.path.isdir(modis_bin_folder):
    os.mkdir(modis_bin_folder)
col_name = 'modis_bin'
valid_date[col_name] = np.nan

modis_func = '((A>={})*(A<=100)+-999*(A==250))'.format(modis_threshold)  # when there is cloud, assign as no data values
for time in valid_date.index:
    modis_proj_path = valid_date['modis_tif_folder_proj'].ix[time]
    modis_bin_name = os.path.basename(modis_proj_path)[:-4]+'_bin.tif'
    modis_bin_path = os.path.join(modis_bin_folder, modis_bin_name)
    cmd_modis_bin = 'gdal_calc.py -A {} --calc="{}" --outfile={} --NoDataValue=-999 --type=Int16'.format(modis_proj_path, modis_func, modis_bin_path)

    try:
        subprocess.call(shlex.split(cmd_modis_bin))
        valid_date[col_name].ix[time] = modis_bin_path
    except Exception as e:
        continue

valid_date.to_csv('./valid_date.csv')

print 'modis binary file is done'



# # # step5: calculate area stats ################################################
# TODO remember to make the modis as mask to claculate the percent snow for swe results
# calculate area based stats


valid_date = pd.DataFrame.from_csv('./valid_date.csv', header=0)

for src_col_name in ['snow17_bin', 'modis_bin']:
    area_stats = pd.DataFrame(columns=['time', 'name', 'snow', 'no_snow', 'nodata', 'percent_snow'])
    percent_col_name = src_col_name+'_percent_snow'
    valid_date[percent_col_name] = np.nan
    i = 0
    for time in valid_date.index:
        i += 1
        bin_path = valid_date[src_col_name].ix[time]
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
    area_stats.to_csv('./{}_area_stats.csv'.format(src_col_name))
    valid_date.to_csv('./valid_date.csv')


snow17_area_stats = get_statistics(valid_date['snow17_bin_percent_snow'], valid_date['modis_bin_percent_snow'])
print snow17_area_stats
# ueb_area_stats = get_statistics(area_stats_dict['ueb_bin']['percent_snow'], area_stats_dict['modis_bin']['percent_snow'])

print 'area stats is done'


# step 6: calculate pixle based stats #########################################

import numpy
from matplotlib import pyplot as plt

model_list = ['snow17']
valid_date = pd.DataFrame.from_csv('./valid_date.csv', header=0)

for model_name in model_list:
    swe_bin_col = '{}_bin'.format(model_name)
    layer_stack = []
    for time in valid_date.index:
        # get compare grid
        swe_bin_path = valid_date[swe_bin_col].ix[time]
        modis_bin_path = valid_date['modis_bin'].ix[time]
        raster_obs = gdalnumeric.LoadFile(modis_bin_path)
        raster_model = gdalnumeric.LoadFile(swe_bin_path)

        obs = np.where(raster_obs != -999, raster_obs, np.nan)
        model = np.where(raster_model != -999, raster_model, np.nan)
        compare = obs-model  # 0 means true, 1 means false, -1 means false
        layer_stack.append(compare)

    # calculate oa values
    nan_mask = np.isnan(model)
    all_stack = numpy.stack(layer_stack)
    missing_data = np.where(nan_mask != True, np.isnan(all_stack).sum(axis=0), np.nan)
    mismatch_data = np.where(nan_mask != True, np.nansum(abs(all_stack), axis=0), np.nan)
    oa_result = 1 - mismatch_data.astype('float32') / (all_stack.shape[0]-missing_data)
    plt.imshow(oa_result, interpolation='nearest')
    plt.savefig('oa_result.png')
    numpy.save('all_stack_{}.npy'.format(model_name), all_stack)
    numpy.save('missing_data_{}.npy'.format(model_name), missing_data)
    numpy.save('mismatch_data_{}'.format(model_name), mismatch_data)
    numpy.save('OA_{}'.format(model_name), oa_result)




