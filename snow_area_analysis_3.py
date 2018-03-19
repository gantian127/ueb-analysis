"""
This is the 2nd version formal script for snow cover area analysis

step3:  use project tif files get binary files and calculate stats

step:
- create binary files for modis and swe, count the different pixels
- calculate the stats based on the pixel count

"""

import os
import gdalnumeric
import csv
import pandas as pd
import numpy as np



# default user settings apply to all steps ####################################################
# folders/files created by step 2 script
watershed = 'animas'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')
modis_proj_folder = os.path.join(result_folder, 'modis_proj_folder')
swe_proj_folders = [os.path.join(result_folder, name) for name in ['snow17_proj_folder', 'ueb_proj_folder']]

# threshold for processing
swe_threshold = 1  # mm

# time for analysis:
start_time = '2006/11/01'
end_time = '2007/10/01'

# new csv file path
stats_folder = os.path.join(result_folder, 'stats_folder')
if not os.path.isdir(stats_folder):
    os.mkdir(stats_folder)

stat_result_path = os.path.join(stats_folder, 'stat_result.csv')


# step1: get binary array and count pixel count ##############################################################
print 'step1: calculate pixel count '

# load data
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)
df_col_name = ['watershed', 'watershed_out', 'invalid', 'modis_snow', 'modis_dry',
               'swe_snow', 'swe_dry', 'A', 'B', 'C', 'D','weight']

for swe_proj_folder in swe_proj_folders:
    swe_col_name = os.path.basename(swe_proj_folder)

    if os.path.isdir(swe_proj_folder) and os.path.isdir(modis_proj_folder):
        # initiate data frame
        pixel_count = pd.DataFrame(index=snow_date.index, columns=df_col_name )
        pixel_count_path = os.path.join(stats_folder, 'pixel_count_{}.csv'.format(swe_col_name.split('_')[0]))

        # get pixel count
        for time in snow_date.index:
            modis_proj_path = snow_date['modis_proj_folder'].ix[time]
            swe_proj_path = snow_date[swe_col_name].ix[time]

            if os.path.isfile(swe_proj_path) and os.path.isfile(modis_proj_path):
                try:
                    # count watershed, watershed_out, invalid pixels
                    modis = gdalnumeric.LoadFile(modis_proj_path)
                    modis_bin = np.where(modis[1] != 0, modis[0], -999)
                    count_watershed = (modis[1] == 255).sum()
                    count_watershed_out = (modis[1] == 0).sum()
                    count_invalid = (modis_bin > 100).sum()

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
                     count_watershed, count_watershed_out, count_invalid, count_modis_snow, count_modis_dry,
                     count_swe_snow, count_swe_dry, a, b, c, d, round(weight, 4),
                    ]

                except Exception as e:
                    pixel_count.at[time] = -999
                    print 'fail at {}'.format(time)
                    continue

        pixel_count.to_csv(pixel_count_path)


# step2: use pixel count to calculate stats ##############################################################
print 'step2: calculate stats'

result_list = [['model', 'modis_ave', 'swe_ave', 'mae', 'nse', 'r2', 'correct']]
invalid_index_list = []
for model in ['snow17', 'ueb']:
    pixel_count_path = os.path.join(stats_folder, 'pixel_count_{}.csv'.format(model))

    if os.path.isfile(pixel_count_path):
        # calculate percent snow
        pixel_count = pd.DataFrame.from_csv(pixel_count_path, header=0)
        pixel_count = pixel_count[(pixel_count.weight > 0)]

        # if start_time and end_time:
        #     pixel_count = pixel_count[(pixel_count.index <= end_time) & (pixel_count.index >= start_time)]
        pixel_count['modis_percent_snow'] = (pixel_count.modis_snow) / (pixel_count.modis_snow + pixel_count.modis_dry)
        pixel_count['swe_percent_snow'] = (pixel_count.swe_snow) / (pixel_count.swe_snow+pixel_count.swe_dry)

        # calculate mas, nse, r2
        modis_ave = sum(pixel_count.weight*pixel_count.modis_percent_snow)/sum(pixel_count.weight)
        swe_ave = sum(pixel_count.weight*pixel_count.swe_percent_snow)/sum(pixel_count.weight)
        mae = sum(pixel_count.weight*abs(pixel_count.modis_percent_snow - pixel_count.swe_percent_snow))\
              / sum(pixel_count.weight)
        nse = 1 - sum(pixel_count.weight*np.power((pixel_count.modis_percent_snow - pixel_count.swe_percent_snow), 2))\
              / sum(pixel_count.weight * np.power((pixel_count.modis_percent_snow - modis_ave), 2))
        r2 = sum(pixel_count.weight*(pixel_count.modis_percent_snow - modis_ave)*(pixel_count.swe_percent_snow - swe_ave))\
             / (np.sqrt(sum(pixel_count.weight * np.power((pixel_count.modis_percent_snow - modis_ave), 2)))
                * np.sqrt(sum(pixel_count.weight * np.power((pixel_count.swe_percent_snow - swe_ave), 2))))



        # calculate correctness and fitness
        # version 2: remove no snow date (at least one source should have snow)
        pixel_count['correctness'] = (pixel_count.A + pixel_count.D) / (pixel_count.C + pixel_count.D + pixel_count.B + pixel_count.A)
        correct = sum(pixel_count.weight*pixel_count.correctness) / sum(pixel_count.weight)

        # version 1: follow the paper method, but will have the situation that C and D all is 0 to create nan for correct and fitness
        # correct = sum(pixel_count.weight*(pixel_count.D*100 / (pixel_count.C + pixel_count.D))) / sum(pixel_count.weight)
        # fitness = sum(pixel_count.weight*(pixel_count.D*100 / (pixel_count.C + pixel_count.D + pixel_count.B))) / sum(pixel_count.weight)

        # save results
        result_list.append([model, modis_ave, swe_ave, mae, nse, r2, correct])
        pixel_count.to_csv(pixel_count_path)

with open(stat_result_path, "wb") as f:
    writer = csv.writer(f)
    writer.writerows(result_list)

print 'snow_area_analysis_3: stats calculation is done'
