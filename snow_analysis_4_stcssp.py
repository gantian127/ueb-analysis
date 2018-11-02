"""
This is the 3rd version formal script for snow cover area analysis

step4:  use pixel count result to calculate stats and make analysis plots  (new modis data)

requirements:
- step3 needs to be finished and create the pixel count file
- matplotlib version 2.1.2
- pandas version 0.22.0


step:
- get valid date and create refined pixel count files
- calculate the stats based on the valid pixel count data:
  a) valid date stats
  b) all years stats and plots: nse, fitness, scatter plot
  b) monthly stats and plots: fitness
  c) annual stats and plots:

findings:
1) monthly: compare the monthly stats table and plots
   - during Oct-Nov (early accumulation):
     UEB and snow17 both has over estimate of total snow cover than modis (monthly scatter plot)
     snow17 has a better fitness
     UEB has a better total area R relationship and catching the trend and less under estimate of the peak (except 2001, 2004, 2007)

   - during Dec - Mar (snow accumulation):
     UEB and snow17 has higher snow cover area than modis
     UBE is doing better for total area without much over estimate (annual time series and monthly scatter plot)
     UEB can capture the total area change trend. (see 2010 annual time series)
     snow17 is doing better for fitness.

   - during April - June (snow melt): remove the outlier 2010-6-7 weired snow cover
     snow17 has faster melt than ueb but both has slower melt rate than modis
     snow17 is doing better at both total area and fitness.

   - bad data: 2010-6-7 weired snow cover

2) annual:  check the time series
   - 2006, 2010 has good data

"""

import os
import calendar

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# default user settings apply to all steps ####################################################
# folders/files created by step 2 script
watershed = 'DIRC2'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')
modis_proj_folder = os.path.join(result_folder, 'modis_proj_folder')
swe_proj_folders = [os.path.join(result_folder, name) for name in ['snow17_proj_folder', 'ueb_proj_folder']]
stats_folder = os.path.join(result_folder, 'stats_folder')
pixel_count_path_list = [os.path.join(stats_folder, 'pixel_count_{}.csv'.format(name)) for name in ['snow17', 'ueb']]

# threshold for processing
swe_threshold = 1  # mm

# time for analysis:
start_time = '2000/10/01'
end_time = '2010/06/30'

# melt month
start_melt = 3
end_melt = 6

plt.ioff()

# step1: get binary array and count pixel count ##############################################################
print 'step1: get valid date'
valid_list = []
bad_date = []
for pixel_count_path in pixel_count_path_list:
    if os.path.isfile(pixel_count_path):
        pixel_count = pd.DataFrame.from_csv(pixel_count_path, header=0)
        valid_data = pixel_count[(pixel_count.modis_snow > 0)]
        valid_list.append(valid_data)

valid_data = pd.concat(valid_list, axis=1)
for date in bad_date:
    valid_data.drop(pd.Timestamp(date), inplace=True)
valid_index = valid_data.index


# step2: calculate stats ###########################################################################
print 'step2: calculate stats'


# define stats function
def get_snow_stats(df):
    pixel_count = df.copy()
    modis_ave = pixel_count.modis_percent_snow.mean()
    swe_ave = pixel_count.swe_percent_snow.mean()
    mae = sum(abs(pixel_count.modis_percent_snow - pixel_count.swe_percent_snow))/len(pixel_count)
    nse = 1 - sum(np.power((pixel_count.modis_percent_snow - pixel_count.swe_percent_snow), 2)) / sum(np.power((pixel_count.modis_percent_snow - modis_ave), 2))

    return [modis_ave, swe_ave, mae, nse]


