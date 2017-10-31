"""
This is used to compare the discharge results from UEB+SAC and Snow17+SAC.

1 separate results:
  create folders include the discharge related statistics and graphs for each simulation results
2 combined results:
  compare all the simulation and observation daily discharge on one plot and the error for all simulation on one plot
"""

import os

from plot_SAC_utility import *

sim_file_list = [
                 'DRGC2_discharge_outlet_22yr.ts',
                 'DRGC2_discharge_outlet_62824_22yr_cali.ts',
                 # 'DRGC2_discharge_outlet_31567.ts',
                 # 'DRGC2_discharge_outlet_chpc_para.ts' # this is useing the parameter from 62824 to rerun 22yr sac model
                 ]

obs_file = 'DRGC2H_F.QME'
watershed_area = 1818920000  # m^2  1818.92 km^2
start_time = '1989-10-01' #'2005-10-01'
end_time = '2010-6-30' #'2006-9-30'

DF_list = []
plt.ioff()

# Analysis for each simulation results
for sim_file in sim_file_list:

    # create results dir
    results_dir = os.path.join(os.getcwd(), 'discharge_{}'.format(sim_file[:-3]))
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)

    # get data frame
    DF = get_sim_obs_dataframe(sim_file, obs_file,
                               start_time=start_time, end_time=end_time,
                               save_folder=results_dir)
    DF_list.append(DF)

    # daily discharge analysis
    plot_obs_vs_sim(DF.time, DF.sim, DF.obs,
                    month_interval=12, format='%Y',
                    ts_xlim=[datetime(DF.time[0].year, 1, 1),
                             datetime(DF.time[len(DF)-1].year, 12, 31)],
                    # month_interval=1, format='%Y/%m',
                    save_folder=results_dir)

    # monthly analysis
    get_monthly_mean_analysis(DF, watershed_area, save_folder=results_dir)

    # annual analysis
    get_annual_mean_analysis(DF, watershed_area, save_folder=results_dir)

    # April - July Volume error
    get_volume_error_analysis(DF, watershed_area, save_folder=results_dir, start_month=4, end_month=7)


# Daily discharge comparison for all the simulation results
if len(sim_file_list) > 1:
    compare_dir = 'compare_daily_discharge'
    if not os.path.isdir(compare_dir):
        os.mkdir(compare_dir)

    DF_list_subset = [x[['time', 'sim', 'obs']] for x in DF_list]
    concat_df = pd.concat(DF_list_subset, axis=1, join='inner')
    obs_data = concat_df[['obs']].iloc[:, 0]
    time_data = concat_df[['time']].iloc[:, 0].tolist()
    sim_data = concat_df[['sim']]
    sim_data.columns = ['sim_'+sim_file[:-3] for sim_file in sim_file_list]

    # plot for all the simulation and observation
    Y = [obs_data.values.T.tolist()] + sim_data.values.T.tolist()
    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    plot_multiple_X_Y(time_data, Y,
                      ax=ax[0], fig=fig,
                      label_list=['obs']+sim_data.columns.tolist(),
                      linestyle_list=['y-'] + [':']*len(sim_data.columns),
                      xlim=[datetime(time_data[0].year, 1, 1),
                            datetime(time_data[-1].year, 12, 31)]
                      )

    refine_plot(ax[0], xlabel='time', ylabel='discharge(cms)',
                title='Daily discharge comparison',
                interval=12,
                format='%Y',
                legend=True,
                time_axis=True)

    difference = [(sim_data.iloc[:, i] - obs_data).tolist() for i in range(0, len(sim_data.columns))]
    difference_mean = [ sum(x)/len(x) for x in difference]
    plot_multiple_X_Y(time_data, difference,
                      ax=ax[1], fig=fig,
                      label_list=sim_data.columns.tolist(),
                      linestyle_list=[':']*len(sim_data.columns),
                      xlim=[datetime(time_data[0].year, 1, 1),
                            datetime(time_data[-1].year, 12, 31)]
                      )

    refine_plot(ax[1], xlabel='time', ylabel='discharge(cms)',
                title='Daily discharge error comparision (sim-obs)',
                interval=12,
                format='%Y',
                legend=True,
                time_axis=True)

    path = os.path.join(compare_dir, 'daily_discharge_comparison.png') if compare_dir else 'daily_discharge_comparison.png'
    save_fig(fig, save_as=path)

print 'All analysis is finished ! Please check the results'
