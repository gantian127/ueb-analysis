"""
This includes the utilities for SAC-SMA output plots
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import math


def plot_multiple_time_series(time, data_list, label_list,
                              fig=None, ax=None,
                              title=None,
                              xlabel=None,
                              ylaebl=None,
                              interval=1,
                              format='%Y/%m'
                              ):

    if ax is None:
        fig, ax = plt.subplots()

    for i in range(0, len(data_list)):
        ax.plot(time, data_list[i], label=label_list[i])

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


def plot_obs_vs_sim(time, sim, obs,  figsize=(15,10),
                    ts_title='Time series of observation and simulation discharge',
                    ts_xlabel='Time',
                    ts_ylabel='Discharge(cms)',
                    title='Observation vs. simulation discharge',
                    xlabel='Observation(cms)',
                    ylabel='Simulation(cms)',
                    text_position=[0.1, 0.95],
                    save_as=False):

    # calculate statistics
    stat_df = pd.DataFrame({'time': time,
                            'discharge': sim,
                            'observation': obs},
                             columns=['time', 'discharge', 'observation'])

    # rmse: sqrt(mean(sum((Qs-Qo)**2)))
    stat_df['valDiff'] = stat_df['observation'] - stat_df['discharge']
    valDiff_mean = stat_df['valDiff'].mean()
    stat_df['valDiffSq'] = stat_df['valDiff'].apply(lambda x: x**2)
    valDiffSq_mean = stat_df['valDiffSq'].mean()
    rmse = math.sqrt(valDiffSq_mean)

    # nse: 1 - sum ((Qs-Qo)**2) / sum((Qo-Qomean)**2)
    stat_df['valDiffA'] = stat_df['valDiff'].apply(lambda x: abs(x))
    valDiffA_mean = stat_df['valDiffA'].mean()
    obs_mean = stat_df['observation'].mean()
    valDiffSq_sum = stat_df['valDiffSq'].sum()

    stat_df['valDiffMean'] = stat_df['observation'].apply(lambda x: x - obs_mean)
    stat_df['valDiffSqmean'] = stat_df['valDiffMean'].apply(lambda x: x**2)
    valDiffSqmean_sum = stat_df['valDiffSqmean'].sum()

    nse = 1 - (valDiffSq_sum/valDiffSqmean_sum)
    mae = valDiffA_mean

    # correlation coefficient
    r = stat_df[['observation', 'discharge']].corr()['observation'][1]

    # plot obs vs sac time series
    fig, ax = plt.subplots(2, 1, figsize=figsize)
    plot_multiple_time_series(stat_df['time'],
                              [stat_df['observation'], stat_df['discharge']],
                              ['observation', 'simulation'],
                              ax=ax[0], fig=fig
                              )
    refine_plot(ax[0], xlabel=ts_xlabel, ylabel=ts_ylabel, title=ts_title,
                legend=True)

    # plot obs vs sac scatter plot
    ax[1].scatter(stat_df['observation'], stat_df['discharge'])
    refine_plot(ax[1], xlabel=xlabel, ylabel=ylabel, title=title,
                time_axis=False, legend=False)
    ax[1].plot([stat_df['observation'].min(), stat_df['observation'].max()],
                [stat_df['observation'].min(), stat_df['observation'].max()],
                linestyle = ':',
                color='r')

    plt.text(stat_df['observation'].max()*text_position[0], stat_df['discharge'].max()*text_position[1],
             ' RMSE = {} \n NSE = {} \n R = {} \n MAE = {}'.format(rmse, nse, r, mae), fontsize=11, color='b')

    plt.tight_layout()

    if save_as:
        save_fig(fig, save_as=save_as)

    return fig, ax
