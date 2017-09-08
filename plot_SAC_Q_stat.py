"""
This is to calculate the Q and error statistics indirectly using:
the subsurfaceflow and surfaceflow from SAC-SMA output
the RTI discharge data

"""

from datetime import datetime, timedelta
from plot_SAC_utility import *
import os


# user inputs
workdir = ''  # workdir of the time series files
if workdir:
    os.chdir(workdir)

sac_sub_file = 'DRGC2_subsurfaceFlow_local.ts'
sac_surf_file = 'DRGC2_surfaceFlow_local.ts'
rti_discharge_file = 'DRGC2H_F.QME.txt'

dtime = 3   # time interval from the sac-sma time series output
area = 1818920000   # Animas m^2
watershed = 'Animas'
year = '1989'  # can be single or multiple year used for title info

start_date = ''  # for rti discharge date time. this can be calculated from sac data
end_date = ''  # for rti discharge date time. this can be calculated from sac data


# SAC-SMA output plots #############################################################
# import SAC-SMA model data
raw_sub = pd.read_csv(sac_sub_file, skiprows=62, header=None, names=['raw'])
raw_surf = pd.read_csv(sac_surf_file, skiprows=62, header=None, names=['raw'])
sub = raw_sub['raw'].str.split('\s+', expand=True)
surf = raw_surf['raw'].str.split('\s+', expand=True)


# get time obj
time_str = (sub[1]+sub[2]).tolist()
time_obj = []
for x in time_str:
    if x[-2:] == '24':
        x = x[:-2] + x[-2:].replace('24', '23')
        time = datetime.strptime(x, '%d%m%y%H')
        time += timedelta(hours=1)
    else:
        time = datetime.strptime(x, '%d%m%y%H')

    time_obj.append(time)


# get flow in mm/dtime
sub_flow = [float(x) for x in sub[3].tolist()]
surf_flow = [float(x) for x in surf[3].tolist()]
sum_flow = [x + y for x, y in zip(sub_flow, surf_flow)]

# get flow in cms
sub_flow_cms = [(x * area) / (dtime*3600*1000) for x in sub_flow]
surf_flow_cms = [(x * area) / (dtime*3600*1000) for x in surf_flow]
sum_flow_cms = [(x * area) / (dtime*3600*1000) for x in sum_flow]


# plot watershed runoff in mm/dtime
fig, ax = plt.subplots(figsize=(15, 5))
plot_multiple_time_series(time_obj,
                          [sub_flow, surf_flow, sum_flow],
                          ['subsurface flow', 'surface flow', 'total flow'],
                          ax=ax, fig=fig
                          )
refine_plot(ax, xlabel='time', ylabel='Watershed runoff(mm/{}hr)'.format(dtime), title='Runoff(mm/hr) in {} {} '.format(watershed, year))
save_fig(fig, save_as='Watershed Runoff_{}_{}_mmhr.png'.format(watershed, year))


# plot watershed runoff in cms
fig, ax = plt.subplots(figsize=(15, 5))
plot_multiple_time_series(time_obj,
                          [sub_flow_cms, surf_flow_cms, sum_flow_cms],
                          ['subsurface flow', 'surface flow', 'total flow'],
                          ax=ax, fig=fig
                          )
refine_plot(ax, xlabel='time', ylabel='runoff(cms)'.format(dtime), title='Runoff(cms) in {} {} '.format(watershed, year))
save_fig(fig, save_as='Watershed Runoff_{}_{}_cms.png'.format(watershed, year))

# # get flow in cfs
# sub_flow_cfs = [(x * (3.28084**3) * area) / (dtime*3600*1000) for x in sub_flow]
# surf_flow_cfs = [(x * (3.28084**3) * area) / (dtime*3600*1000) for x in surf_flow]
# sum_flow_cfs = [(x * (3.28084**3) * area) / (dtime*3600*1000) for x in sum_flow]

# # plot watershed runoff in cfs
# fig, ax = plt.subplots(figsize=(15, 5))
# plot_multiple_time_series(time_obj,
#                           [sub_flow_cfs, surf_flow_cfs, sum_flow_cfs],
#                           ['subsurface flow', 'surface flow', 'total flow'],
#                           ax=ax, fig=fig
#                           )
# refine_plot(ax, xlabel='time', ylabel='runoff(cfs)'.format(dtime), title='Runoff(cfs) in {} {} '.format(watershed, year))
# # save_fig(fig, save_as='Watershed Runoff_{}_{}_cfs.png'.format(watershed, year))


# import rti discharge data
rti_discharge = pd.read_csv(rti_discharge_file, skiprows=3, header=None, names=['raw'])  # time column is used as index in dataframe
if not (start_date and end_date):
    start_date = datetime.strftime(time_obj[0], '%Y-%m-%d')
    end_date = datetime.strftime(time_obj[-1]+ timedelta(days=1), '%Y-%m-%d')

obs_discharge = rti_discharge.ix[start_date:end_date]['raw'].apply(lambda x : x*0.0283168)  # daily discharge in cms with start and end time


# get the sac daily mean data
sac_df = pd.DataFrame(data={'time': time_obj, 'flow': sum_flow_cms}, columns=['time', 'flow'])
sac_discharge = sac_df.set_index('time').groupby(pd.TimeGrouper(freq='D'))['flow'].mean()

plot_obs_vs_sim(time=sac_discharge.index.values,
                obs=obs_discharge.tolist(),
                sim=sac_discharge.tolist(),
                save_as='obs_sim_runoff_{}_{}'.format(watershed,year))




