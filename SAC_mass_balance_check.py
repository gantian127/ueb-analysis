"""
This is used to check the mass balance of the SAC-SAM model results
- mass balance of cum prcp, cum discharge, cum ET, storage
- mass balance of surface flow
- mass balance of subsurface flow
- mass balance of discharge = surface + subsurface
- total storage = lower zone + upper zone storage
"""
import os

from plot_SAC_utility import *

workdir=r'C:\Users\jamy\Desktop\SAC_output_bad'
os.chdir(workdir)
start_time = '1988-10-01'
end_time = '1989-10-01'
watershed_area = 1818920000   #m^2  1818.92 km^2
dt = 3  # hour
format = '%Y/%m'
interval = 1

# get ts file list
ts_file_list = [name for name in os.listdir(os.getcwd()) if name[-2:] == 'ts']
DF = get_sac_ts_dataframe(ts_file_list,start_time=start_time, end_time=end_time)

# get mass balance variables
DF['cum_prcp'] = DF['xmrg'].cumsum()   #xmrg is prcp in mm at each time step
DF['cum_tet'] = DF['tet'].cumsum()  # tet is total ET in mm/dt(hr)
DF['discharge_depth'] = DF['discharge']*dt*3600*1000/watershed_area
DF['cum_discharge'] = DF['discharge_depth'].cumsum()
DF['total_storage'] = DF['real_lzfpc'] + DF['real_lzfsc'] + DF['real_lztwc'] + DF['real_uzfwc'] + DF['real_uztwc']
DF['storage_change'] = DF['total_storage'] - DF['total_storage'][0]
DF['error'] = DF['cum_prcp'] - DF['cum_tet'] -DF['cum_discharge'] - DF['storage_change']
# DF['subsurfaceFlow_cms'] = DF.subsurfaceFlow*watershed_area / (dt*3600*1000)
# DF['surfaceFlow_cms'] = DF.surfaceFlow*watershed_area/(dt*3600*1000)
# DF['tet_cms'] = DF.tet*watershed_area/(dt*3600*1000)


# make mass balance plot
# cumulative prcp = cumulative discharge + storage_change + cumulative ET
fig, ax = plt.subplots(2, 1, figsize=(15, 10))
plot_multiple_X_Y(DF.index, [DF.cum_prcp, DF.cum_discharge, DF.cum_tet, DF.storage_change],
                  ax=ax[0], fig=fig,
                  label_list=['cumulative prcp', 'cumulative discharge', 'cumulative ET','storage_change'],
                  # xlim=[datetime(DF.index[0].year, 1, 1),
                  #       datetime(DF.index[-1].year, 12, 31)]
                  )

