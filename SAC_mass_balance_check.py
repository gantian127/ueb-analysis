"""
This is used to check the mass balance of the SAC-SAM model results. This is just for experimenting purpose
- mass balance of cum prcp, cum discharge, cum ET, storage
- mass balance of surface flow
- mass balance of subsurface flow
- mass balance of discharge = surface + subsurface
- total storage = lower zone + upper zone storage
"""

from plot_SAC_utility import *

workdir_list = [
    r'C:\Users\jamy\Desktop\SAC_output_rti_parameters',
    # r'C:\Users\jamy\Desktop\SAC_output_bad',
    r'C:\Users\jamy\Desktop\SAC_output_snow17_parameter',
    r'C:\Users\jamy\Desktop\SAC_output_usu_paul_repeat_22yr',

]

start_time = '2008-10-01'
end_time = '2009-10-01'
watershed_area = 1818920000  # m^2  1818.92 km^2
dt = 3  # hour
format = '%Y/%m'
interval = 1
plt.ioff()

df_list = []
df_name_list = []
#
for workdir in workdir_list:
    if not os.path.isdir(workdir):
        continue
    else:
        os.chdir(workdir)
        print workdir
        # get ts file list
        ts_file_list = [name for name in os.listdir(os.getcwd()) if name[-2:] == 'ts']
        DF = get_sac_ts_dataframe(ts_file_list, start_time=start_time, end_time=end_time)

        # get mass balance variables
        DF['cum_prcp'] = DF['xmrg'].cumsum()   #xmrg is prcp in mm at each time step
        DF['cum_tet'] = DF['tet'].cumsum()  # tet is total ET in mm/dt(hr)

        DF['discharge_depth'] = DF['discharge']*dt*3600*1000/watershed_area
        DF['cum_discharge'] = DF['discharge_depth'].cumsum()

        if 'real_lzfpc' not in DF.columns:
            para_file_name = [file_name for file_name in ts_file_list if 'lzfpc' in file_name][0]
            para_df = pd.read_csv(para_file_name, nrows=20, header=6, sep='\s+').iloc[:,1:3]
            para_df.columns = ['name', 'value']
            DF['real_lzfpc'] = DF['lzfpc']* para_df['value'].ix[para_df.name == 'sac_LZFPM'].values[0]
            DF['real_lzfsc'] = DF['lzfsc']* para_df['value'].ix[para_df.name == 'sac_LZFSM'].values[0]
            DF['real_lztwc'] = DF['lztwc']* para_df['value'].ix[para_df.name == 'sac_LZTWM'].values[0]
            DF['real_uzfwc'] = DF['uzfwc']* para_df['value'].ix[para_df.name == 'sac_UZFWM'].values[0]
            DF['real_uztwc'] = DF['uztwc']* para_df['value'].ix[para_df.name == 'sac_UZTWM'].values[0]
        DF['total_storage'] = DF['real_lzfpc'] + DF['real_lzfsc'] + DF['real_lztwc'] + DF['real_uzfwc'] + DF['real_uztwc']
        DF['storage_change'] = DF['total_storage'] - DF['total_storage'][0]

        DF['error'] = DF['cum_prcp'] - DF['cum_tet'] -DF['cum_discharge'] - DF['storage_change']
        # DF['subsurfaceFlow_cms'] = DF.subsurfaceFlow*watershed_area / (dt*3600*1000)
        # DF['surfaceFlow_cms'] = DF.surfaceFlow*watershed_area/(dt*3600*1000)
        # DF['tet_cms'] = DF.tet*watershed_area/(dt*3600*1000)

        df_list.append(DF)
        df_name_list.append(os.path.basename(workdir))

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
        if 'subsurfaceFlow' in DF.columns and 'surfaceFlow' in DF.columns:
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
        if 'primaryFlow' in DF.columns and 'supplementalFlow' in DF.columns and 'interflow' in DF.columns:
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
        if 'excessFlow' in DF.columns and 'directFlow' in DF.columns:
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

# Code for testing and compare
var_list = ['tet', 'cum_tet', 'total_storage']
ylabel_list = ['ET (mm/{}hr)'.format(dt), 'cumulative ET (mm)', 'storage(mm)']
title_list = ['ET','Cumulative ET', 'Total storage']

df_list = df_list[0:2]

for i in range(0, len(var_list)):
    var=var_list[i]
    if var in ['tet', 'total_storage']:
        data = [df[[var]].groupby(pd.TimeGrouper(freq='D')).mean() for df in df_list]
    elif var in ['cum_tet', 'cum_prcp']:
        data = [df[[var]].groupby(pd.TimeGrouper(freq='D')).max() for df in df_list]
    time = data[0].index

    fig, ax = plot_multiple_X_Y(time, data, label_list=df_name_list)
    refine_plot(ax, xlabel='time', ylabel=ylabel_list[i],
                title=title_list[i],
                interval=interval,
                format=format,
                legend=True,
                time_axis=True)
