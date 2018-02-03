"""
This is the formal script for snow cover area analysis

step 1: get modis and swe snow date data and unzip

requirements:
- add swe domain average time series
- put utility py file

step:
- get snow date csv file
- copy and unzip modis .gz file
- copy and unzip swe .gz file

"""

import gzip
import os

import numpy as np
import pandas as pd

from snow_cover_utility import get_sim_dataframe


# default user settings apply to all steps ####################################################
watershed = 'animas'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
if not os.path.isdir(result_folder):
    os.mkdir(result_folder)
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')


# Step 1 get model snow date info #########################################
print 'step1: get snow date info'

# user settings
swe_ts_snow17 = 'DRGC2_we_snow17.ts'
swe_ts_ueb = ''#'DRGC2_we_ueb.ts'
# snow_threshold = 0
start_time = '2006-10-01'
end_time = '2007-9-30'


# get date of snow for both models and save in csv file
concat = []
col_name = []

if swe_ts_snow17:
    snow17_df = get_sim_dataframe(swe_ts_snow17, sim_skip=136, start_time=start_time, end_time=end_time)
    # snow17_snow_date = snow17_df[snow17_df > 0]
    # concat.append(snow17_snow_date)
    concat.append(snow17_df)
    col_name.append('snow17_swe')

if swe_ts_ueb:
    ueb_df = get_sim_dataframe(swe_ts_ueb, sim_skip=136, start_time=start_time, end_time=end_time)
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
modis_gz_folder = r'/Projects/snow_fraction_canadj/'  # this is the folder that stores the original .gz data
modis_snowdate_folder = os.path.join(result_folder, 'modis_snowdate_folder')  #  folder that stores the modis with snow

# create tif folder:
if not os.path.isdir(modis_snowdate_folder):
    os.mkdir(modis_snowdate_folder)

# load snow date record
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)

# unzip .gz file to assigned folder
col_name = 'modis_snowdate_folder'
snow_date[col_name] = np.nan
for time in snow_date.index:
    year = str(time.year)
    day = '{:03d}'.format(time.dayofyear)
    # gz_name = 'modscag.snow_fraction.{}.{}.mosaic.tif.gz'.format(year, day)
    gz_name = 'modscag.snow_fraction_canadj.{}.{}.mosaic.tif.gz'.format(year, day)
    gz_path = os.path.join(modis_gz_folder, year, day, gz_name)
    modis_tif_path = os.path.join(modis_snowdate_folder, gz_name[:-3])

    try:
        with gzip.open(gz_path, 'rb') as inf:
            with open(modis_tif_path, 'wb') as outf:
                content = inf.read()
                outf.write(content)
        snow_date[col_name].ix[time] = modis_tif_path
    except Exception as e:
        print 'failed to unzip modis data!!'
        continue

# step3 swe: unzip .gz file to assigned folder ####################################
print 'step3: get swe data with snow'

# user settings
swe_gz_folders = [
    r'/Projects/Tian_workspace/snow_analysis_test/WY2007/',  # snow17 swe xmrg .gz folder
    # 'ueb_folder',  # ueb swe xmrg .gz folder
]

swe_snowdate_folders = [os.path.join(result_folder, name) for name in ['snow17_snowdate_folder', 'ueb_snowdate_folder']]  # folder that stores swe tif with snow


# copy snow date swe to assigned folder
for i in range(0, len(swe_gz_folders)):
    swe_gz_folder = swe_gz_folders[i]
    swe_tif_folder = swe_snowdate_folders[i]
    if not os.path.isdir(swe_tif_folder):
        os.mkdir(swe_tif_folder)

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
    snow_date.to_csv(model_snow_date_path)

print 'snow_cover_1: unzip files is done'

