"""
This is using the RDHM time series to analyze the mass balance of snow model (snow17 vs ueb workflow)

requirements:
- put utility py file
- the output should be from the updated code that has mm/dt or mm units.

step:
- check ueb mass balance: snow/ sac/ snow+sac
- check snow17 mass balance: snow / sac / snow+sac
- model compare: prcp, SWE, total et (ET+sublimation vs ET only)

"""

import os
import calendar

import pandas as pd
import matplotlib.pyplot as plt

from plot_SAC_utility import get_sac_ts_dataframe, get_snotel_swe_df, get_obs_dataframe

# Default settings ########################################################
plt.ioff()
watershed = 'MPHC2'

snow17_dir = r'D:\Research_Data\Mcphee_MPHC2\snow17_best_time_series'
ueb_dir = r'D:\Research_Data\Mcphee_MPHC2\ueb_best_time_series_2005'
snotel_folder_path = r'D:\Research_Data\Mcphee_MPHC2\snotel_swe'
obs_discharge_path = r'D:\Research_Data\Mcphee_MPHC2\MPHC2L_F.QME'

snow17_skip = 136
ueb_skip = 121

start_time = '1989-10-1'
end_time = '2005-9-30'
dt = 6

result_dir = os.path.join(os.getcwd(), 'model_mass_balance_{}_{}'.format(watershed, 'all' if end_time == '' else start_time[:4] + end_time[:4]))
if not os.path.isdir(result_dir):
    os.makedirs(result_dir)


