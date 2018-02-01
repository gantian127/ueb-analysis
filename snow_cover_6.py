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
print 'step1: start oa stats analysis'
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
print 'step2: start elevation stats analysis'
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
        valid_grid_count = (oa_result != -999).sum()
        if os.path.isfile(elevation_path):
            # get low oa elevation grid
            elev = gdalnumeric.LoadFile(elevation_path)[0]
            elev[elev < 0] = -999
            low_oa = np.where(((oa_result <= low_oa_threshold) & (oa_result >= 0)), oa_result, -999)
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
    elev_stats['elev_percent_{}'.format(model_name)] = [round(float(x)*100/valid_grid_count, 1) for x in hist]
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
print 'step3: start slope stats analysis'

slope_stats = pd.DataFrame()
slope_stats_path = os.path.join(terrain_stats_folder, 'slope_stats_low_oa')
model_name_list = []

# get low oa slope grid tif and png file
for oa_array_path in oa_array_path_list:
    if os.path.isfile(oa_array_path):
        model_name = os.path.basename(oa_array_path).split('_')[1]
        model_name_list.append(model_name)
        oa_result = np.load(oa_array_path)
        oa_result[np.isnan(oa_result)] = -999
        valid_grid_count = (oa_result != -999).sum()
        if os.path.isfile(slope_path):
            # get low oa slope grid
            slope = gdalnumeric.LoadFile(slope_path)[0]
            slope[slope < 0] = -999
            low_oa = np.where(((oa_result <= low_oa_threshold) & (oa_result >= 0)), oa_result, -999)
            slope_stat_grid = np.where(low_oa != -999, slope, -999)
            np.save(slope_stats_path + '_{}.npy'.format(model_name), slope_stat_grid)

            # calculate low oa slope stats
            hist, bin = np.histogram(slope_stat_grid, range=(0, 90), bins=9)
            slope_stats['slope_pixel_{}'.format(model_name)] = hist
            slope_stats['slope_percent_{}'.format(model_name)] = [round(float(x) * 100 / valid_grid_count, 1) for x in hist]
            slope_stats['slope_bin'] = [int(x) for x in bin[1:]]
            slope_stats.to_csv(slope_stats_path + '.csv')

            # make low oa slope plot
            plt.clf()
            plt.imshow(slope_stat_grid, interpolation='nearest')
            plt.colorbar()
            plt.title('plot of low oa slope for {}'.format(model_name))
            plt.savefig(slope_stats_path + '_{}.png'.format(model_name))

            # save low oa slope as tif
            array_to_raster(output_path=slope_stats_path + '_{}.tif'.format(model_name),
                            source_path=slope_path,
                            array_data=slope_stat_grid)
        else:
            print'provide slope file path !!'
    else:
        print 'provide oa array file path!!'

for data_name, ylabel in zip(['slope_pixel', 'slope_percent'], ['pixel count', 'arae(%)']):
    slope_stat_hist = [data_name + '_{}'.format(model) for model in model_name_list]
    create_bar_plot(slope_stats, slope_stat_hist, slope_stats['slope_bin'].tolist(),
                    title='plot of {}'.format(data_name),
                    xlabel='slope (degree)',
                    ylabel=ylabel,
                    legend=True,
                    labels=model_name_list,
                    save_path=os.path.join(terrain_stats_folder, 'slope_stats_barplot_of_{}.png').format(data_name)
                    )

# step4 aspect stats ############################################################
print 'step4: start aspect stats analysis'

aspect_stats = pd.DataFrame()
aspect_stats_path = os.path.join(terrain_stats_folder, 'aspect_stats_low_oa')
model_name_list = []

