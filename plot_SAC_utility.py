"""
This includes the utilities for SAC-SMA output plots
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import math
from datetime import datetime, timedelta
import numpy as np
import calendar
import os


def plot_multiple_X_Y(time, data_list,
                      label_list=None,
                      linestyle_list=None,
                      fig=None, ax=None,
                      xlim=None,
                      ylim=None,
                      xticks=False,
                      figsize=None,
                      ):

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    for i in range(0, len(data_list)):
        fmt = linestyle_list[i] if linestyle_list else '-'
        ax.plot(time, data_list[i], fmt, label=label_list[i] if label_list else str(i))

    if xlim:
        ax.set_xlim(xlim[0], xlim[1])

    if ylim:
        ax.set_ylim(ylim[0], ylim[1])

    if xticks:
        ax.set_xticks(time)

    return fig, ax


def refine_plot(ax, xlabel='', ylabel='', title='', interval=1, format='%Y/%m', text=None, text_position=None, legend=True, time_axis=True):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if time_axis:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(format))

    if legend:
        ax.legend(loc='best')

    if text and text_position:
        x1, x2 = ax.get_xlim()
        x = x1 + text_position[0]*(x2-x1)
        y1, y2 = ax.get_ylim()
        y = y1 + text_position[1]*(y2-y1)

        ax.text(x, y, text)


def save_fig(fig, save_as=None):
    if save_as is not None:
        try:
            fig.savefig(save_as)
            return '{} is created'.format(save_as)
        except Exception as e:
            return 'Warning: failed to save the plot as a file.'


def get_sacsma_time_and_discharge(discharge=None, surf_flow=None, sub_flow=None,
                          discharge_skip=91, surf_flow_skip=62, sub_flow_skip=62,
                          unit_factor=1, unit_offset=0,
                          time_hr_change='24', time_hr_change_factor=1):
    """
    used for auto calibration option selection
    """
    results = {}

    if discharge:
        # get discharge
        raw_discharge = pd.read_csv(discharge, skiprows=discharge_skip, header=None, names=['raw'])
        discharge = raw_discharge['raw'].str.split('\s+', expand=True)
        discharge_flow = [float(x)*unit_factor+unit_offset for x in discharge[3].tolist()]

        # get time
        time_str = (discharge[1] + discharge[2]).tolist()
        time_obj = []
        for x in time_str:
            if x[-2:] == time_hr_change:
                x = x[:-2] + x[-2:].replace(time_hr_change, '23')
                time = datetime.strptime(x, '%d%m%y%H')
                time += timedelta(hours=time_hr_change_factor)
            else:
                time = datetime.strptime(x, '%d%m%y%H')

            time_obj.append(time)

        results['discharge'] = discharge_flow
        results['time'] = time_obj

    elif surf_flow and sub_flow:

        # get surf, sub, sum flow
        raw_sub = pd.read_csv(sub_flow, skiprows=sub_flow_skip, header=None, names=['raw'])
        raw_surf = pd.read_csv(surf_flow, skiprows=surf_flow_skip, header=None, names=['raw'])
        sub = raw_sub['raw'].str.split('\s+', expand=True)
        surf = raw_surf['raw'].str.split('\s+', expand=True)
        sub_flow = [float(x)*unit_factor + unit_offset for x in sub[3].tolist()]
        surf_flow = [float(x)*unit_factor + unit_offset for x in surf[3].tolist()]
        sum_flow = [x + y for x, y in zip(sub_flow, surf_flow)]

        # get time
        time_str = (sub[1] + sub[2]).tolist()
        time_obj = []
        for x in time_str:
            if x[-2:] == '24':
                x = x[:-2] + x[-2:].replace('24', '23')
                time = datetime.strptime(x, '%d%m%y%H')
                time += timedelta(hours=1)
            else:
                time = datetime.strptime(x, '%d%m%y%H')

            time_obj.append(time)

        results['discharge'] = sum_flow
        results['surf'] = surf_flow
        results['sub'] = sub_flow
        results['time'] = time_obj
    else:
        return 'Please provide valid input file'

    return results


def get_data_by_time_aggregation(time, data, freq='D'):
    """
    used for auto calibration option selection
    """
    df = pd.DataFrame(data={'time': time, 'data': data}, columns=['time', 'data'])
    data = df.set_index('time').groupby(pd.TimeGrouper(freq=freq))['data'].mean()

    return data.tolist(), data.index.values


def get_rit_discharge(discharge, skiprows=3, start_date_obj=None, end_date_obj=None,
                      unit_factor=0.0283168, unit_offset=0):
    """
    used for auto calibration option selection
    """

    rti_discharge = pd.read_csv(discharge, skiprows=skiprows, header=None, names=['raw'])  # time column is used as index in dataframe
    if start_date_obj and end_date_obj:
        start_date = datetime.strftime(start_date_obj, '%Y-%m-%d')
        end_date = datetime.strftime(end_date_obj + timedelta(days=1), '%Y-%m-%d')
        discharge = rti_discharge.ix[start_date:end_date]['raw'].apply(lambda x: x * unit_factor + unit_offset).tolist()
    else:
        discharge = rti_discharge['raw'].apply(lambda x: x * unit_factor + unit_offset).tolist()

    return discharge


# Functions for SAC mass balance check
def get_sac_ts_dataframe(ts_file_list, start_time='', end_time='', sim_skip=91,
                          time_change_ori=('24', '25'), time_change_new=('23', '1'),
                          grouper_freq=None, save_as=None):
    """
     This will create the daily sim vs obs data frame for discharge comparision
    """
    df_list = []

    # get sim daily data
    for ts_file in ts_file_list:
        if os.path.isfile(ts_file):
            column_name = '_'.join(os.path.basename(ts_file).split('_')[1:-1])
            raw_sim = pd.read_csv(ts_file, skiprows=sim_skip, header=None, names=['raw'])
            sim_data = raw_sim['raw'].str.split('\s+', expand=True)
            sim_data.rename(columns={3: column_name }, inplace=True)
            sim_data[column_name] = sim_data[column_name].astype(float)
            for i in range(0, len(time_change_ori)):
                sim_data[[2]] = sim_data[[2]].apply(lambda x: x.replace(time_change_ori[i], time_change_new[i]))
            sim_data['time'] = sim_data[[1, 2]].apply(lambda x: ''.join(x), axis=1)
            sim_data['time'] = pd.to_datetime(sim_data['time'], format='%d%m%y%H')
            sim_data.drop([0, 1, 2], axis=1, inplace=True)
            sim_data.ix[sim_data[column_name] < 0, column_name] = np.nan
            sim_data = sim_data.set_index('time')
            df_list.append(sim_data)

    DF = pd.concat(df_list, axis=1, join='inner')
    if start_time and end_time:
        DF = DF[(DF.index >= start_time) & (DF.index <= end_time)]

    DF.dropna(inplace=True)

    if grouper_freq:
        DF = DF.groupby(pd.TimeGrouper(freq=grouper_freq)).mean()

    return DF


# Functions used for 22yr model comparision and data analysis
def get_sim_obs_dataframe(sim_file, obs_file=None, start_time='', end_time='', sim_skip=91, obs_skip=3, obs_unit=0.0283168,
                          time_change_ori=('24', '25'), time_change_new=('23', '1'), save_folder=None):
    """
     This will create the daily sim vs obs data frame for discharge comparision
    """
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

    # get observation data
    obs = pd.read_csv(obs_file, skiprows=obs_skip, header=None, names=['obs'])
    obs.index = pd.to_datetime(obs.index, format='%Y-%m-%d %H:%M:%S')
    obs['obs'] = obs['obs'].apply(lambda x: x*obs_unit)
    obs.ix[obs.obs < 0, 'obs'] = np.nan  # remove negative value

    # create dataframe
    DF = pd.concat([sim, obs], axis=1, join_axes=[sim.index]).reset_index()

    path = os.path.join(save_folder, 'DF.csv') if save_folder else './DF.csv'
    DF.to_csv(path)

    return DF


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


def plot_obs_vs_sim(
                    time=None, sim=None, obs=None,
                    DF=None,
                    figsize=[(15,10),(15,5)],
                    ts_title='Time series of observation vs. simulation discharge',
                    ts_xlabel='Time',
                    ts_ylabel='Discharge(cms)',
                    ts_xlim=None,
                    ts_ylim=None,
                    ts_line_label=['observation','simulation',],
                    ts_line_style=['-', '-'],
                    title='Observation vs. simulation discharge',
                    xlabel='Observation(cms)',
                    ylabel='Simulation(cms)',
                    xlim=None,
                    ylim=None,
                    text_position=[0.1, 0.80],
                    month_interval=1,
                    format='%Y',
                    reverse=False,
                    save_folder=None,
                    save_name='',
                    ):

    # calculate statistics
    if DF is None:
        DF = pd.DataFrame({'time': time,
                            'sim': sim,
                            'obs': obs},
                            columns=['time', 'sim', 'obs'])

    statistics = get_statistics(DF['sim'], DF['obs'])

    # plot obs vs sac time series
    fig, ax = plt.subplots(2, 1, figsize=figsize[0])
    Y = [DF['obs'], DF['sim']]
    if reverse:
        Y.reverse()
        ts_line_label.reverse()
        ts_line_style.reverse()

    plot_multiple_X_Y(DF['time'],
                      Y,
                      label_list=ts_line_label,
                      linestyle_list=ts_line_style,
                      ax=ax[0], fig=fig,
                      xlim=ts_xlim,
                      ylim=ts_ylim,
                       )
    refine_plot(ax[0], xlabel=ts_xlabel, ylabel=ts_ylabel, title=ts_title,
                legend=True, interval=month_interval, format=format)

    # plot obs vs sac scatter plot
    ax[1].scatter(DF['obs'], DF['sim'])
    refine_plot(ax[1], xlabel=xlabel, ylabel=ylabel, title=title,
                time_axis=False, legend=False)
    ax[1].plot([DF['obs'].min(), DF['obs'].max()],
                [DF['obs'].min(), DF['obs'].max()],
                linestyle = ':',
                color='r',
                )
    if xlim:
        ax[1].set_xlim(xlim[0], xlim[1])

    if ylim:
        ax[1].set_ylim(ylim[0], ylim[1])

    plt.text(DF['obs'].max()*text_position[0], DF['sim'].max()*text_position[1],
             ' RMSE = {} \n NSE = {} \n R = {} \n Bias = {}cms'.format(statistics['rmse'], statistics['nse'],
                                                                   statistics['r'], round(statistics['bias'],3)),
             fontsize=11, color='b')

    plt.tight_layout()

    if save_folder or save_name:
        save_fig(fig, save_as=os.path.join(save_folder if save_folder else os.getcwd(),
                                           save_name if save_name else 'time_series.png')
                 )

    # plot daily bias
    DF['bias'] = DF['sim'] - DF['obs']
    fig, ax = plot_multiple_X_Y(DF['time'], [DF['bias']],
                                xlim=ts_xlim,
                                figsize=figsize[1],
                                label_list=['sim-obs (mean={}'.format(DF['bias'].mean())])
    refine_plot(ax, xlabel='time', ylabel='discharge(cms)',
                title='Daily mean bias',
                time_axis=True,
                interval=month_interval,
                format=format,
                legend=True,

                )
    if save_folder or save_name:
        save_fig(fig, save_as=os.path.join(save_folder if save_folder else os.getcwd(),
                                           'bias_{}'.format(save_name) if save_name else 'time_series_bias.png')
                 )

    return fig, ax


def get_monthly_mean_analysis(DF, watershed_area, save_folder=None, text_position=[0.1, 0.8]):
    """
    tested monthly mean multiyear in excel with DF.csv and monthly mean.csv
    """
    # monthly_mean
    monthly_mean = DF.groupby([DF.time.dt.month, DF.time.dt.year]).mean()
    monthly_mean_multiyear = monthly_mean.groupby(level=0).mean()
    monthly_mean_multiyear['bias'] = monthly_mean_multiyear['sim'] - monthly_mean_multiyear['obs']
    bias_mean = monthly_mean_multiyear['bias'].mean()
    percent_bias = sum(monthly_mean_multiyear['bias']) / sum(monthly_mean_multiyear['obs']) * 100

    # monthly bias in depth
    monthly_mean_multiyear['factor'] = [calendar.monthrange(2010, x)[1] * 24 * 3600 * (watershed_area ** -1) * 1000 for x
                                        in range(1, 13)]  # depth in mm
    monthly_mean_multiyear['sim_depth'] = monthly_mean_multiyear.sim * monthly_mean_multiyear.factor
    monthly_mean_multiyear['obs_depth'] = monthly_mean_multiyear.obs * monthly_mean_multiyear.factor
    monthly_mean_multiyear['bias_depth'] = monthly_mean_multiyear['sim_depth'] - monthly_mean_multiyear['obs_depth']
    bias_mean_depth = monthly_mean_multiyear['bias_depth'].mean()
    percent_bias_depth = sum(monthly_mean_multiyear['bias_depth']) / sum(monthly_mean_multiyear['obs_depth']) * 100

    # write results
    path = os.path.join(save_folder, 'monthly_mean_multiyear.csv') if save_folder else './monthly_mean_multiyear.csv'
    monthly_mean_multiyear.to_csv(path)
    with open(path, 'a') as my_file:
        my_file.write(
            '\nbias mean = {}'
            '\npercent bias = {}%'
            '\nbias mean depth = {}'
            '\npercent bias depth = {}%'.format(bias_mean, percent_bias, bias_mean_depth, percent_bias_depth)
        )

    path = os.path.join(save_folder,'monthly_mean.csv') if save_folder else './monthly_mean.csv'
    monthly_mean.to_csv(path)

    # make plots
    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_X_Y(monthly_mean_multiyear.index,
                      [monthly_mean_multiyear.sim, monthly_mean_multiyear.obs],
                      ax=ax[0], fig=fig,
                      label_list=['sim', 'obs'],
                      linestyle_list=['-o', '-o'],
                      xticks=True)

    refine_plot(ax[0], xlabel='month', ylabel='discharge(cms)',
                title='Monthly mean discharge',
                legend=True,
                time_axis=False)

    plot_multiple_X_Y(monthly_mean_multiyear.index,
                      [monthly_mean_multiyear.bias],
                      ax=ax[1], fig=fig,
                      label_list=['bias'],
                      linestyle_list=['-o'],
                      xticks=True)

    refine_plot(ax[1], xlabel='month', ylabel='bias(cms)',
                title='Monthly mean bias',
                legend=True,
                time_axis=False,
                text='mean bias = {} \npercent bias= {}%'.format(round(bias_mean,2), round(percent_bias,2)),
                text_position=text_position
                )

    path = os.path.join(save_folder, 'monthly_mean_bias.png') if save_folder else 'monthly_mean_bias.png'
    save_fig(fig, path)

    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_X_Y(monthly_mean_multiyear.index,
                      [monthly_mean_multiyear.sim_depth, monthly_mean_multiyear.obs_depth],
                      ax=ax[0], fig=fig,
                      xticks=True,
                      label_list=['sim', 'obs'],
                      linestyle_list=['-o', '-o'],)

    refine_plot(ax[0], xlabel='month', ylabel='discharge(mm)',
                title='Monthly mean discharge (in depth)',
                legend=True,
                time_axis=False)

    plot_multiple_X_Y(monthly_mean_multiyear.index,
                      [monthly_mean_multiyear.bias_depth],
                      ax=ax[1], fig=fig,
                      label_list=['bias'],
                      linestyle_list=['-o'],
                      xticks=True)

    refine_plot(ax[1], xlabel='month', ylabel='bias(mm)',
                title='Monthly mean bias (in depth)',
                legend=True,
                time_axis=False,
                text='mean bias = {} \npercent bias= {}%'.format(round(bias_mean_depth,3), round(percent_bias_depth,3)),
                text_position=text_position
                )

    path = os.path.join(save_folder, 'monthly_mean_bias_depth.png') if save_folder else 'monthly_mean_bias_depth.png'
    save_fig(fig, path)

    return 'monthly mean analysis done'


def get_annual_mean_analysis(DF, watershed_area,
                             text_position=[0.1, 0.8],
                             save_folder=None):

    """
    Tested with excel using DF.csv
    """
    # annual mean in discharge
    annual_mean = DF.set_index('time').resample('A-SEP').mean()
    annual_mean['bias'] = annual_mean['sim'] - annual_mean['obs']
    bias_mean = annual_mean['bias'].mean()
    percent_bias = sum(annual_mean['bias']) / sum(annual_mean['obs']) * 100

    # annual mean in depth
    annual_mean['sim_depth'] = annual_mean['sim'] * 24 * 3600 * 365.25 * 1000 * (watershed_area ** -1)
    annual_mean['obs_depth'] = annual_mean['obs'] * 24 * 3600 * 365.25 * 1000 * (watershed_area ** -1)
    annual_mean['bias_depth'] = annual_mean['sim_depth'] - annual_mean['obs_depth']
    bias_mean_depth = annual_mean['bias_depth'].mean()
    percent_bias_depth = sum(annual_mean['bias_depth']) / sum(annual_mean['obs_depth']) * 100

    # write results
    path = os.path.join(save_folder, 'annual_mean.csv') if save_folder else './annual_mean.csv'
    annual_mean.to_csv(path)
    with open(path, 'a') as my_file:
        my_file.write(
            '\nbias mean = {}'
            '\npercent bias = {}%'
            '\nbias mean depth = {}'
            '\npercent bias depth = {}%'.format(bias_mean, percent_bias, bias_mean_depth, percent_bias_depth)
        )

    # make plots
    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_X_Y(annual_mean.index.year,
                      [annual_mean.sim, annual_mean.obs],
                      ax=ax[0], fig=fig,
                      label_list=['sim', 'obs'],
                      linestyle_list=['-o', '-o'],
                      xticks=True)

    refine_plot(ax[0], xlabel='time', ylabel='discharge(cms)',
                title='Annual mean discharge',
                legend=True,
                time_axis=False
                )

    plot_multiple_X_Y(annual_mean.index.year,
                      [annual_mean.bias],
                      ax=ax[1], fig=fig,
                      label_list=['bias'],
                      linestyle_list=['-o'],
                      xticks=True
                      )

    refine_plot(ax[1], xlabel='time', ylabel='bias(cms)',
                title='Annual mean bias',
                legend=True,
                time_axis=False,
                text='mean bias = {} \npercent bias= {}%'.format(round(bias_mean,3), round(percent_bias,3)),
                text_position=text_position
                )

    path = os.path.join(save_folder, 'annual_mean_bias.png') if save_folder else 'annual_mean_bias.png'
    save_fig(fig, path)

    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_X_Y(annual_mean.index.year,
                      [annual_mean.sim_depth, annual_mean.obs_depth],
                      ax=ax[0], fig=fig,
                      xticks=True,
                      label_list=['sim', 'obs'],
                      linestyle_list=['-o', '-o']
                      )

    refine_plot(ax[0], xlabel='time', ylabel='discharge(mm)',
                title='Annual mean discharge (in depth)',
                legend=True,
                time_axis=False,
                )

    plot_multiple_X_Y(annual_mean.index.year,
                      [annual_mean.bias_depth],
                      ax=ax[1], fig=fig,
                      label_list=['bias'],
                      linestyle_list=['-o'],
                      xticks=True)

    refine_plot(ax[1], xlabel='time', ylabel='bias(mm)',
                title='Annual mean bias (in depth)',
                legend=True,
                time_axis=False,
                text='mean bias = {} \npercent bias= {}%'.format(round(bias_mean_depth, 2), round(percent_bias_depth, 2)),
                text_position=text_position
                )

    path = os.path.join(save_folder,
                        'annual_mean_bias_depth.png') if save_folder else 'annual_mean_bias_depth.png'
    save_fig(fig, path)

    return 'Annual mean analysis done'


def get_volume_error_analysis(DF, watershed_area, save_folder=None, start_month=4, end_month=7, text_position=(0.1, 0.8)):
    """
    tested the volume error in excel with monthly mean.csv
    """
    DF['sim_vol'] = DF['sim'] * 24 * 60 * 60
    DF['obs_vol'] = DF['obs'] * 24 * 60 * 60
    monthly_vol = DF.set_index('time').resample('M')['sim_vol', 'obs_vol'].sum()
    monthly_vol_subset = monthly_vol[(monthly_vol.index.month >= start_month) & (monthly_vol.index.month <= end_month)]
    monthly_vol_subset_sum = monthly_vol_subset.resample('A').sum()
    monthly_vol_subset_sum['error'] = monthly_vol_subset_sum['sim_vol'] - monthly_vol_subset_sum['obs_vol']
    volume_error = monthly_vol_subset_sum['error'].mean()
    percent_error = sum(monthly_vol_subset_sum['error']) / sum(monthly_vol_subset_sum['obs_vol']) * 100

    monthly_vol_subset_sum['sim_depth'] = monthly_vol_subset_sum['sim_vol'] / watershed_area * 1000
    monthly_vol_subset_sum['obs_depth'] = monthly_vol_subset_sum['obs_vol'] / watershed_area * 1000
    monthly_vol_subset_sum['error_depth'] = monthly_vol_subset_sum['sim_depth'] - monthly_vol_subset_sum['obs_depth']
    volume_error_depth = monthly_vol_subset_sum['error_depth'].mean()
    percent_error_depth = sum(monthly_vol_subset_sum['error_depth']) / sum(monthly_vol_subset_sum['obs_depth']) * 100

    # write volume error
    path = os.path.join(save_folder, 'monthly_volume.csv') if save_folder else './monthly_volume.csv'
    monthly_vol.to_csv(path)
    path = os.path.join(save_folder, 'volume_err.csv') if save_folder else './volume_err.csv'
    monthly_vol_subset_sum.to_csv(path)

    with open(path, 'a') as my_file:
        my_file.write(
            '\n volume error = {}'
            '\n percent error = {} '
            '\n volume error depth = {} '
            '\n percent error depth = {} '.format(volume_error, percent_error, volume_error_depth, percent_error_depth)
        )


    # make plots
    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_X_Y(monthly_vol_subset_sum.index.year,
                      [monthly_vol_subset_sum.sim_vol, monthly_vol_subset_sum.obs_vol],
                      ax=ax[0], fig=fig,
                      linestyle_list=['-o', '-o'],
                      label_list=['sim', 'obs'],
                      xticks=True)

    refine_plot(ax[0], xlabel='time', ylabel='volume(m^3)',
                title='April-July Volume',
                legend=True,
                time_axis=False,
                )

    plot_multiple_X_Y(monthly_vol_subset_sum.index.year,
                      [monthly_vol_subset_sum.error],
                      ax=ax[1], fig=fig,
                      linestyle_list=['-o'],
                      label_list=['error'],
                      xticks=True)

    refine_plot(ax[1], xlabel='time', ylabel='error(m^3)',
                title='April-July volume error',
                legend=True,
                time_axis=False,
                text='volume error = {} \npercent error= {}'.format(round(volume_error,3), round(percent_error,3)),
                text_position=text_position,
                )

    path = os.path.join(save_folder, 'volume_error.png') if save_folder else 'volume_error.png'
    save_fig(fig, path)

    # make plots
    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_X_Y(monthly_vol_subset_sum.index.year,
                      [monthly_vol_subset_sum.sim_depth, monthly_vol_subset_sum.obs_depth],
                      ax=ax[0], fig=fig,
                      linestyle_list=['-o', '-o'],
                      label_list=['sim', 'obs'],
                      xticks=True)

    refine_plot(ax[0], xlabel='time', ylabel='depth(mm)',
                title='April-July Volume (in depth)',
                legend=True,
                time_axis=False,
                )

    plot_multiple_X_Y(monthly_vol_subset_sum.index.year,
                      [monthly_vol_subset_sum.error_depth],
                      ax=ax[1], fig=fig,
                      linestyle_list=['-o'],
                      label_list=['error'],
                      xticks=True)

    refine_plot(ax[1], xlabel='time', ylabel='error in depth(mm)',
                title='April-July volume error (in depth)',
                legend=True,
                time_axis=False,
                text='volume error = {} \npercent error= {}'.format(round(volume_error_depth,2), round(percent_error_depth,2)),
                text_position=text_position,
                )

    path = os.path.join(save_folder, 'volume_error_depth.png') if save_folder else 'volume_error_depth.png'
    save_fig(fig, path)

    return 'Volume error analysis is done.'