# step 1 ueb mass balance  ##############################################
if os.path.isdir(ueb_dir):
    ts_file_list = [os.path.join(ueb_dir, name) for name in os.listdir(ueb_dir) if name[-2:] == 'ts']
    ueb_df = get_sac_ts_dataframe(ts_file_list, start_time=start_time, end_time=end_time, sim_skip=ueb_skip)
    ueb_df.columns = ['ueb_' + name if 'ueb' not in name else name for name in ueb_df.columns]

    # snow model mass balance ###########################################################
    # error = cump - swe - Wc - cumrmlt - cumEc - cumEs
    ueb_df['ueb_prcp'] = ueb_df['uebPrec'] #ueb_df['uebPrec']  # or ueb_df['ueb_P']*dt but this has small system error. uebPrec is exactly same as snow17 xmrg
    ueb_df['ueb_prcp_cum'] = ueb_df['uebPrec'].cumsum() #ueb_df['uebPrec'].cumsum()  # or use this dt*ueb_df['ueb_P'].cumsum() but this has small system error.
    ueb_df['ueb_swit_cum'] = dt*ueb_df['ueb_SWIT'].cumsum()
    ueb_df['ueb_es_cum'] = dt*ueb_df['ueb_Es'].cumsum()
    ueb_df['ueb_ec_cum'] = dt*ueb_df['ueb_Ec'].cumsum()
    ueb_df['ueb_sublimation_cum'] = ueb_df['ueb_ec_cum'] + ueb_df['ueb_es_cum']
    ueb_df['ueb_we_total'] = ueb_df['ueb_SWE'] + ueb_df['ueb_Wc']
    ueb_df['ueb_rmlt_cum'] = ueb_df['ueb_xmrg'].cumsum()
    ueb_df['ueb_snow_error'] = ueb_df['ueb_prcp_cum'] - ueb_df['ueb_rmlt_cum'] - ueb_df['ueb_we_total'] - ueb_df['ueb_sublimation_cum']


    # stat: total sublimation stats
    percent_as_sublimation = 100 * ueb_df['ueb_sublimation_cum'][-1]/ueb_df['ueb_prcp_cum'][-1]
    annual_sublimation = ueb_df['ueb_sublimation_cum'][-1]/(ueb_df.index[-1].year - ueb_df.index[0].year)  # in meter
    annual_canopy_sublimation = ueb_df['ueb_ec_cum'][-1]/(ueb_df.index[-1].year - ueb_df.index[0].year)
    annual_ground_sublimation = ueb_df['ueb_es_cum'][-1]/(ueb_df.index[-1].year - ueb_df.index[0].year)
    percent_canopy_sublimation = 100 * ueb_df['ueb_ec_cum'][-1]/ueb_df['ueb_sublimation_cum'][-1]
    percent_ground_sublimation = 100 * ueb_df['ueb_es_cum'][-1]/ueb_df['ueb_sublimation_cum'][-1]

    with open(os.path.join(result_dir, 'sublimation_stat.txt'),'w') as f:
        f.write("\n".join([
            'percent sublimation:{} %'.format(round(percent_as_sublimation, 2)),
            'annual sublimation:{} mm'.format(round(annual_sublimation, 3)),
            'annual canopy sublimation:{} mm'.format(round(annual_canopy_sublimation, 3)),
            'annual canopy sublimation:{} %'.format(round(percent_canopy_sublimation, 2)),
            'annual ground sublimation:{} mm'.format(round(annual_ground_sublimation, 3)),
            'annual ground sublimation:{} %'.format(round(percent_ground_sublimation, 2)),
        ]))

    # plot: mass balance and error
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df.plot(y=['ueb_prcp_cum',
                   'ueb_rmlt_cum',
                   'ueb_sublimation_cum',
                   'ueb_we_total',
                   ],
                ax=ax,
                title='UEB model mass balance for {}'.format(watershed),
                legend=False,
                )
    ax.legend(['cum prcpitation',
               'cum rain plus melt',
               'cum sublimation',
               'total swe',
               ])
    ax.set_ylabel('water input/output (mm)')
    fig.savefig(os.path.join(result_dir, 'ueb_snow_mass_balance.png'))

    # plot: mass balance error
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df.plot(y='ueb_snow_error',
                ax=ax,
                title='UEB model mass balance error for {}'.format(watershed),
                legend=False,
                )
    ax.set_ylabel('error (mm)')
    fig.savefig(os.path.join(result_dir, 'ueb_snow_error.png'))

    # plot: SWE
    fig, ax = plt.subplots(figsize=(10,5))

    ueb_df.plot.area(y=['ueb_Wc', 'ueb_SWE'],
                     ax=ax,
                     style=['grey', 'silver'],
                     title='UEB ground and canopy swe for {}'.format(watershed),
                     )
    ueb_df.plot(y='ueb_we_total', ax=ax)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(labels=['total swe', 'canopy swe', 'ground swe'], handles=handles)
    ax.set_ylabel('SWE(mm)')
    fig.savefig(os.path.join(result_dir, 'ueb_swe.png'))

    # plot: sublimation
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    ueb_df.plot(y=['ueb_es_cum', 'ueb_ec_cum', 'ueb_sublimation_cum'],
                     ax=ax[0],
                     title='UEB cumulative ground and canopy sublimation for {}'.format(watershed),
                )
    ax[0].set_ylabel('cumulative sublimation(mm)')
    ax[0].legend(['ground', 'canopy', 'total'])

    ueb_df.plot(y=['ueb_Ec', 'ueb_Es'],
                     ax=ax[1],
                     title='UEB ground and canopy sublimation for {}'.format(watershed),
                )
    ax[1].set_ylabel('sublimation(mm/{}hr)'.format(dt))
    ax[1].legend(['canopy', 'ground', ])
    plt.tight_layout()

    fig.savefig(os.path.join(result_dir,'ueb_sublimation.png'))

    # plot: check cumMr, ueb_swit_cum, ueb_rmlt_cum
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df['ueb_cumMr'] = ueb_df['ueb_cumMr'] - ueb_df['ueb_cumMr'][0]
    ueb_df.plot(y=['ueb_swit_cum', 'ueb_cumMr', 'ueb_rmlt_cum'],
                ax=ax,
                title='UEB cumulative rain plus melt check '.format(watershed))
    fig.savefig(os.path.join(result_dir, 'ueb_check_cum_rmlt.png'))

    # plot: check cumes, ueb_es_cum
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df['ueb_cumes'] = ueb_df['ueb_cumes'] - ueb_df['ueb_cumes'][0]
    ueb_df.plot(y=['ueb_cumes', 'ueb_es_cum'],
                ax=ax,
                title='UEB cumulative sublimation check '.format(watershed))
    fig.savefig(os.path.join(result_dir, 'ueb_check_cum_es.png'))

    # plot: check uebPrec, cump
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df['ueb_cump'] = ueb_df['ueb_cump'] - ueb_df['ueb_cump'][0]
    ueb_df.plot(y=['ueb_cump','ueb_prcp_cum'],
                ax=ax,
                title='UEB cumulative precipitation check'.format(watershed))
    ax.set_ylabel('cumulative precipitation (mm)')
    fig.savefig(os.path.join(result_dir, 'ueb_check_cum_prcp.png'))

    # plot: check errMB, ueb_snow_error
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df['ueb_errMB'] = ueb_df['ueb_errMB']*1000 - ueb_df['ueb_errMB'][0]*1000
    ueb_df.plot(y=['ueb_errMB', 'ueb_snow_error'],
                ax=ax,
                title='UEB cumulative snow model error'.format(watershed))
    ax.set_ylabel('cumulative error (mm)')
    fig.savefig(os.path.join(result_dir, 'ueb_check_errMB.png'))

    # sac mass balance ################################################################
    # error = cumrmlt - cumsubflow - cumsurflow - storage change - cumET
    ueb_df['ueb_total_storage'] = ueb_df['ueb_real_lzfpc'] + ueb_df['ueb_real_lzfsc'] + ueb_df['ueb_real_lztwc'] \
                                  + ueb_df['ueb_real_uzfwc'] + ueb_df['ueb_real_uztwc']
    ueb_df['ueb_storage_change'] = ueb_df['ueb_total_storage'] - ueb_df['ueb_total_storage'][0]
    ueb_df['ueb_tet_cum'] = ueb_df['ueb_tet'].cumsum()
    ueb_df['ueb_subsurfaceFlow_cum'] = ueb_df['ueb_subsurfaceFlow'].cumsum()
    ueb_df['ueb_surfaceFlow_cum'] = ueb_df['ueb_surfaceFlow'].cumsum()
    ueb_df['ueb_sac_error'] = ueb_df['ueb_rmlt_cum'] - ueb_df['ueb_storage_change'] - ueb_df['ueb_tet_cum'] \
                              - ueb_df['ueb_surfaceFlow_cum'] - ueb_df['ueb_subsurfaceFlow_cum']
    ueb_df['ueb_total_et_cum'] = ueb_df['ueb_sublimation_cum'] + ueb_df['ueb_tet_cum']
    ueb_df['ueb_total_et'] = ueb_df['ueb_Es']*dt + ueb_df['ueb_Ec']*dt + ueb_df['ueb_tet']
    ueb_df['ueb_total_runoff'] = ueb_df['ueb_surfaceFlow'] = ueb_df['ueb_subsurfaceFlow']

    # plot: mass balance and error
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df.plot(y=['ueb_rmlt_cum',
                   'ueb_storage_change',
                   'ueb_tet_cum',
                   'ueb_surfaceFlow_cum',
                   'ueb_subsurfaceFlow_cum',
                   ],
                ax=ax,
                title='SAC-SMA model mass balance for {}(UEB+SAC workflow)'.format(watershed),
                legend=False,
                )
    ax.legend([
               'cum rain plus melt',
               'water storage change',
               'cum ET',
               'cum surfaceFlow',
               'cum subsurfaceFlow'
              ])
    ax.set_ylabel('water input/output (mm)')
    fig.savefig(os.path.join(result_dir, 'ueb_sac_mass_balance.png'))

    # plot: mass balance error
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df.plot(y='ueb_sac_error',
                ax=ax,
                title='SAC-SMA model mass balance error for {} (UEB+SAC workflow)'.format(watershed),
                legend=False,
                )
    ax.set_ylabel('error (mm)')
    fig.savefig(os.path.join(result_dir, 'ueb_sac_error.png'))

    ueb_df.to_csv(os.path.join(result_dir, 'ueb_df.csv'))


