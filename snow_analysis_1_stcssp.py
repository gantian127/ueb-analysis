"""
This is the 3rd version script for snow cover area analysis

step 1: get new modis data (STC SSP) and swe snow date data and unzip

requirements:
- add swe domain average time series
- put utility py file

step:
- get snow date csv file
- copy and unzip modis .gz file
- copy and unzip swe .gz file

info:
- the new modis data is already with RDHM projection.
"""

import gzip
import os
import shutil

import pandas as pd

from snow_cover_utility import get_sim_dataframe


# default user settings apply to all steps ####################################################
watershed = 'MPHC2'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
if not os.path.isdir(result_folder):
    os.mkdir(result_folder)
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')


# Step 1 get model snow date info #########################################
print 'step1: get snow date info'

# user settings
swe_ts_snow17 = 'MPHC2_we_local.ts'
swe_ts_ueb = 'MPHC2_uebW_local.ts'
ueb_skip = 121
snow17_skip = 136
# snow_threshold = 0
start_time = '2001-10-01'
end_time = '2001-10-05'

# user settings
swe_gz_folders = [
    r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/snow17_best_calibration/SAC_out/we',  # snow17 swe xmrg .gz folder
    r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/ueb_sublimation_test/SAC_out/uebW/',  # ueb swe xmrg .gz folder
]
grid_time_step = [
    '06',  # snow17 swe output
    '06'  # ueb swe output
]
var_name = [
    'we',  # snow17 swe var name
    'uebW',  # ueb swe var name
]

# get date of snow for both models and save in csv file
concat = []
col_name = []

if swe_ts_snow17:
    snow17_df = get_sim_dataframe(swe_ts_snow17, sim_skip=snow17_skip, start_time=start_time, end_time=end_time)
    # snow17_snow_date = snow17_df[snow17_df > 0]
    # concat.append(snow17_snow_date)
    concat.append(snow17_df)
    col_name.append('snow17_swe')

if swe_ts_ueb:
    ueb_df = get_sim_dataframe(swe_ts_ueb, sim_skip=ueb_skip , start_time=start_time, end_time=end_time)
    # ueb_snow_date = ueb_df[ueb_df > 0]
    # concat.append(ueb_snow_date)
    concat.append(ueb_df)
    col_name.append('ueb_swe')

if concat:
    snow_date = pd.concat(concat, axis=1)
    snow_date.columns = col_name
    snow_date.to_csv(model_snow_date_path)
    print 'get snow date info done'
else:
    print 'Failed to get snow date'


# step 2 modis: get data based on snow date #################################################
print 'step2: get modis data with snow'

# user settings
modis_data_folder = r'/Projects/Tian_workspace/rdhm_ueb_modeling/MODIS_STC_SSP/STC_SSP_Snow_cover/tif_raster'  # this is the folder that stores the original .tif data
modis_snowdate_folder = os.path.join(result_folder, 'modis_snowdate_folder')  #  folder that stores the modis with snow
fail_modis = []
# create tif folder:
if not os.path.isdir(modis_snowdate_folder):
    os.mkdir(modis_snowdate_folder)

# load snow date record
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)

# unzip .gz file to assigned folder
col_name = 'modis_snowdate_folder'
snow_date[col_name] = 'invalid'
for time in snow_date.index:
    ori_tif_path = os.path.join(modis_data_folder, 'STC_SSP_{}_Sc.tif'.format(time.strftime("%Y%m%d")))
    modis_tif_path = os.path.join(modis_snowdate_folder, os.path.basename(ori_tif_path))
    if not os.path.isfile(modis_tif_path):
        try:
            shutil.copyfile(ori_tif_path, modis_tif_path)
            snow_date[col_name].ix[time] = os.path.basename(modis_tif_path)
        except Exception as e:
            print 'failed to copy modis data!!'
            fail_modis.append(modis_tif_path)
            continue
    else:
        snow_date[col_name].ix[time] = os.path.basename(modis_tif_path)

snow_date.to_csv(model_snow_date_path)
with open(os.path.join(result_folder, 'fail_modis.txt'), 'w') as f:
    f.write('\n'.join(fail_modis))


# step3 swe: unzip .gz file to assigned folder ####################################
print 'step3: get swe data with snow'

swe_snowdate_folders = [os.path.join(result_folder, name) for name in ['snow17_snowdate_folder', 'ueb_snowdate_folder']]  # folder that stores swe tif with snow

# copy snow date swe to assigned folder
for i in range(0, len(swe_gz_folders)):
    swe_gz_folder = swe_gz_folders[i]
    if os.path.isdir(swe_gz_folder):
        fail_swe = []
        swe_tif_folder = swe_snowdate_folders[i]
        if not os.path.isdir(swe_tif_folder):
            os.mkdir(swe_tif_folder)

        col_name = os.path.basename(swe_tif_folder)
        snow_date[col_name] = 'invalid'

        for time in snow_date.index:
            swe_gz_name = '{}{}{}z.gz'.format(var_name[i], time.strftime('%m%d%Y'), grid_time_step[i])
            swe_gz_path = os.path.join(swe_gz_folder, swe_gz_name)
            swe_tif_path = os.path.join(swe_tif_folder, swe_gz_name[:-3])
            if not os.path.isfile(swe_tif_path):
                try:
                    if os.path.isfile(swe_gz_path):
                        with gzip.open(swe_gz_path, 'rb') as inf:
                            with open(swe_tif_path, 'wb') as outf:
                                content = inf.read()
                                outf.write(content)
                        snow_date[col_name].ix[time] = os.path.basename(swe_tif_path)
                except Exception as e:
                    print 'failed to unzip model swe !'
                    print swe_gz_path
                    print os.path.isfile(swe_gz_path)
                    fail_swe.append(swe_gz_path)
                    continue
            else:
                snow_date[col_name].ix[time] = os.path.basename(swe_tif_path)

        snow_date.to_csv(model_snow_date_path)
        with open(os.path.join(result_folder, 'fail_swe_{}.txt'.format(var_name[i])), 'w') as f:
            f.write('\n'.join(fail_swe))

print 'snow_area_analysis_1: unzip files is done'

