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
terrain_folder = os.path.join(result_folder, 'terrain')
stats_folder = os.path.join(result_folder, 'stats_folder')

oa_array_path = [os.path.join(stats_folder, name) for name in ['oa_snow17_bin_folder.npy', 'oa_ueb_bin_folder.npy']]
elevation_path = os.path.join(terrain_folder,'{}_dem_watershed_clip.tif'.format(watershed))
slope_path = os.path.join(terrain_folder,'{}_slope_clip.tif'.format(watershed))
aspect_path = os.path.join(terrain_folder, '{}_aspect_clip.tif'.format(watershed))
nlcd_path = os.path.join(terrain_folder, '{}_nlcd_clip.tif'.format(watershed))

# create new folder
terrain_stats_folder = os.path.join(result_folder, 'terrain_stats_folder')

if not os.path.isdir(terrain_stats_folder):
    os.mkdir(terrain_stats_folder)


# step1 OA stats ###################################################################
for oa_file_path in oa_array_path:
    if os.path.isfile(oa_file_path):
        model_name = os.path.basename(oa_file_path).split('_')[1]
        oa_stats = pd.DataFrame()
        oa_stats_path = os.path.join(terrain_stats_folder, 'oa_stats_{}.csv'.format(model_name))
        oa_result = np.load(oa_file_path)
        oa_result[np.isnan(oa_result)] = -999
        hist, bin = np.histogram(oa_result, range=(0, 1), bins=10)
        hist_percent = [round(float(x)*100/hist.sum(), 1) for x in hist]
        oa_stats['oa_pixel'] = hist
        oa_stats['oa_percent'] = hist_percent
        oa_stats['oa_bin'] = bin[1:]
        for name,ylabel in zip(['oa_pixel', 'oa_percent'], ['pixel count', 'arae(%)']):
            create_bar_plot(oa_stats, name, oa_stats['oa_bin'].tolist(),
                            title='plot of {}'.format(name),
                            xlabel='overal accuracy',
                            ylabel=ylabel,
                            save_path=os.path.join(terrain_stats_folder, 'plot_of_{}_{}.png').format(name, model_name)
                            )

        oa_stats.to_csv(oa_stats_path)


# step2 Elevation stats  #############################################################
bin_number = 5
for oa_file_path in oa_array_path:

    if os.path.isfile(oa_file_path):
        model_name = os.path.basename(oa_file_path).split('_')[1]
        elev_stats = pd.DataFrame()
        elev_stats_path = os.path.join(terrain_stats_folder, 'elev_stats_{}.csv'.format(model_name))
        oa_result = np.load(oa_file_path)
        oa_result[np.isnan(oa_result)] = -999
        if os.path.isfile(elevation_path):
            # get low oa elevation grid
            elev = gdalnumeric.LoadFile(elevation_path)[0]
            elev[elev < 0] = -999
            low_oa = np.where(((oa_result <= 0.7) & (oa_result >= 0)), oa_result, -999)
            elev_stat_grid = np.where(low_oa != -999, elev, -999)

            # calculate stats and save to file TODO: not finished here !!!
            ma = np.ma.masked_equal(elev_stat_grid, -999, copy=False)
            scale = 10**(len(str(int(ma.max()-ma.min()))) - 2)

            start = int(ma.min()/100)*100
            end = int(ma.max()/100)
            step = int(end-start)/bin_number


            hist, bin = np.histogram(elev_stat_grid, range=(ma.min(), ma.max()), bins=range(start, end+step, step))
            elev_stats['elev_pixel'] = hist
            elev_stats['elev_percent'] = elev_stats['elev_pixel'] / float(hist.sum())
            elev_stats['elev_bin'] = bin[1:]


            # make low oa elevation plot
            elev_stat_file_path = os.path.join(terrain_stats_folder, os.path.basename(elevation_path).replace('.tif',''))

            fig = plt.imshow(elev_stat_grid, interpolation='nearest')
            plt.colorbar()
            plt.title('plot of low oa elevation {}'.format(os.path.basename(oa_file_path)))
            plt.savefig(elev_stat_file_path+'_low_oa.png')
            plt.clf()

            # save low oa elevation as tif
            array_to_raster(output_path=elev_stat_file_path+'_low_oa.tif',
                            source_path=elevation_path,
                            array_data=elev_stat_grid)



print 'Elevation stats is done'










# step3 slope stats ############################################################




# step4 aspect stats ############################################################




# step5 land cover stats ############################################################