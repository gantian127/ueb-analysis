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

import pandas as pd
import matplotlib.pyplot as plt

from plot_SAC_utility import get_sac_ts_dataframe

# Default settings ########################################################
plt.ioff()
watershed = 'DOLC2'
watershed_area = 0

snow17_dir = r'C:\Users\jamy\Desktop\snow17'
ueb_dir = r'C:\Users\jamy\Desktop\SAC_out'

snow17_skip = 136
ueb_skip = 121

start_time = '1988-10-1'
end_time = '2010-6-30'
dt = 6

result_dir = os.path.join(os.getcwd(), 'model_mass_balance_{}_{}'.format(watershed, 'all' if end_time == '' else end_time[:4]))
if not os.path.isdir(result_dir):
    os.makedirs(result_dir)


# step 1 ueb mass balance  ##############################################
if os.path.isdir(ueb_dir):
    ts_file_list = [os.path.join(ueb_dir, name) for name in os.listdir(ueb_dir) if name[-2:] == 'ts']
    ueb_df = get_sac_ts_dataframe(ts_file_list, start_time=start_time, end_time=end_time, sim_skip=ueb_skip)
    ueb_df.columns = ['ueb_' + name if 'ueb' not in name else name for name in ueb_df.columns]

    # snow model mass balance ###########################################################
    # error = cump - swe - Wc - cumrmlt - cumEc - cumEs
    ueb_df['ueb_prcp'] = 1000 * ueb_df['ueb_P']*dt  #TODO: may need to delete 1000 after the model code update
    ueb_df['ueb_prcp_cum'] = ueb_df['ueb_cump'] # 1000*dt*ueb_df['ueb_P'].cumsum()  different from cump and smaller than cump
    ueb_df['ueb_swit_cum'] = dt*ueb_df['ueb_SWIT'].cumsum()  # different from ueb_cumMr
    ueb_df['ueb_es_cum'] = dt*ueb_df['ueb_Es'].cumsum()
    ueb_df['ueb_ec_cum'] = dt*ueb_df['ueb_Ec'].cumsum()
    ueb_df['ueb_sublimation_cum'] = ueb_df['ueb_ec_cum'] + ueb_df['ueb_es_cum']
    ueb_df['ueb_we_total'] = ueb_df['ueb_SWE'] + ueb_df['ueb_Wc']
    ueb_df['ueb_rmlt_cum'] = ueb_df['ueb_xmrg'].cumsum()
    ueb_df['ueb_snow_error'] = ueb_df['ueb_prcp_cum'] - ueb_df['ueb_rmlt_cum'] - ueb_df['ueb_we_total'] - ueb_df['ueb_sublimation_cum']

    # stat: total sublimation stats
    percent_as_sublimation = 100 * ueb_df['ueb_sublimation_cum'][-1]/ueb_df['ueb_prcp_cum'][-1]
    annual_sublimation = ueb_df['ueb_sublimation_cum'][-1]/(ueb_df.index[-1].year - ueb_df.index[0].year)  # in meter
    annual_sublimation_percent = percent_as_sublimation/(ueb_df.index[-1].year - ueb_df.index[0].year)
    with open(os.path.join(result_dir, 'sublimation_stat.txt'),'w') as f:
        f.write("\n".join([
            'percent sublimation:{} %'.format(round(percent_as_sublimation, 2)),
            'annual sublimation:{} mm'.format(round(annual_sublimation,3)),
            'annual sublimation:{} %'.format(round(annual_sublimation_percent, 2)),
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
    ueb_df.plot.area(y=['ueb_Wc','ueb_SWE'],
                     ax=ax,
                     title='UEB ground and canopy swe for {}'.format(watershed),
                     style=['whitesmoke','silver'],
                     legend=False)
    ueb_df.plot(y=['ueb_we_total'],
                   ax=ax,
                   legend=False,
                   )

    ax.legend(['ground SWE',
               'surface SWE',
               'total SWE',
              ])
    ax.set_ylabel('SWE(mm)')

    fig.savefig(os.path.join(result_dir,'ueb_swe.png'))

    # plot: sublimation
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    ueb_df.plot(y=['ueb_es_cum', 'ueb_ec_cum', 'ueb_sublimation_cum'],
                     ax=ax[0],
                     title='UEB cumulative ground and canopy sublimation for {}'.format(watershed),
                )
    ax[0].set_ylabel('SWE(mm)')

    ueb_df.plot(y=['ueb_Ec', 'ueb_Es'],
                     ax=ax[1],
                     title='UEB ground and canopy sublimation for {}'.format(watershed),
                )
    ax[1].set_ylabel('SWE(mm)')
    plt.tight_layout()

    fig.savefig(os.path.join(result_dir,'ueb_sublimation.png'))

    # plot: check cumMr, ueb_swit_cum, ueb_rmlt_cum
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df.plot(y=['ueb_swit_cum', 'ueb_cumMr', 'ueb_rmlt_cum'],
                ax=ax,
                title='UEB cumulative rain plus melt check '.format(watershed))
    fig.savefig(os.path.join(result_dir, 'ueb_check_cum_rmlt.png'))

    # plot: check cumes, ueb_es_cum
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df.plot(y=['ueb_cumes', 'ueb_es_cum'],
                ax=ax,
                title='UEB cumulative sublimation check '.format(watershed))
    fig.savefig(os.path.join(result_dir, 'ueb_check_cum_es.png'))

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
    snow17_df['snow17_prcp_cum'] = snow17_df['snow17_xmrg'].cumsum() # TODO: mass balance error check how to calculate cum prcp
    snow17_df['snow17_rmlt_cum'] = snow17_df['snow17_rmlt'].cumsum()
    snow17_df['snow17_we_total'] = snow17_df['snow17_liqw'] + snow17_df['snow17_we']
    snow17_df['snow17_snow_error'] = snow17_df['snow17_prcp_cum'] - snow17_df['snow17_rmlt_cum'] - snow17_df['snow17_we_total']

    # plot: mass balance
    fig, ax = plt.subplots(figsize=(10, 5))
    snow17_df.plot(y=['snow17_prcp_cum',
                      'snow17_rmlt_cum',
                      'snow17_we',
                      ],
                   ax=ax,
                   title='SNOW17 model mass balance for {}'.format(watershed),
                   legend=False,
                   )

    ax.legend(['cum prcpitation',
               'cum rain plus melt',
               'swe',
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
    fig, ax = plt.subplots(figsize=(10, 5))
    snow17_df.plot(y=['snow17_we', 'snow17_liqw'],
                     ax=ax,
                     title='Snow17 swe and liquid water for {}'.format(watershed),
                   )
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
    concat_df['swe_diff'] = concat_df['ueb_we_total'] - concat_df['snow17_we_total']
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_we_total',
                      'snow17_we_total'],
                   ax=ax[0],
                   title='Compare SWE between UEB and Snow17',
                   legend=False,
                   )
    ax[0].legend(['ueb SWE',
               'snow17 SWE'])
    ax[0].set_ylabel('SWE(mm)')

    concat_df.plot(y=['swe_diff'],
                   ax=ax[1],
                   title='Difference of SWE between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('SWE(mm)'.format(dt))
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_swe.png'))

    # compare ET  #####################################################
    concat_df['tet_diff'] = concat_df['ueb_tet'] - concat_df['snow17_tet']
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
    ax[0].set_ylabel('ET (mm/{})'.format(dt))

    concat_df.plot(y=['tet_diff'],
                   ax=ax[1],
                   title='Difference of tet between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('ET (mm/{})'.format(dt))
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_tet.png'))

    # compare cum total ET
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

    # compare total ET
    fig, ax = plt.subplots(2,1, figsize=(10, 8))
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

    # compare discharge  #####################################################
    concat_df['discharge_diff'] = concat_df['ueb_discharge'] - concat_df['snow17_discharge']

    # compare tet
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    concat_df.plot(y=['ueb_discharge',
                      'snow17_discharge'
                      ],
                   ax=ax[0],
                   title='Compare discharge between UEB and Snow17',
                   legend=False,
                   )
    ax[0].legend(['ueb', 'snow17'])
    ax[0].set_ylabel('discharge(cms)')

    concat_df.plot(y=['discharge_diff'],
                   ax=ax[1],
                   title='Difference of discharge between UEB and Snow17',
                   legend=False,
                   )
    ax[1].legend(['ueb - snow17'])
    ax[1].set_ylabel('discharge(cms)')
    plt.tight_layout()
    fig.savefig(os.path.join(result_dir, 'compare_discharge.png'))

    concat_df.to_csv(os.path.join(result_dir, 'concat_df.csv'))

print 'Analysis is done'