"""
This is the formal script for snow cover area analysis

step6: os analysis for terrain data

requirements:
- make sure all other scripts are executed.

step:
- OA stats: area coverage distribution of different oa values
- elevation vs low OA stats:
- slope vs low OA stats
- aspect vs low OA stats
- land cover vs low OA stats

"""

import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import gdalnumeric

from snow_cover_utility import create_bar_plot, array_to_raster


# User settings #############################################################
# low oa threshold
low_oa_threshold = 0.7

# file and folders created before
watershed = 'animas'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
terrain_folder = os.path.join(result_folder, 'terrain')  # step5 to create terrain data
stats_folder = os.path.join(result_folder, 'stats_folder')  # step4 to create oa result

oa_array_path_list = [os.path.join(stats_folder, name) for name in ['oa_snow17_bin_folder.npy', 'oa_ueb_bin_folder.npy']]
elevation_path = os.path.join(terrain_folder,'{}_dem_watershed_clip.tif'.format(watershed))
slope_path = os.path.join(terrain_folder,'{}_slope_clip.tif'.format(watershed))
aspect_path = os.path.join(terrain_folder, '{}_aspect_clip.tif'.format(watershed))
nlcd_path = os.path.join(terrain_folder, '{}_nlcd_clip.tif'.format(watershed))

# create new folder
terrain_stats_folder = os.path.join(result_folder, 'terrain_stats_folder')

if not os.path.isdir(terrain_stats_folder):
    os.mkdir(terrain_stats_folder)


# step1 OA stats ###################################################################
print 'start oa stats analysis'
oa_stats = pd.DataFrame()
oa_stats_path = os.path.join(terrain_stats_folder, 'oa_stats.csv')
model_name_list = []

# get oa stats
for oa_array_path in oa_array_path_list:
    if os.path.isfile(oa_array_path):
        model_name = os.path.basename(oa_array_path).split('_')[1]
        model_name_list.append(model_name)
        oa_result = np.load(oa_array_path)
        oa_result[np.isnan(oa_result)] = -999
        hist, bin = np.histogram(oa_result, range=(0, 1), bins=10)
        hist_percent = [round(float(x)*100/hist.sum(), 1) for x in hist]
        oa_stats['oa_pixel_{}'.format(model_name)] = hist
        oa_stats['oa_percent_{}'.format(model_name)] = hist_percent
        oa_stats['oa_bin'] = bin[1:]
        oa_stats.to_csv(oa_stats_path)
    else:
        print 'please provide oa array file !!'

for name, ylabel in zip(['oa_pixel', 'oa_percent'], ['pixel count', 'arae(%)']):
    oa_stats_hist = [name+'_{}'.format(model_name) for model_name in model_name_list]
    create_bar_plot(oa_stats, oa_stats_hist, oa_stats['oa_bin'].tolist(),
                    title='plot of {} '.format(name),
                    xlabel='overall accuracy',
                    ylabel=ylabel,
                    legend=True,
                    labels=model_name_list,
                    save_path=os.path.join(terrain_stats_folder, 'oa_stats_barplot_of_{}.png').format(name)
                    )


# step2 Elevation stats  #############################################################
print 'start elevation stats analysis'
bin_number = 6
scale = 100
elev_stats = pd.DataFrame()
elev_stats_path = os.path.join(terrain_stats_folder, 'elev_stats_low_oa')
array_path_list = []
elev_stat_grid_list = []
model_name_list = []

# get low oa elevation grid tif and png file
for oa_array_path in oa_array_path_list:
    if os.path.isfile(oa_array_path):
        model_name = os.path.basename(oa_array_path).split('_')[1]
        model_name_list.append(model_name)
        oa_result = np.load(oa_array_path)
        oa_result[np.isnan(oa_result)] = -999
        if os.path.isfile(elevation_path):
            # get low oa elevation grid
            elev = gdalnumeric.LoadFile(elevation_path)[0]
            elev[elev < 0] = -999
            low_oa = np.where(((oa_result <= 0.7) & (oa_result >= 0)), oa_result, -999)
            elev_stat_grid = np.where(low_oa != -999, elev, -999)
            elev_stat_grid_list.append(elev_stat_grid)
            np.save(elev_stats_path+'_{}.npy'.format(model_name), elev_stat_grid)

            # make low oa elevation plot
            plt.clf()
            plt.imshow(elev_stat_grid, interpolation='nearest')
            plt.colorbar()
            plt.title('plot of low oa elevation for {}'.format(model_name))
            plt.savefig(elev_stats_path+'_{}.png'.format(model_name))

            # save low oa elevation as tif
            array_to_raster(output_path=elev_stats_path+'_{}.tif'.format(model_name),
                            source_path=elevation_path,
                            array_data=elev_stat_grid)
        else:
            print'provide elevation file path !!'
    else:
        print 'provide oa array file path!!'


# make low oa elevation stats comparison bar plot
ma = np.ma.masked_equal(np.stack(elev_stat_grid_list), -999, copy=False)
start = scale*int(ma.min()/scale)
end = scale*(int(ma.max()/scale)+1)
step = ((end-start)/(scale*bin_number)+1)*scale


for elev_stat_grid, model_name in zip(elev_stat_grid_list, model_name_list):
    hist, bin = np.histogram(elev_stat_grid, range=(start, end), bins=range(start, end+step, step))
    elev_stats['elev_pixel_{}'.format(model_name)] = hist
    elev_stats['elev_percent_{}'.format(model_name)] = [round(float(x)*100/hist.sum(), 1) for x in hist]
    elev_stats['elev_bin'] = bin[:-1]
    elev_stats.to_csv(elev_stats_path+'.csv')


for data_name, ylabel in zip(['elev_pixel', 'elev_percent'], ['pixel count', 'arae(%)']):
    elev_stat_hist = [data_name+'_{}'.format(model) for model in model_name_list]
    create_bar_plot(elev_stats, elev_stat_hist, elev_stats['elev_bin'].tolist(),
                      title='plot of {}'.format(data_name),
                      xlabel='elevation (m)',
                      ylabel=ylabel,
                      legend=True,
                      labels=model_name_list,
                      save_path=os.path.join(terrain_stats_folder, 'elev_stats_barplot_of_{}.png').format(data_name)
                    )












# step3 slope stats ############################################################




# step4 aspect stats ############################################################




# step5 land cover stats ############################################################