# calculate stats and make plots
for model in ['snow17', 'ueb']:
    pixel_count_path = os.path.join(stats_folder, 'pixel_count_{}.csv'.format(model))

    if os.path.isfile(pixel_count_path):
        # refine pixel_count and calculate percent snow, fitness #################################################
        pixel_count = pd.DataFrame.from_csv(pixel_count_path, header=0)
        pixel_count = pixel_count.ix[valid_index]

        if start_time and end_time:
            pixel_count = pixel_count[(pixel_count.index <= end_time) & (pixel_count.index >= start_time)]
        pixel_count['modis_percent_snow'] = (pixel_count.modis_snow) / (pixel_count.modis_snow + pixel_count.modis_dry)
        pixel_count['swe_percent_snow'] = (pixel_count.swe_snow) / (pixel_count.swe_snow + pixel_count.swe_dry)
        pixel_count['fitness'] = (pixel_count.D) / (pixel_count.C + pixel_count.D + pixel_count.B)  # fitness is more informative than correctness
        pixel_count.to_csv(os.path.join(stats_folder, 'refine_pixel_count_{}.csv'.format(model)))
        # pixel_count['correctness'] = (pixel_count.A + pixel_count.D) / (pixel_count.C + pixel_count.D + pixel_count.B + pixel_count.A)  # this is not good
        # pixel_count['correctness'] = (pixel_count.D) / (pixel_count.C + pixel_count.D)  # correctness may have invalid values when C=0, D=0

        # valid date stats  ############################################################################
        valid_date_month = pixel_count.groupby(pixel_count.index.month).count()
        valid_date_annual = pixel_count.resample('A-SEP').count()

        fig, ax = plt.subplots(2, 1, figsize=(15, 9))
        valid_date_month.plot.bar(y='weight',
                                  color='blue',
                                  ax=ax[0],
                                  rot=0,
                                  legend=False,
                                  )

        ax[0].set_xlabel('Month')
        ax[0].set_ylabel('Number of days')
        ax[0].set_title('Number of valid days in each month')

        valid_date_annual.plot.bar(x=valid_date_annual.index.year,
                                   y='weight',
                                   color='green',
                                   ax=ax[1],
                                   rot=0,
                                   legend=False,
                                   )

        ax[1].set_xlabel('Year')
        ax[1].set_ylabel('Number of days')
        ax[1].set_title('Number of valid days in each water year')

        plt.tight_layout()
        fig.savefig(os.path.join(stats_folder, 'valid_date_stats_{}.png'.format(model)))
        valid_date_month.to_csv(os.path.join(stats_folder,'valid_date_month_{}.csv'.format(model)))
        valid_date_annual.to_csv(os.path.join(stats_folder,'valid_date_annual_{}.csv'.format(model)))

        #  all years stats ############################################################################
        columns = ['modis ave', 'swe ave', 'mae', 'nse', 'fitness']
        annual_stats = pd.DataFrame(columns=columns)

        df_type = ['all years', 'snow melt']
        melt_snow = pixel_count[(pixel_count.index.month >= start_melt) & (pixel_count.index.month <= end_melt)]

        for df_type, stat_df in zip(df_type, [pixel_count, melt_snow]):
            stats = get_snow_stats(stat_df)
            stats.append(stat_df['fitness'].mean())
            annual_stats.ix[df_type, columns] = stats

            # plot: obs vs sim scatter
            fig, ax = plt.subplots()
            stat_df.plot.scatter(x='modis_percent_snow', y='swe_percent_snow', ax=ax)
            ax.plot([pixel_count['modis_percent_snow'].min(), pixel_count['modis_percent_snow'].max()],
                    [pixel_count['modis_percent_snow'].min(), pixel_count['modis_percent_snow'].max()],
                    linestyle=':',
                    color='r')
            ax.set_xlabel('Modis observation')
            ax.set_ylabel('Snow model output')
            ax.set_title('Comparison of percent snow of {} for {} model '.format(df_type, model))
            fig.savefig(os.path.join(stats_folder, '{}_percent_snow_scatter_{}'.format(df_type, model)))

        annual_stats.to_csv(os.path.join(stats_folder, 'all_year_stat_{}.csv'.format(model)))

        #  monthly stats ##############################################################################
        # get each month stats
        columns = ['modis ave', 'swe ave', 'mae', 'nse', 'fitness']
        month_stats = pd.DataFrame(index=range(1, 13), columns=columns)

        for month, group in pixel_count.groupby(pixel_count.index.month):
            stats = get_snow_stats(group)
            stats.append(group['fitness'].mean())
            month_stats.at[month, columns] = stats
            group.to_csv(os.path.join(stats_folder, 'monthly_data_{}_{}.csv').format(month, model))

            # plot: obs vs sim scatter
            fig, ax = plt.subplots()
            group.plot.scatter(x='modis_percent_snow',y='swe_percent_snow', ax=ax)
            ax.plot([group['modis_percent_snow'].min(), group['modis_percent_snow'].max()],
                    [group['modis_percent_snow'].min(), group['modis_percent_snow'].max()],
                    linestyle=':',
                    color='r')
            ax.set_xlabel('Modis observation')
            ax.set_ylabel('Snow model output')
            ax.set_title('Comparison of percent snow in {} for {} model '.format(calendar.month_name[month][:3], model))
            fig.savefig(os.path.join(stats_folder, 'monthly_percent_snow_{}_{}'.format(month, model)))

        # plot: monthly fitness boxplot
        fig, ax = plt.subplots(figsize=(13, 6))
        pixel_count.boxplot(column='fitness', ax=ax, by=pixel_count.index.month, grid=False)
        ax.set_xlabel('Month')
        ax.set_ylabel('Fitness')
        ax.set_title('Box plot of fitness in each month for {} moddel'.format(model))
        fig.suptitle('')
        fig.savefig(os.path.join(stats_folder, 'monthly_fitness_{}'.format(model)))

        # plot: monthly snow cover boxplot
        fig, ax = plt.subplots(figsize=(13, 6))
        pixel_count.boxplot(column=['modis_percent_snow'],
                            ax=ax, by=pixel_count.index.month, grid=False)
        ax.set_xlabel('Month')
        ax.set_ylabel('percent snow')
        ax.set_title('Box plot of percent snow in each month for Modis observation'.format(model))
        fig.suptitle('')
        fig.savefig(os.path.join(stats_folder, 'monthly_percent_snow_scatter_{}'.format(model)))

        month_stats.to_csv(os.path.join(stats_folder, 'month_stat_{}.csv'.format(model)))

        # annual stats ##############################################################################
        # get annual stats
        columns = ['modis ave', 'swe ave', 'mae', 'nse', 'fitness']
        annual_stats = pd.DataFrame(columns=columns)
        melt_stats = pd.DataFrame(columns=columns[:-1])
        fitness_list = []
        snow_list = []
        year_list = []

        for time, group in pixel_count.groupby(pd.Grouper(freq='A-SEP')):
            # annual stats
            stats = get_snow_stats(group)
            stats.append(group['fitness'].mean())
            annual_stats.at[time, columns] = stats

            fitness_list.append(group.dropna()['fitness'].tolist())
            snow_list.append(group['modis_percent_snow'].tolist())
            year_list.append(time.year)

            # seasonal stats
            melt_df = group[(group.index.month >= start_melt) & (group.index.month <= end_melt)]
            melt_stats.at[time, columns[:-1]] = get_snow_stats(melt_df)

            # plot: obs vs sim scatter plot
            fig, ax = plt.subplots()
            group.plot.scatter(x='modis_percent_snow', y='swe_percent_snow', ax=ax)
            ax.plot([group['modis_percent_snow'].min(), group['modis_percent_snow'].max()],
                    [group['modis_percent_snow'].min(), group['modis_percent_snow'].max()],
                    linestyle=':',
                    color='r')
            ax.set_xlabel('Modis observation')
            ax.set_ylabel('Snow model output')
            ax.set_title('Comparison of percent snow in {} for {} model '.format(time.year, model))
            fig.savefig(os.path.join(stats_folder, 'annual_percent_snow_scatter_{}_{}'.format(time.year, model)))

            # plot: obs vs sim time series
            fig, ax = plt.subplots(figsize=(12, 6))
            ax_twin = ax.twinx()
            group.plot(y=['modis_percent_snow', 'swe_percent_snow',],
                       ax=ax,
                       style=['-', '-.'],
                       rot=0,
                       ms=3)
            group.plot(y='fitness',
                       ax=ax_twin,
                       style=['g*'],
                       alpha=0.6,
                       ms=4
                       )
            ax.legend(['modis', model], loc=2)
            ax_twin.legend(loc=0)
            ax.set_xlabel('Time')
            ax.set_ylabel('Percent snow')
            ax_twin.set_ylabel('Fitness')
            ax.set_title('Percent snow and fitness in {} for {} model '.format(time.year, model))
            fig.savefig(os.path.join(stats_folder, 'annual_percent_snow_ts_{}_{}'.format(time.year, model)))

            group.to_csv(os.path.join(stats_folder, 'annual_data_{}_{}.csv').format(time.year, model))

        annual_stats.to_csv(os.path.join(stats_folder, 'annual_stat_{}.csv'.format(model)))
        melt_stats.to_csv(os.path.join(stats_folder, 'melt_stat_{}.csv').format(model))

        # plot: annual fitness boxplot
        fig, ax = plt.subplots(figsize=(13, 6))
        ax.boxplot(fitness_list)
        ax.set_xlabel('Water Year')
        ax.set_ylabel('Fitness')
        ax.set_xticklabels(year_list)
        ax.set_title('Box plot of fitness in each water year for {} model'.format(model))
        fig.savefig(os.path.join(stats_folder, 'annual_fitness_{}.png'.format(model)))

        # plot: annual snow cover boxplot
        fig, ax = plt.subplots(figsize=(13, 6))
        ax.boxplot(snow_list)
        ax.set_xlabel('Water year')
        ax.set_ylabel('percent snow')
        ax.set_xticklabels(year_list)
        ax.set_title('Box plot of percent snow in each water year for Modis observation'.format(model))
        fig.savefig(os.path.join(stats_folder, 'annual_snow_cover_{}.png'.format(model)))

print 'snow_analysis_4: stats calculation is done'