# step 2 snow17 mass balance #########################################
if os.path.isdir(snow17_dir):
    ts_file_list = [os.path.join(snow17_dir, name) for name in os.listdir(snow17_dir) if name[-2:] == 'ts']
    snow17_df = get_sac_ts_dataframe(ts_file_list, start_time=start_time, end_time=end_time, sim_skip=snow17_skip)
    snow17_df.columns = ['snow17_'+name if 'snow17' not in name else name for name in snow17_df.columns]

    # snow model mass balance #################################################
    # error = cump - cumrmlt - swe
    snow17_df['snow17_prcp_cum'] = snow17_df['snow17_xmrg'].cumsum()
    snow17_df['snow17_rmlt_cum'] = snow17_df['snow17_rmlt'].cumsum()
    snow17_df['snow17_we_total'] = snow17_df['snow17_liqw'] + snow17_df['snow17_we']
    snow17_df['snow17_snow_error'] = snow17_df['snow17_prcp_cum'] - snow17_df['snow17_rmlt_cum'] - snow17_df['snow17_we_total']

    # plot: mass balance
    fig, ax = plt.subplots(figsize=(10, 5))
    snow17_df.plot(y=['snow17_prcp_cum',
                      'snow17_rmlt_cum',
                      'snow17_we_total',
                      ],
                   ax=ax,
                   title='SNOW17 model mass balance for {}'.format(watershed),
                   legend=False,
                   )

    ax.legend(['cum prcpitation',
               'cum rain plus melt',
               'total swe',
               ]
              )
    ax.set_ylabel('water input/output (mm)')
    fig.savefig(os.path.join(result_dir, 'snow17_snow_mass_balance.png'))

    # plot: mass balance error
    fig, ax = plt.subplots(figsize=(10, 5))
    snow17_df.plot(y='snow17_snow_error',
                   ax=ax,
                   title='Snow17 model mass balance error for {}'.format(watershed),
                   legend=False,
                   )
    ax.set_ylabel('error (mm)')
    fig.savefig(os.path.join(result_dir, 'snow17_snow_error.png'))

    # plot: SWE
    fig, ax = plt.subplots(figsize=(10,5))
    snow17_df.plot.area(y=['snow17_liqw', 'snow17_we'],
                     ax=ax,
                     style=['grey', 'silver'],
                     title='Snow17 swe and liquid water for {}'.format(watershed),
                     )
    snow17_df.plot(y='snow17_we_total', ax=ax)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(labels=['total swe', 'liqw', 'we'], handles=handles)
    ax.set_ylabel('SWE(mm)')
    fig.savefig(os.path.join(result_dir, 'snow17_we.png'))

    # sac mass balance ################################################################
    # error = cumrmlt - cumsubflow - cumsurflow - storage change - cumET
    snow17_df['snow17_total_storage'] = snow17_df['snow17_real_lzfpc'] + snow17_df['snow17_real_lzfsc'] + snow17_df['snow17_real_lztwc'] \
                                  + snow17_df['snow17_real_uzfwc'] + snow17_df['snow17_real_uztwc']
    snow17_df['snow17_storage_change'] = snow17_df['snow17_total_storage'] - snow17_df['snow17_total_storage'][0]
    snow17_df['snow17_tet_cum'] = snow17_df['snow17_tet'].cumsum()
    snow17_df['snow17_subsurfaceFlow_cum'] = snow17_df['snow17_subsurfaceFlow'].cumsum()
    snow17_df['snow17_surfaceFlow_cum'] = snow17_df['snow17_surfaceFlow'].cumsum()
    snow17_df['snow17_sac_error'] = snow17_df['snow17_rmlt_cum'] - snow17_df['snow17_storage_change'] - snow17_df['snow17_tet_cum'] \
                                    - snow17_df['snow17_surfaceFlow_cum'] - snow17_df['snow17_subsurfaceFlow_cum']
    snow17_df['snow17_total_runoff'] = snow17_df['snow17_surfaceFlow'] = snow17_df['snow17_subsurfaceFlow']

    # plot: mass balance and error
    fig, ax = plt.subplots(figsize=(10, 5))
    snow17_df.plot(y=[ 'snow17_rmlt_cum',
                       'snow17_storage_change',
                       'snow17_tet_cum',
                       'snow17_surfaceFlow_cum',
                       'snow17_subsurfaceFlow_cum',
                      ],
                    ax=ax,
                    title='SAC-SMA model mass balance for {}(snow17+SAC workflow)'.format(watershed),
                    legend=False,
                )
    ax.legend([
               'cum rain plus melt',
               'water storage change',
               'cum ET',
               'cum surfaceFlow',
               'cum subsurfaceFlow'
              ])
    ax.set_ylabel('water input/output (mm)')
    fig.savefig(os.path.join(result_dir, 'snow17_sac_mass_balance.png'))

    # plot: mass balance error
    fig, ax = plt.subplots(figsize=(10, 5))
    snow17_df.plot(y='snow17_sac_error',
                   ax=ax,
                   title='SAC-SMA model mass balance error for {} (snow17+SAC workflow)'.format(watershed),
                   legend=False,
                   )
    ax.set_ylabel('error (mm)')
    fig.savefig(os.path.join(result_dir, 'snow17_sac_error.png'))

    snow17_df.to_csv(os.path.join(result_dir, 'snow17_df.csv'))


