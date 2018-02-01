"""
This includes  the utility functions to support snow cover area analysis

"""
import pandas as pd
import numpy as np
import math
import gdal
from gdalconst import GA_ReadOnly
import matplotlib.pyplot as plt


def get_sim_dataframe(sim_file, start_time='', end_time='', sim_skip=91, time_change_ori=('24', '25'), time_change_new=('23', '1'), column_name=''):
    # get sim daily data
    raw_sim = pd.read_csv(sim_file, skiprows=sim_skip, header=None, names=['raw'])
    sim_data = raw_sim['raw'].str.split('\s+', expand=True)
    sim_data.rename(columns={3: 'sim'}, inplace=True)
    sim_data['sim'] = sim_data['sim'].astype(float)
    for i in range(0, len(time_change_ori)):
        sim_data[[2]] = sim_data[[2]].apply(lambda x: x.replace(time_change_ori[i], time_change_new[i]))
    sim_data['time'] = sim_data[[1, 2]].apply(lambda x: ''.join(x), axis=1)
    sim_data['time'] = pd.to_datetime(sim_data['time'], format='%d%m%y%H')
    sim_data.drop([0, 1, 2], axis=1, inplace=True)
    sim_data.ix[sim_data.sim < 0, 'sim'] = np.nan
    sim = sim_data.set_index('time').groupby(pd.TimeGrouper(freq='D'))['sim'].mean()

    if start_time and end_time:
        sim = sim[(sim.index >= start_time) & (sim.index <= end_time)]

    return sim


def get_statistics(sim, obs):
    # calculate statistics
    stat_df = pd.DataFrame({'discharge': sim, 'observation': obs},
                             columns=['discharge', 'observation']
                           )

    # rmse: sqrt(mean(sum((Qs-Qo)**2)))
    stat_df['valDiff'] = stat_df['observation'] - stat_df['discharge']
    valDiff_mean = stat_df['valDiff'].mean()
    stat_df['valDiffSq'] = stat_df['valDiff'].apply(lambda x: x ** 2)
    valDiffSq_mean = stat_df['valDiffSq'].mean()
    rmse = math.sqrt(valDiffSq_mean)

    # nse: 1 - sum ((Qs-Qo)**2) / sum((Qo-Qomean)**2)
    stat_df['valDiffA'] = stat_df['valDiff'].apply(lambda x: abs(x))
    valDiffA_mean = stat_df['valDiffA'].mean()
    obs_mean = stat_df['observation'].mean()
    valDiffSq_sum = stat_df['valDiffSq'].sum()

    stat_df['valDiffMean'] = stat_df['observation'].apply(lambda x: x - obs_mean)
    stat_df['valDiffSqmean'] = stat_df['valDiffMean'].apply(lambda x: x ** 2)
    valDiffSqmean_sum = stat_df['valDiffSqmean'].sum()

    nse = 1 - (valDiffSq_sum / valDiffSqmean_sum)
    mae = valDiffA_mean

    # correlation coefficient
    r = stat_df[['observation', 'discharge']].corr()['observation'][1]

    # bias: Qs-Qo
    stat_df['bias'] = stat_df['discharge'] - stat_df['observation']
    bias = stat_df['bias'].mean()

    return {'rmse': rmse, 'nse': nse, 'mae': mae, 'r': r, 'bias': bias}


def array_to_raster(output_path, source_path, array_path=None, array_data=None, no_data=-999, x_size=None, y_size=None, data_type='float32'):
    data_type_mapping = {
        'Int16': gdal.GDT_Int16,
        'float32': gdal.GDT_Float32
    }

    if array_path:
        raster_data = np.load(array_path)
        raster_data[np.isnan(raster_data)] = no_data
    else:
        raster_data = array_data

    source_raster = gdal.Open(source_path, GA_ReadOnly)
    driver = gdal.GetDriverByName("GTiff")
    if not(x_size and y_size):
        x_size = raster_data.shape[-1]
        y_size = raster_data.shape[-2]
    output_raster = driver.Create(output_path, x_size, y_size, bands=1, eType=data_type_mapping[data_type])
    output_raster.SetGeoTransform(source_raster.GetGeoTransform())
    output_raster.SetProjection(source_raster.GetProjection())
    output_raster.GetRasterBand(1).SetNoDataValue(no_data)
    output_raster.GetRasterBand(1).WriteArray(raster_data.astype(data_type))

    output_raster = None
    source_raster = None

    return 'finish raster creation'


def create_bar_plot(data_frame, data_list, x_ticks_list=None,
                    fig=None, ax=None, figsize=None,
                    legend=False, title='', xlabel='',
                    labels=None,
                    fontsize=10,
                    text='',
                    text_position=(0, 0),
                    text_fontsize=10,
                    ylabel='', save_path=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    data_frame[data_list].plot.bar(ax=ax, legend=legend, rot=0)

    if x_ticks_list:
        ax.set_xticklabels(x_ticks_list, fontsize=fontsize)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if legend and labels:
        ax.legend(labels)

    if text:
        ax.text(text_position[0], text_position[1], text, transform=ax.transAxes, fontsize=text_fontsize)

    if save_path:
        fig.savefig(save_path)

    return fig, ax