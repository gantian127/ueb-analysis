"""
This includes the utilities for SAC-SMA output plots
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import math
from datetime import datetime, timedelta


def plot_multiple_time_series(time, data_list, label_list,
                              fig=None, ax=None,
                              title=None,
                              xlabel=None,
                              ylaebl=None,
                              xlim=None,
                              ylim=None,
                              interval=1,
                              format='%Y/%m'
                              ):

    if ax is None:
        fig, ax = plt.subplots()

    for i in range(0, len(data_list)):
        ax.plot(time, data_list[i], label=label_list[i])

    if xlim:
        ax.set_xlim(xlim[0], xlim[1])

    if ylim:
        ax.set_ylim(ylim[0], ylim[1])

    return fig, ax


def refine_plot(ax, xlabel='', ylabel='', title='', interval=1, format='%Y/%m', legend=True, time_axis=True):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if time_axis:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(format))

    if legend:
        ax.legend(loc='best')


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
                x = x[:-2] + x[-2:].replace('24', '23')
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
    df = pd.DataFrame(data={'time': time, 'data': data}, columns=['time', 'data'])
    data = df.set_index('time').groupby(pd.TimeGrouper(freq=freq))['data'].mean()

    return data.tolist(), data.index.values


def get_rit_discharge(discharge, skiprows=3, start_date_obj=None, end_date_obj=None,
                      unit_factor=0.0283168, unit_offset=0):
    rti_discharge = pd.read_csv(discharge, skiprows=skiprows, header=None, names=['raw'])  # time column is used as index in dataframe
    if start_date_obj and end_date_obj:
        start_date = datetime.strftime(start_date_obj, '%Y-%m-%d')
        end_date = datetime.strftime(end_date_obj + timedelta(days=1), '%Y-%m-%d')
        discharge = rti_discharge.ix[start_date:end_date]['raw'].apply(lambda x: x * unit_factor + unit_offset).tolist()
    else:
        discharge = rti_discharge['raw'].apply(lambda x: x * unit_factor + unit_offset).tolist()

    return discharge


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

    return {'rmse': rmse, 'nse': nse, 'mae': mae, 'r': r}


def plot_obs_vs_sim(time, sim, obs,  figsize=(15,10),
                    ts_title='Time series of observation and simulation discharge',
                    ts_xlabel='Time',
                    ts_ylabel='Discharge(cms)',
                    ts_xlim=None,
                    ts_ylim=None,
                    title='Observation vs. simulation discharge',
                    xlabel='Observation(cms)',
                    ylabel='Simulation(cms)',
                    xlim=None,
                    ylim=None,
                    text_position=[0.1, 0.90],
                    month_interval=1,
                    format='%Y',
                    save_as=False
                    ):

    # calculate statistics
    stat_df = pd.DataFrame({'time': time,
                            'discharge': sim,
                            'observation': obs},
                             columns=['time', 'discharge', 'observation'])
    #
    # # rmse: sqrt(mean(sum((Qs-Qo)**2)))
    # stat_df['valDiff'] = stat_df['observation'] - stat_df['discharge']
    # valDiff_mean = stat_df['valDiff'].mean()
    # stat_df['valDiffSq'] = stat_df['valDiff'].apply(lambda x: x**2)
    # valDiffSq_mean = stat_df['valDiffSq'].mean()
    # rmse = math.sqrt(valDiffSq_mean)
    #
    # # nse: 1 - sum ((Qs-Qo)**2) / sum((Qo-Qomean)**2)
    # stat_df['valDiffA'] = stat_df['valDiff'].apply(lambda x: abs(x))
    # valDiffA_mean = stat_df['valDiffA'].mean()
    # obs_mean = stat_df['observation'].mean()
    # valDiffSq_sum = stat_df['valDiffSq'].sum()
    #
    # stat_df['valDiffMean'] = stat_df['observation'].apply(lambda x: x - obs_mean)
    # stat_df['valDiffSqmean'] = stat_df['valDiffMean'].apply(lambda x: x**2)
    # valDiffSqmean_sum = stat_df['valDiffSqmean'].sum()
    #
    # nse = 1 - (valDiffSq_sum/valDiffSqmean_sum)
    # mae = valDiffA_mean
    #
    # # correlation coefficient
    # r = stat_df[['observation', 'discharge']].corr()['observation'][1]

    statistics = get_statistics(stat_df['discharge'], stat_df['observation'])

    # plot obs vs sac time series
    fig, ax = plt.subplots(2, 1, figsize=figsize)
    plot_multiple_time_series(stat_df['time'],
                              [stat_df['observation'], stat_df['discharge']],
                              ['observation', 'simulation'],
                              ax=ax[0], fig=fig,
                              xlim=ts_xlim,
                              ylim=ts_ylim,
                              )
    refine_plot(ax[0], xlabel=ts_xlabel, ylabel=ts_ylabel, title=ts_title,
                legend=True, interval=month_interval, format=format)

    # plot obs vs sac scatter plot
    ax[1].scatter(stat_df['observation'], stat_df['discharge'])
    refine_plot(ax[1], xlabel=xlabel, ylabel=ylabel, title=title,
                time_axis=False, legend=False)
    ax[1].plot([stat_df['observation'].min(), stat_df['observation'].max()],
                [stat_df['observation'].min(), stat_df['observation'].max()],
                linestyle = ':',
                color='r',
                )
    if xlim:
        ax[1].set_xlim(xlim[0], xlim[1])

    if ylim:
        ax[1].set_ylim(ylim[0], ylim[1])

    plt.text(stat_df['observation'].max()*text_position[0], stat_df['discharge'].max()*text_position[1],
             ' RMSE = {} \n NSE = {} \n R = {} \n MAE = {}'.format(statistics['rmse'], statistics['nse'],
                                                                   statistics['r'], statistics['mae']),
             fontsize=11, color='b')

    plt.tight_layout()

    if save_as:
        save_fig(fig, save_as=save_as)

    return fig, ax
