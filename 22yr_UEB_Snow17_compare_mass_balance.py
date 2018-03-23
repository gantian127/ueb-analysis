"""
This is using the RDHM time series to analyze the mass balance of snow model (snow17 vs ueb workflow)

requirements:
- put utility py file
- the output should be from the old code that has m/dt or m units.

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
watershed = 'DOLC2'
watershed_area = 0

snow17_dir = 'invalid'
ueb_dir = r'C:\Users\jamy\Desktop\22yr_Dolores_2nd'

snow17_skip = 121
ueb_skip = 121

start_time = ''
end_time = ''
dt = 6

result_dir = os.path.join(os.getcwd(), 'model_mass_balance_{}'.format(watershed))
if not os.path.isdir(result_dir):
    os.makedirs(result_dir)


# step 1 ueb mass balance  ##############################################
if os.path.isdir(ueb_dir):
    ts_file_list = [os.path.join(ueb_dir, name) for name in os.listdir(ueb_dir) if name[-2:] == 'ts']
    ueb_df = get_sac_ts_dataframe(ts_file_list, start_time=start_time, end_time=end_time, sim_skip=ueb_skip)
    if start_time and end_time:
        ueb_df = ueb_df[(ueb_df.index >= start_time)&(ueb_df.index <= end_time)]

    # snow model mass balance ###########################################################
    # error = cump - swe - Wc - cumrmlt - cumEc - cumEs
    ueb_df.columns = ['ueb_'+name if 'ueb' not in name else name for name in ueb_df.columns]
    ueb_df['ueb_prcp'] = 1000* ueb_df['ueb_P']*dt
    ueb_df['ueb_prcp_cum'] = 1000*dt*ueb_df['ueb_P'].cumsum()  # different from ueb_cump
    # ueb_df['ueb_swit_cum'] = 1000*dt*ueb_df['ueb_SWIT'].cumsum()  # different from ueb_cumMr
    ueb_df['ueb_es_cum'] = 1000*dt*ueb_df['ueb_Es'].cumsum()
    ueb_df['ueb_ec_cum'] = 1000*dt*ueb_df['ueb_Ec'].cumsum()
    ueb_df['ueb_sublimation_cum'] = ueb_df['ueb_ec_cum'] + ueb_df['ueb_es_cum']
    ueb_df['ueb_SWE_mm'] = 1000*ueb_df['ueb_SWE']
    # ueb_df['ueb_Wc_mm'] = 1000*ueb_df['ueb_Wc'] TODO
    ueb_df['ueb_we'] = ueb_df['ueb_SWE_mm']  #+ ueb_df['ueb_Wc_mm'] TODO
    ueb_df['ueb_rmlt_cum'] = ueb_df['ueb_xmrg'].cumsum()  # same as ueb_cumMr *1000
    ueb_df['ueb_snow_error'] = ueb_df['ueb_prcp_cum'] - ueb_df['ueb_rmlt_cum'] - ueb_df['ueb_SWE_mm'] - \
                               ueb_df['ueb_es_cum'] - ueb_df['ueb_ec_cum'] #- ueb_df['ueb_Wc_mm']  # TODO

    # stat: total sublimation stats
    ueb_df['ueb_sublim_cum'] = ueb_df['ueb_es_cum'] + ueb_df['ueb_ec_cum']
    percent_as_sublimation = 100 * ueb_df['ueb_sublim_cum'][-1]/ueb_df['ueb_prcp_cum'][-1]
    annual_sublimation = ueb_df['ueb_sublim_cum'][-1]/(ueb_df.index[-1].year - ueb_df.index[0].year)  # in meter
    annual_sublimation_percent = percent_as_sublimation/(ueb_df.index[-1].year - ueb_df.index[0].year)
    with open(os.path.join(result_dir,'sublimation_stat.txt'),'w') as f:
        f.write("\n".join([
            'percent sublimation:{} %'.format(round(percent_as_sublimation, 2)),
            'annual sublimation:{} mm'.format(round(annual_sublimation,3)),
            'annual sublimation:{} %'.format(round(annual_sublimation_percent, 2)),
        ]))

    # plot: mass balance and error
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df.plot(y=['ueb_prcp_cum',
                   'ueb_rmlt_cum',
                   'ueb_we',
                   # 'ueb_Wc',  # TODO
                   'ueb_es_cum',
                   'ueb_ec_cum'],
                ax=ax,
                title='UEB model mass balance for {}'.format(watershed),
                legend=False,
                )
    ax.legend(['cum prcpitation',
               'cum rain plus melt',
               'ground swe',
               # 'canopy swe',  #TODO
               'cum ground sublimation',
               'cum canopy sublimation'])
    ax.set_ylabel('water input/output (mm)')
    fig.savefig(os.path.join(result_dir,'ueb_snow_mass_balance.png'))

    # plot: mass balance error
    fig, ax = plt.subplots(figsize=(10, 5))
    ueb_df.plot(y='ueb_snow_error',
                ax=ax,
                title='UEB model mass balance error for {}'.format(watershed),
                legend=False,
                )
    ax.set_ylabel('error (mm)')
    fig.savefig(os.path.join(result_dir, 'ueb_snow_error.png'))

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
# TODO all sections need to validate with real data
if os.path.isdir(snow17_dir):
    ts_file_list = [os.path.join(snow17_dir, name) for name in os.listdir(snow17_dir) if name[-2:] == 'ts']
    snow17_df = get_sac_ts_dataframe(ts_file_list, start_time=start_time, end_time=end_time, sim_skip=snow17_skip)
    if start_time and end_time:
        snow17_df = snow17_df[(snow17_df.index >= start_time) & (snow17_df.index <= end_time)]
    # snow model mass balance #################################################
    # error = cump - cumrmlt - swe
    snow17_df.columns = ['snow17_'+name if 'snow17' not in name else name for name in snow17_df.columns]
    snow17_df['snow17_prcp_cum'] = snow17_df['snow17_xmrg'].cumsum()  # TODO: check the term for prcp and swit
    snow17_df['snow17_rmlt_cum'] = snow17_df['snow17_rmlt'].cumsum()
    snow17_df['snow17_snow_error'] = snow17_df['snow17_prcp_cum'] - snow17_df['snow17_rmlt_cum'] - snow17_df['snow17_we']

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
# TODO needs to validate with real data
if os.path.isdir(ueb_dir) and os.path.isdir(snow17_dir):
    concat_df = pd.concat([ueb_df, snow17_df], axis=1)

    # compare prcp #############################################################
    concat_df['prcp_error'] = concat_df['ueb_prcp'] #- concat_df['ueb_prcp'] # TODO not sure about

    fig, ax = plt.subplots(figsize=(10, 5))
    concat_df.plot(y=['ueb_prcp',
                      # 'snow17_xmrg' TODO
                      ],
                   ax=ax,
                   title='Compare precipitation between UEB and Snow17',
                   legend=False,
                   )

    ax.legend(['ueb','snow17',])
    ax.set_ylabel('prec(mm/{}hr)'.format(dt))
    fig.savefig(os.path.join(result_dir, 'prcp_model_compare.png'))

    fig, ax = plt.subplots(figsize=(10, 5))
    concat_df.plot(y=['prcp_error'],
                   ax=ax,
                   title='Error of precipitation between UEB and Snow17',
                   legend=False,
                   )
    ax.set_ylabel('error(mm/{}hr)'.format(dt))
    fig.savefig(os.path.join(result_dir, 'prcp_model_compare_error.png'))

    # compare SWE  #####################################################
    fig, ax = plt.subplots(figsize=(10, 5))
    concat_df.plot.area(y=[#'ueb_Wc_mm'
                           'ueb_SWE_mm',
                           ],
                        ax=ax,
                        title='SWE comparison between UEB and Snow17',
                        style=['whitesmoke',
                               'silver',
                               ],
                        legend=False,
                        )
    concat_df.plot(y=['ueb_we',
                      # 'snow17_we'
                      ],
                   ax=ax,
                   style=['k:',
                          'k-',
                          ],
                   legend=False,
                   )

    ax.legend(['ueb ground SWE',
               'ueb surface SWE',
               'ueb SWE',
               'snow17 SWE'])  #TODO the sequence is not correct

    fig.savefig(os.path.join(result_dir, 'swe_model_compare.png'))

    # compare total ET  #####################################################
    fig, ax = plt.subplots(figsize=(10, 5))
    concat_df.plot.area(y=['ueb_sublimation_cum',
                           'ueb_tet_cum',
                           ],
                        ax=ax,
                        title='Total Evaporation comparison between UEB and Snow17',
                        style=['whitesmoke',
                               'silver',
                               ],
                        legend=False,
                        )
    concat_df.plot(y=['ueb_total_et_cum'
                      # 'snow17_we'
                      ],
                   ax=ax,
                   style=['k:',
                          'k-',
                          ],
                   legend=False,
                   )

    ax.legend(['ueb',
               'snow17'])  #TODO the sequence is not correct

    fig.savefig(os.path.join(result_dir, 'total_et_model_compare.png'))