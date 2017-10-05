"""
This is to calculate the Q and error statistics directly using:
outlet discharge from SAC-SMA output
the RTI discharge data

"""

from datetime import datetime, timedelta
from plot_SAC_utility import *
import os


# user inputs
workdir = ''  # workdir of the time series files
if workdir:
    os.chdir(workdir)

sac_discharge_file = 'DRGC2_discharge_outlet_22yr.ts'
rti_discharge_file = 'DRGC2H_F.QME.txt'

watershed = 'Animas'
year = '1988_2010'  # can be single or multiple year used for title info

start_date = ''
end_date = ''

# SAC-SMA output plots #############################################################
# import SAC-SMA model data

raw_discharge = pd.read_csv(sac_discharge_file, skiprows=250, header=None, names=['raw'])
discharge = raw_discharge['raw'].str.split('\s+', expand=True)
discharge_flow = [float(x) for x in discharge[3].tolist()]

# get time obj
time_str = (discharge[1]+discharge[2]).tolist()
time_obj = []
for x in time_str:
    if x[-2:] == '25':
        x = x[:-2] + x[-2:].replace('25', '23')
        time = datetime.strptime(x, '%d%m%y%H')
        time += timedelta(hours=2)
    else:
        time = datetime.strptime(x, '%d%m%y%H')

    time_obj.append(time)


# import rti discharge data
rti_discharge = pd.read_csv(rti_discharge_file, skiprows=3, header=None, names=['raw'])  # time column is used as index in dataframe
if not (start_date and end_date):
    start_date = datetime.strftime(time_obj[0], '%Y-%m-%d')
    end_date = datetime.strftime(time_obj[-1]+ timedelta(days=1), '%Y-%m-%d')

obs_discharge = rti_discharge.ix[start_date:end_date]['raw'].apply(lambda x : x*0.0283168)  # daily discharge in cms with start and end time


# get the sac daily mean data
sac_df = pd.DataFrame(data={'time': time_obj, 'discharge': discharge_flow}, columns=['time', 'discharge'])
sac_discharge_outlet = sac_df.set_index('time').groupby(pd.TimeGrouper(freq='D'))['discharge'].mean()

# make obs vs simulation plot
plot_obs_vs_sim(time=sac_discharge_outlet.index.values,
                sim=sac_discharge_outlet.tolist(),
                obs=obs_discharge.tolist(),
                month_interval=12,
                format='%Y/%m',
                save_as='obs_sim_discharge_{}_{}.png'.format(watershed, year))