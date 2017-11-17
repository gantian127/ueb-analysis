"""
This is to analyze the 22yr UEB output point data for UEB+SAC workflow.

1 read the data from the text file and clean up the data
2 make plots of mass balance
3 make plots adding sublimation part

This method uses the data of prcp, swit, swe from point simulation results as text file from UEB

"""
import pandas as pd
from datetime import datetime
import urllib
from plot_SAC_utility import *


# point_name = ['molaslake',
# point_file = 'molaslake.txt'
start_time = ''
end_time = ''
interval = 1
format = '%Y/%m'

point_info = {
    'molaslake': 'C:\Users\jamy\Desktop\Nasa_analysis\molaslake.txt',
    # 'cascade': 'C:\Users\jamy\Desktop\Nasa_analysis\cascade.txt'
}

results_dir = r'C:\Users\jamy\Desktop\Nasa_analysis'

# Get simulation data and plot ####################################################

for point_name, point_file in point_info.items():
    # create results_dir
    results_dir = os.path.join(results_dir, point_name)
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)

    # get model simulation data frame
    point_df = pd.read_csv(point_file, sep='\s+')
    point_df['time'] = point_df['Year'].map(str)+ ' ' + point_df['Month'].map(str) + ' ' + point_df['Day'].map(str)+ ' ' + point_df['dHour'].map(int).map(str)
    point_df['time'] = point_df['time'].apply(lambda x: datetime.strptime(x,'%Y %m %d %H'))
    point_df['error'] = point_df['cump'] - point_df['cumes'] - point_df['cumMr'] - point_df['SWE']


    # make mass balance plot for start_time, end_time
    if start_time and end_time:
        point_df = point_df.ix[(point_df.time >= start_time) & (point_df.time <= end_time)]

    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_X_Y(point_df.time,
                      [point_df.cump, point_df.cumes, point_df.cumMr, point_df.SWE],
                      label_list=['cumulative prcp', 'cumulative sublim', 'cumulative melt', 'SWE'],
                      fig=fig, ax=ax[0],
                      xlim=[datetime(point_df['time'].iloc[0].year, 1, 1), datetime(point_df['time'].iloc[-1].year, 12, 31)],
                      )

    refine_plot(ax[0],
                title='Mass balance for snow analysis at point {}'.format(point_name),
                ylabel='cumulative depth(m)',
                xlabel='time',
                interval=interval,
                format=format,
                )

    plot_multiple_X_Y(point_df.time,
                      [point_df.error],
                      ['mass balance error'],
                      fig=fig, ax=ax[1],
                      xlim=[datetime(point_df['time'].iloc[0].year, 1, 1), datetime(point_df['time'].iloc[-1].year, 12, 31)],
                      )

    refine_plot(ax[1],
                title='Mass balance error at point {}'.format(point_name),
                ylabel='mass balance error(m)',
                xlabel='time',
                interval=interval,
                format=format,
                )


    # save_fig(fig, save_as=os.path.join(results_dir, 'mass_balance_{}.png'.format(point_name)))

    # cumulative sublimation plot
    fig, ax = plot_multiple_X_Y(point_df.time,
                                [point_df.cumes],
                                ['cumulative sublim'],
                                xlim=[datetime(point_df['time'].iloc[0].year, 1, 1), datetime(point_df['time'].iloc[-1].year, 12, 31)],
                                figsize=(15, 5)
                                )

    refine_plot(ax,
                title='Cumulative sublimation at point {}'.format(point_name),
                ylabel='cumulative sublimation(m)',
                xlabel='time',
                interval=interval,
                format=format,
                )

    # save_fig(fig, save_as=os.path.join(results_dir, 'cum_sublim_{}.png'.format(point_name)))



# # Get observation data and make plots ###########################################
#
#
# snotel_info = {
#     # 'cascade': 'https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultiTimeSeriesGroupByStationReport/daily/start_of_period/386:CO:SNTL%7Cid=%22%22%7Cname/1987-10-01,2010-10-01/WTEQ::value,PREC::value?fitToScreen=false'.format(start_time, end_time),
#     # 'molaslake': 'https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultiTimeSeriesGroupByStationReport/daily/start_of_period/632:CO:SNTL%7Cid=%22%22%7Cname/1987-10-01,2010-10-01/WTEQ::value,PREC::value?fitToScreen=false'
#     'cascade': 'https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultiTimeSeriesGroupByStationReport/daily/start_of_period/386:CO:SNTL%7Cid=%22%22%7Cname/{},{}/WTEQ::value,PREC::value?fitToScreen=false'.format(start_time, end_time),
#     'molaslake': 'https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customMultiTimeSeriesGroupByStationReport/daily/start_of_period/632:CO:SNTL%7Cid=%22%22%7Cname/{},{}/WTEQ::value,PREC::value?fitToScreen=false'.format(start_time,end_time)
# }
#
# # get snotel data
# snotel_22yr = {}
#
# for name, url in snotel_info.items():
#     # instantaneous value at the start of the day for swe, prcp acc
#     file_name = os.path.join(results_dir, '{}_snotel.csv'.format(name))
#     urllib.urlretrieve(url, file_name)
#     snotel_22yr[name] = pd.read_csv(file_name, header=54)
#     snotel_22yr[name].columns = ['time', 'swe', 'prcp_acc']  #  prcp accumulative for each water year
#
#     snotel_22yr[name]['time'] = pd.to_datetime(snotel_22yr[name].time)
#     snotel_22yr[name]['swe_m'] = snotel_22yr[name].swe * 0.0254
#     snotel_22yr[name]['prcp_acc_m'] = snotel_22yr[name].prcp_acc * 0.0254
#
#     snotel_22yr[name]['prcp_m'] = ''
#
#     for year in range(snotel_22yr[name]['time'][0].year, snotel_22yr[name]['time'].iloc[-1].year):
#         df = snotel_22yr[name][['prcp_acc_m', 'time']].ix[
#             (snotel_22yr[name].time >= '{}-10-01'.format(year)) &
#             (snotel_22yr[name].time <= '{}-10-01'.format(year+1))
#             ]
#
#         data = df['prcp_acc_m'].tolist()
#         index = df.index[:-1]
#         new_data = [data[i + 1] - data[i] for i in range(0, len(data)) if i < len(data)-2]
#         new_data.append(data[-1])
#
#         snotel_22yr[name].loc[index, 'prcp_m'] = new_data
#
#
# # swe plot
# fig, ax = plot_multiple_X_Y(point_df.time,
#                             [point_df.SWE],
#                             ['cumulative prcp', 'cumulative sublim', 'cumulative melt', 'SWE'],
#                             xlim=[datetime(point_df.time[0].year, 1, 1), datetime(point_df.time.iloc[-1].year, 12, 31)],
#                             figsize=(15,5)
#                             )
#
# refine_plot(ax,
#             title='Snow water equivalent at point {}'.format(point_name),
#             ylabel='SWE(m)',
#             xlabel='time',
#             interval=interval,
#             format=format
#             )
#
# save_fig(fig, save_as=os.path.join(results_dir, 'swe_{}.png'.format(point_name)))