refine_plot(ax[0], xlabel='time', ylabel='depth(mm)',
            title='Mass balance for SAC-SMA simulation',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

plot_multiple_X_Y(DF.index, [DF.error],
                  ax=ax[1], fig=fig,
                  label_list=['error'],
                  # xlim=[datetime(DF.index[0].year, 10, 1),
                  #       datetime(DF.index[-1].year, 10, 1)]
                  )

refine_plot(ax[1], xlabel='time', ylabel='depth(mm)',
            title='Mass Balance error',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

save_fig(fig, save_as='sac_mass_balance.png')

# make storage plots
fig, ax = plot_multiple_X_Y(DF.index, [DF.total_storage, DF.real_uztwc, DF.real_uzfwc, DF.real_lztwc, DF.real_lzfpc, DF.real_lzfsc],
                            label_list=['total storage', 'uztwc', 'uzfwc', 'lztwc', 'lzfpc', 'lzfsc', ],
                            figsize=(15, 5),
                            # xlim=[datetime(DF.index[0].year, 1, 1),
                            # datetime(DF.index[-1].year, 12, 31)]
                              )

refine_plot(ax, xlabel='time', ylabel='depth(mm)',
            title='Domain average storage for SAC-SMA simulation',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

save_fig(fig, save_as='storage.png')


# make discharge mass balance
# discharge_depth =~ subsurfaceFlow + surfaceFlow
fig, ax = plt.subplots(2, 1, figsize=(15, 10))
plot_multiple_X_Y(DF.index, [DF.discharge_depth, DF.subsurfaceFlow, DF.surfaceFlow],
                            ax=ax[0], fig=fig,
                            label_list=['discharge', 'subsurfaceFlow', 'surfaceFlow'],
                            figsize=(15, 5),
                            # xlim=[datetime(DF.index[0].year, 1, 1),
                            # datetime(DF.index[-1].year, 12, 31)]
                              )

refine_plot(ax[0], xlabel='time', ylabel='depth(mm)',
            title='Discharge mass balance for SAC-SMA simulation',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

plot_multiple_X_Y(DF.index, [DF.discharge_depth - DF.subsurfaceFlow - DF.surfaceFlow],
                  ax=ax[1], fig=fig,
                  label_list=['error'],
                  # xlim=[datetime(DF.index[0].year, 10, 1),
                  #       datetime(DF.index[-1].year, 10, 1)]
                  )

refine_plot(ax[1], xlabel='time', ylabel='depth(mm)',
            title='Discharge mass balance error',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

save_fig(fig, save_as='discharge_mass_balance.png')

# subsurface mass balance:
# subsurface flow = primary flow + supplemental flow + inter flow
fig, ax = plt.subplots(2, 1, figsize=(15, 10))
plot_multiple_X_Y(DF.index, [DF.subsurfaceFlow, DF.primaryFlow, DF.supplementalFlow, DF.interflow],
                            ax=ax[0], fig=fig,
                            label_list=['subsurfaceFlow', 'primaryFlow','supplementalFlow','interflow' ],
                            figsize=(15, 5),
                            # xlim=[datetime(DF.index[0].year, 1, 1),
                            # datetime(DF.index[-1].year, 12, 31)]
                              )

refine_plot(ax[0], xlabel='time', ylabel='flow (mm/{}hr)'.format(dt),
            title='Subserface Flow mass balance for SAC-SMA simulation',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

plot_multiple_X_Y(DF.index, [DF.subsurfaceFlow - DF.primaryFlow- DF.supplementalFlow - DF.interflow],
                  ax=ax[1], fig=fig,
                  label_list=['error'],
                  # xlim=[datetime(DF.index[0].year, 10, 1),
                  #       datetime(DF.index[-1].year, 10, 1)]
                  )

refine_plot(ax[1], xlabel='time', ylabel='flow (mm/{}hr)'.format(dt),
            title='Discharge mass balance error',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

save_fig(fig, save_as='subsurface_mass_balance.png')


# surface flow mass balance:
# surface flow = excess flow + direct flow
fig, ax = plt.subplots(2, 1, figsize=(15, 10))
plot_multiple_X_Y(DF.index, [DF.surfaceFlow, DF.excessFlow, DF.directFlow],
                            ax=ax[0], fig=fig,
                            label_list=['surfaceFlow', 'excessFlow','directFlow'],
                            figsize=(15, 5),
                            # xlim=[datetime(DF.index[0].year, 1, 1),
                            # datetime(DF.index[-1].year, 12, 31)]
                              )

refine_plot(ax[0], xlabel='time', ylabel='flow (mm/{}hr)'.format(dt),
            title='Surface flow mass balance for SAC-SMA simulation',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

plot_multiple_X_Y(DF.index, [DF.surfaceFlow - DF.excessFlow- DF.directFlow],
                  ax=ax[1], fig=fig,
                  label_list=['error'],
                  # xlim=[datetime(DF.index[0].year, 10, 1),
                  #       datetime(DF.index[-1].year, 10, 1)]
                  )

refine_plot(ax[1], xlabel='time', ylabel='flow (mm/{}hr)'.format(dt),
            title='Surface flow mass balance error',
            interval=interval,
            format=format,
            legend=True,
            time_axis=True)

save_fig(fig, save_as='surface_mass_balance.png')

print 'Analysis is done'