# get low oa aspect grid tif and png file
for oa_array_path in oa_array_path_list:
    if os.path.isfile(oa_array_path):
        model_name = os.path.basename(oa_array_path).split('_')[1]
        model_name_list.append(model_name)
        oa_result = np.load(oa_array_path)
        oa_result[np.isnan(oa_result)] = -999
        valid_grid_count = (oa_result != -999).sum()
        if os.path.isfile(aspect_path):
            # preprocess aspect with index and get stats
            aspect = gdalnumeric.LoadFile(aspect_path)[0]
            aspect[oa_result == -999] = -999
            for bound, index in zip(range(0, 360, 45), range(1, 9)):
                aspect[(aspect >= bound) & (aspect < bound+45)] = index
            np.save(aspect_stats_path + '_ori_index_{}.npy'.format(model_name), aspect)

            hist, bin = np.histogram(aspect, range=(1, 8), bins=range(1, 10))  # np.unique(aspect_stat_grid,return_counts=True)
            aspect_stats['aspect_pixel_ori_{}'.format(model_name)] = hist
            aspect_stats['aspect_percent_ori_{}'.format(model_name)] = [round(float(x) * 100 / valid_grid_count, 1) for x in hist]
            aspect_stats['aspect_bin'] = [int(x) for x in bin[:-1]]  # don't change the bin list subset as the last value is 9!!
            aspect_stats.to_csv(aspect_stats_path + '.csv')

            # get low oa aspect stats
            low_oa = np.where(((oa_result <= low_oa_threshold) & (oa_result >= 0)), oa_result, -999)
            aspect_stat_grid = np.where(low_oa != -999, aspect, -999)
            np.save(aspect_stats_path + '_index_{}.npy'.format(model_name), aspect_stat_grid)

            # preprocess grid and calculate low oa aspect stats
            # for bound, index in zip(range(0, 360, 45), range(1, 9)):
            #     aspect_stat_grid[(aspect_stat_grid >= bound) & (aspect_stat_grid < bound+45)] = index
            # np.save(aspect_stats_path + '_index_{}.npy'.format(model_name), aspect_stat_grid)

            hist, bin = np.histogram(aspect_stat_grid, range=(1, 8), bins=range(1, 10))  # np.unique(aspect_stat_grid,return_counts=True)
            aspect_stats['aspect_pixel_{}'.format(model_name)] = hist
            aspect_stats['aspect_percent_{}'.format(model_name)] = [round(float(x) * 100 / valid_grid_count, 1) for x in
                                                                    hist]
            aspect_stats['aspect_bin'] = [int(x) for x in bin[:-1]]  # don't change the bin list subset as the last value is 9!!
            aspect_stats.to_csv(aspect_stats_path + '.csv')

            # make low oa aspect plot
            plt.clf()
            plt.imshow(aspect_stat_grid, interpolation='nearest')
            plt.colorbar()
            plt.title('plot of low oa aspect for {}'.format(model_name))
            plt.savefig(aspect_stats_path + '_{}.png'.format(model_name))

            # save low oa aspect as tif
            array_to_raster(output_path=aspect_stats_path + '_{}.tif'.format(model_name),
                            source_path=aspect_path,
                            array_data=aspect_stat_grid)
        else:
            print'provide aspect file path !!'
    else:
        print 'provide oa array file path!!'

for data_name, ylabel in zip(['aspect_pixel', 'aspect_percent'], ['pixel count', 'arae(%)']):
    aspect_stat_hist = [data_name + '_{}'.format(model) for model in model_name_list]
    aspect_hist = [data_name+'_ori_{}'.format(model) for model in model_name_list]
    for stat_hist,tag in zip([aspect_stat_hist, aspect_hist], ['final', 'ori']):
        create_bar_plot(aspect_stats, stat_hist,
                        ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],  # this is the tick name for different aspect index
                        title='plot of {} {}'.format(data_name,tag),
                        xlabel='aspect (degree)',
                        ylabel=ylabel,
                        legend=True,
                        labels=model_name_list,
                        save_path=os.path.join(terrain_stats_folder, 'aspect_stats_barplot_of_{}_{}.png').format(data_name, tag)
                        )

    create_bar_plot(aspect_stats, aspect_hist+aspect_stat_hist,
                    ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'],  # this is the tick name for different aspect index
                    title='plot of {} {}'.format(data_name,tag),
                    xlabel='aspect (degree)',
                    ylabel=ylabel,
                    legend=True,
                    # labels=model_name_list,
                    figsize=(10, 6),
                    save_path=os.path.join(terrain_stats_folder, 'aspect_stats_barplot_of_{}_mix.png').format(data_name)
                    )


# step5 land cover stats ############################################################
print 'step5: start land cover stats analysis'
bin_number = 6
scale = 100

nlcd_stats = pd.DataFrame()
nlcd_stats_path = os.path.join(terrain_stats_folder, 'nlcd_stats_low_oa')
nlcd_stat_grid_list = []
model_name_list = []

nlcd_type_dict = {
    11: 'water',
    12: 'perennial ice snow',
    21: 'developed open space',
    22: 'developed Low intensity',
    23: 'developed medium intensity',
    24: 'developed high intensity',
    31: 'bare rock',
    41: 'deciduous forest',
    42: 'evergreen forest',
    43: 'mixed forest',
    52: 'shrub',
    71: 'grasslands',
    81: 'pasture',
    82: 'cultivated Crops',
    90: 'woody wetlands',
    95: 'emergent herbaceous wetlands',
}   # https://www.mrlc.gov/nlcd11_stat.php