# step 3 Model compare  #################################################
if os.path.isdir(ueb_dir) and os.path.isdir(snow17_dir):
    concat_df = pd.concat([ueb_df, snow17_df], axis=1)

    # compare prcp #############################################################
    # prcp compare
    concat_df['prcp_diff'] = concat_df['ueb_prcp'] - concat_df['snow17_xmrg']
    concat_df['prcp_cum_diff'] = concat_df['ueb_prcp_cum'] - concat_df['snow17_prcp_cum']
    fig, ax = plt.subplots(2,1, figsize=(10, 8))
    concat_df.plot(y=['ueb_prcp',
                      'snow17_xmrg'
                      ],
                   ax=ax[0],
                   title='Compare precipitation between UEB and Snow17',
                   legend=False,
                   )

    ax[0].legend(['ueb', 'snow17'])
    ax[0].set_ylabel('prec(mm/{}hr)'.format(dt))

    concat_df.plot(y=['prcp_diff'],
                   ax=ax[1],
                   title='Difference of precipitation between UEB and Snow17',
                   legend=False,
                   )
    ax[1].set_ylabel('prec(mm/{}hr)'.format(dt))
    ax[1].legend(['ueb-snow17'])
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_prcp.png'))

    # cum prcp compare
    fig, ax = plt.subplots(2,1, figsize=(10, 8))
    concat_df.plot(y=['ueb_prcp_cum',
                      'snow17_prcp_cum'
                      ],
                   ax=ax[0],
                   title='Compare cumulative precipitation between UEB and Snow17',
                   legend=False,
                   )

    ax[0].legend(['ueb', 'snow17'])
    ax[0].set_ylabel('water input(mm)')

    concat_df.plot(y=['prcp_cum_diff'],
                   ax=ax[1],
                   title='Difference of cumulative precipitation between UEB and Snow17',
                   legend=False,
                   )
    ax[1].set_ylabel('water input(mm)')
    ax[1].legend(['ueb-snow17'])
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_cum_prcp.png'))

    # compare SWE  #####################################################
    # compare model swe
    concat_df['swe_diff'] = concat_df['ueb_we_total'] - concat_df['snow17_we_total']
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_we_total',
                      'snow17_we_total'],
                   ax=ax[0],
                   title='Compare SWE between UEB and Snow17',
                   legend=False,
                   )
    ax[0].legend(['ueb SWE', 'snow17 SWE'])
    ax[0].set_ylabel('SWE(mm)')

    concat_df.plot(y=['swe_diff'],
                   ax=ax[1],
                   title='Difference of SWE between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('SWE(mm)'.format(dt))
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_swe_model.png'))

    # compare model vs snotel obs swe
    if snotel_folder_path:
        swe_file_list = [os.path.join(snotel_folder_path, file_name) for file_name in os.listdir(snotel_folder_path)]
        snotel_df = get_snotel_swe_df(swe_file_list, start_time=start_time, end_time=end_time)
        fig, ax = plt.subplots(figsize=(10, 8))

        concat_df.plot(y=['ueb_we_total',
                          'snow17_we_total'],
                       ax=ax,
                       title='Compare model SWE with SNOTEL SWE',
                       legend=True,
                       )
        snotel_df.plot(ax=ax,
                       legend=True,
                       style=[':']*len(snotel_df.columns),
                       )
        ax.set_ylabel('SWE(mm)')
        fig.savefig(os.path.join(result_dir, 'compare_swe_snotel.png'))

    # compare ET  #####################################################
    concat_df['tet_diff'] = concat_df['ueb_tet'] - concat_df['snow17_tet']
    concat_df['tet_cum_diff'] = concat_df['ueb_tet_cum'] - concat_df['snow17_tet_cum']
    concat_df['total_et_cum_diff'] = concat_df['ueb_total_et_cum'] - concat_df['snow17_tet_cum']
    concat_df['total_et_diff'] = concat_df['ueb_total_et'] - concat_df['snow17_tet']

    # compare tet
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_tet',
                      'snow17_tet'
                      ],
                   ax=ax[0],
                   title='Compare tet between UEB and Snow17',
                   legend=False,
                   )
    ax[0].legend(['ueb', 'snow17'])
    ax[0].set_ylabel('ET (mm/{}hr)'.format(dt))

    concat_df.plot(y=['tet_diff'],
                   ax=ax[1],
                   title='Difference of tet between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('ET (mm/{}hr)'.format(dt))
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_tet.png'))

    # compare cum tet: all years
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_tet_cum',
                      'snow17_tet_cum'
                      ],
                   ax=ax[0],
                   title='Compare cumulative tet between UEB and Snow17',
                   legend=False,
                   )
    ax[0].legend(['ueb', 'snow17'])
    ax[0].set_ylabel('cumulative ET (mm)')

    concat_df.plot(y=['tet_cum_diff'],
                   ax=ax[1],
                   title='Difference of cumulative tet between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('cumulative ET (mm)')
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_cum_tet.png'))

    # compare cum tet: each years time series
    concat_df['ueb_tet_cum_yearly'] = concat_df.groupby(pd.Grouper(freq='A-Sep'))['ueb_tet'].cumsum()
    concat_df['snow17_tet_cum_yearly'] = concat_df.groupby(pd.Grouper(freq='A-Sep'))['snow17_tet'].cumsum()
    annual_tet_cum = pd.DataFrame(columns=['snow17', 'ueb'])

    fig, ax = plt.subplots(figsize=(10, 6))  # time series plots
    for i, group in concat_df.groupby(pd.Grouper(freq='A-Sep')):
        y1 = group['ueb_tet_cum_yearly']
        y2 = group['snow17_tet_cum_yearly']
        x = range(0, len(group))
        ax.plot(x, y1, 'g-',
                x, y2, 'c:',
                # alpha=0.7,
                )
        annual_tet_cum.at[int(i.year)] = [group['snow17_tet_cum_yearly'].ix[-1], group['ueb_tet_cum_yearly'].ix[-1]]

    ax.set_title('Annual cumulative tet compare between UEB and snow17 at {}'.format(watershed))
    ax.set_ylabel('Cumulative ET (mm)')
    ax.set_xlabel('Month')
    ax.legend(['ueb', 'snow17'])

    x_ticks = []
    x_ticklabels = []
    month = [x[:3].upper() for x in calendar.month_name if x]
    for index in group.index:
        if index.day == 1 and index.hour == 6:
            x_ticks.append(group.index.get_loc(index))
            x_ticklabels.append(month[index.month-1])
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_ticklabels)
    fig.savefig(os.path.join(result_dir, 'compare_cum_tet_annual_ts.png'))

    annual_tet_cum['diff'] = annual_tet_cum['snow17'] - annual_tet_cum['ueb']
    percent_differnce = annual_tet_cum['snow17'].sum() - annual_tet_cum['ueb'].sum()
    fig, ax = plt.subplots(2, 1, figsize=(13, 10))  # bar plot
    annual_tet_cum.plot.bar(y=['snow17',
                                'ueb'],
                                 ax=ax[0],
                                 title='Annual cumulative total ET from UEB and Snow17',
                                 legend=True,
                                 rot=0,
                                 )
    ax[0].set_ylabel('Cumulative ET (mm)')

    annual_tet_cum.plot.bar(y=['diff'],
                            ax=ax[1],
                            title='Difference of the cumulative total ET from UEB and Snow17',
                            rot=0,
                            )
    percent_difference = 100*annual_tet_cum['diff'].sum()/annual_tet_cum['snow17'].sum()
    ax[1].text(0.02, 0.9,
               'percent difference = {}%'.format(round(percent_difference,2)),
                transform=ax[1].transAxes, size=9)
    ax[1].legend(['snow17-ueb'])
    ax[1].set_xlabel('water year')
    plt.tight_layout()

    fig.savefig(os.path.join(result_dir, 'compare_cum_tet_bar.png'))
    annual_tet_cum.to_csv(os.path.join(result_dir, 'cum_tet_annual.csv'))

    # compare cum total ET: all years
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_total_et_cum',
                      'snow17_tet_cum'
                      ],
                   ax=ax[0],
                   title='Compare cumulative total ET between UEB and Snow17',
                   legend=False,
                   )
    ax[0].legend(['ueb', 'snow17'])
    ax[0].set_ylabel('Cumulative ET (mm)')

    concat_df.plot(y=['total_et_cum_diff'],
                   ax=ax[1],
                   title='Difference of total ET between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('Cumulative ET (mm)')
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_cum_total_et.png'))

    # compare cum total ET: each years time series
    concat_df['ueb_total_et_cum_yearly'] = concat_df.groupby(pd.Grouper(freq='A-Sep'))['ueb_total_et'].cumsum()
    concat_df['snow17_total_et_cum_yearly'] = concat_df.groupby(pd.Grouper(freq='A-Sep'))['snow17_tet'].cumsum()
    annual_total_et_cum = pd.DataFrame(columns=['snow17','ueb'])

    fig, ax = plt.subplots(figsize=(10, 6))  # time series plots
    for i, group in concat_df.groupby(pd.Grouper(freq='A-Sep')):
        y1 = group['ueb_total_et_cum_yearly']
        y2 = group['snow17_total_et_cum_yearly']
        x = range(0,len(group))
        ax.plot(x, y1, 'g-',
                x, y2, 'c:',
                # alpha=0.7,
                )
        annual_total_et_cum.at[int(i.year)] = [group['snow17_total_et_cum_yearly'].ix[-1], group['ueb_total_et_cum_yearly'].ix[-1]]

    ax.set_title('Annual cumulative total ET compare between UEB and snow17 at {}'.format(watershed))
    ax.set_ylabel('Cumulative total ET (mm)')
    ax.set_xlabel('Month')  # TODO the xlabel is not done
    ax.legend(['ueb', 'snow17'])

    x_ticks = []
    x_ticklabels = []
    month = [x[:3].upper() for x in calendar.month_name if x]
    for index in group.index:
        if index.day == 1 and index.hour == 6:
            x_ticks.append(group.index.get_loc(index))
            x_ticklabels.append(month[index.month-1])
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_ticklabels)
    fig.savefig(os.path.join(result_dir, 'compare_cum_total_et_annual_ts.png'))

    annual_total_et_cum['diff'] = annual_total_et_cum['snow17'] - annual_total_et_cum['ueb']
    percent_differnce = annual_total_et_cum['snow17'].sum() - annual_total_et_cum['ueb'].sum()
    fig, ax = plt.subplots(2, 1, figsize=(13, 10))  # bar plot
    annual_total_et_cum.plot.bar(y=['snow17',
                                    'ueb'],
                                 ax=ax[0],
                                 title='Annual cumulative total ET from UEB and Snow17',
                                 legend=True,
                                 rot=0,
                                 )
    ax[0].set_ylabel('Cumulative ET (mm)')

    annual_total_et_cum.plot.bar(y=['diff'],
                                     ax=ax[1],
                                     title='Difference of the cumulative total ET from UEB and Snow17',
                                     rot=0,
                                 )
    percent_difference = 100*annual_total_et_cum['diff'].sum()/annual_total_et_cum['snow17'].sum()
    ax[1].text(0.02, 0.9,
               'percent difference = {}%'.format(round(percent_difference,2)),
                transform=ax[1].transAxes, size=9)
    ax[1].legend(['snow17-ueb'])
    ax[1].set_xlabel('water year')
    plt.tight_layout()

    fig.savefig(os.path.join(result_dir, 'compare_cum_total_et_bar.png'))
    annual_total_et_cum.to_csv(os.path.join(result_dir, 'cum_total_et_annual.csv'))

    # compare total ET
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_total_et',
                      'snow17_tet'
                      ],
                   ax=ax[0],
                   title='Compare total ET between UEB and Snow17',
                   legend=False,
                   )
    ax[0].legend(['ueb', 'snow17'])
    ax[0].set_ylabel('ET(mm/{}hr)'.format(dt))

    concat_df.plot(y=['total_et_diff'],
                   ax=ax[1],
                   title='Difference of total ET between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('ET(mm/{}hr'.format(dt))
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_total_et.png'))

    # combine cumulative snow17 tet, ueb tet and total ET
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_total_et_cum',
                      'ueb_tet_cum',
                      'snow17_tet_cum',
                      ],
                   ax=ax[0],
                   title='Compare cumulative total ET between UEB and Snow17',
                   legend=False,
                   )
    ax[0].legend(['ueb cumulative total ET', 'ueb cumulative ET', 'snow17 cumulative total ET'])
    ax[0].set_ylabel('Cumulative ET (mm)')

    concat_df.plot(y=['total_et_cum_diff',
                      'tet_cum_diff'],
                   ax=ax[1],
                   title='Difference of total ET between UEB and Snow17 (UEB - Snow17)',
                   legend=False,
                   )
    ax[1].legend(['cumulative total ET', 'cumulative ET'])
    ax[1].set_ylabel('Cumulative ET (mm)')
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_combine_ET.png'))

    # compare discharge  #####################################################

    # compare discharge with obs.
    concat_df['discharge_diff'] = concat_df['ueb_discharge'] - concat_df['snow17_discharge']

    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_discharge',
                      'snow17_discharge'
                      ],
                   ax=ax[0],
                   style=['-', ':'],
                   title='Compare discharge between UEB and Snow17',
                   )
    ax[0].set_ylabel('discharge(cms)')

    if obs_discharge_path:
        obs_discharge = get_obs_dataframe(obs_discharge_path, start_time=start_time, end_time=end_time)
        obs_discharge.plot.area(ax=ax[0],alpha=0.3)

    concat_df.plot(y=['discharge_diff'],
                   ax=ax[1],
                   title='Difference of discharge between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('discharge(cms)')
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_discharge.png'))

    # combine swe with discharge
    fig, ax = plt.subplots(figsize=(12,6))
    ax1 = ax.twinx()
    ax1.margins(0)
    concat_df.plot.area(y=['ueb_we_total',
                          'snow17_we_total'],
                   ax=ax,
                   title='Compare SWE and discharge between UEB and Snow17',
                   legend=False,
                   style=['black','silver'],
                   stacked=False,
                   )
    ax.legend(['ueb_swe', 'snow17_swe'], loc='upper left')
    ax.set_ylabel('SWE(mm)')

    concat_df.plot(y=['ueb_discharge','snow17_discharge'],
                   ax=ax1,
                   )
    # ax1.legend(['ueb_discharge', 'snow17_discharge'], loc='upper right')
    ax1.set_ylabel('discharge(cms)')

    if obs_discharge_path:
        obs_discharge.plot(ax=ax1, style='g:')

    fig.savefig(os.path.join(result_dir,'compare_combine_swe_discharge.png'))

    concat_df.to_csv(os.path.join(result_dir, 'concat_df.csv'))

print 'Analysis is done'