# get low oa nlcd grid tif and png file
for oa_array_path in oa_array_path_list:
    if os.path.isfile(oa_array_path):
        model_name = os.path.basename(oa_array_path).split('_')[1]
        model_name_list.append(model_name)
        oa_result = np.load(oa_array_path)
        oa_result[np.isnan(oa_result)] = -999
        valid_grid_count = (oa_result != -999).sum()
        if os.path.isfile(nlcd_path):
            # get nlcd grid and calculate stats
            nlcd = gdalnumeric.LoadFile(nlcd_path)[0].astype('Int16')
            nlcd[oa_result == -999] = -999

            bin, hist = np.unique(nlcd, return_counts=True)
            nlcd_stats['nlcd_pixel_ori_{}'.format(model_name)] = hist[1:]
            nlcd_stats['nlcd_percent_ori_{}'.format(model_name)] = [round(float(x) * 100 / valid_grid_count, 1) for x in hist[1:]]
            nlcd_stats['nlcd_bin'] = [int(x) for x in bin[1:]]  # don't change the bin list subset as the first value is -999!!
            nlcd_stats.to_csv(nlcd_stats_path + '.csv')

            # get low oa nlcd stats
            low_oa = np.where(((oa_result <= low_oa_threshold) & (oa_result >= 0)), oa_result, -999)
            nlcd_stat_grid = np.where(low_oa != -999, nlcd, -999)
            np.save(nlcd_stats_path + '_{}.npy'.format(model_name), nlcd_stat_grid)

            raw_bin, raw_hist = np.unique(nlcd_stat_grid, return_counts=True)
            raw_bin = raw_bin.tolist()
            raw_hist = raw_hist.tolist()
            new_hist = []
            for index in bin:
                if index in raw_bin:
                    new_hist.append(raw_hist[raw_bin.index(index)])
                else:
                    new_hist.append(0)

            nlcd_stats['nlcd_pixel_{}'.format(model_name)] = new_hist[1:]
            nlcd_stats['nlcd_percent_{}'.format(model_name)] = [round(float(x) * 100 / valid_grid_count, 1) for x in new_hist[1:]]
            nlcd_stats['nlcd_bin'] = [int(x) for x in bin[1:]]  # don't change the bin list subset as the last value is 9!!
            nlcd_stats.to_csv(nlcd_stats_path + '.csv')

            # make low oa nlcd plot
            plt.clf()
            plt.imshow(nlcd_stat_grid, interpolation='nearest')
            plt.colorbar()
            plt.title('plot of low oa nlcd for {}'.format(model_name))
            plt.savefig(nlcd_stats_path + '_{}.png'.format(model_name))

            # save low oa nlcd as tif
            array_to_raster(output_path=nlcd_stats_path + '_{}.tif'.format(model_name),
                            source_path=nlcd_path,
                            array_data=nlcd_stat_grid)
        else:
            print'provide nlcd file path !!'

bin_names_list = []
for index in nlcd_stats['nlcd_bin'].tolist():
    full_name = nlcd_type_dict[index]
    simple_name = ''.join([name[0].upper() for name in full_name.split()])
    bin_names_list.append(simple_name)

for data_name, ylabel in zip(['nlcd_pixel', 'nlcd_percent'], ['pixel count', 'arae(%)']):
    nlcd_stat_hist = [data_name + '_{}'.format(model) for model in model_name_list]
    nlcd_hist = [data_name+'_ori_{}'.format(model) for model in model_name_list]

    for stat_hist, tag in zip([nlcd_stat_hist, nlcd_hist], ['final', 'ori']):
        create_bar_plot(nlcd_stats, stat_hist,
                        bin_names_list,  # this is the tick name for different nlcd index
                        title='plot of {} {}'.format(data_name,tag),
                        xlabel='land type',
                        ylabel=ylabel,
                        legend=True,
                        labels=model_name_list,
                        save_path=os.path.join(terrain_stats_folder, 'nlcd_stats_barplot_of_{}_{}.png').format(data_name, tag)
                        )
    create_bar_plot(nlcd_stats, nlcd_hist + nlcd_stat_hist,
                    bin_names_list,  # this is the tick name for different nlcd index
                    title='plot of {} {}'.format(data_name, tag),
                    xlabel='land type',
                    ylabel=ylabel,
                    legend=True,
                    # labels=model_name_list,
                    figsize=(10, 6),
                    save_path=os.path.join(terrain_stats_folder, 'nlcd_stats_barplot_of_{}_mix.png').format(
                        data_name)
                    )

        # ToDo:  remove water
        # TODo: for other analysis, make compare plots of original and low oa histogram
        # Todo: label of the compare plot