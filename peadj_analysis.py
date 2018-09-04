"""
This is to analyze the peadj parameters of RDHM using the PE grid

requirement:
- input deck file with watershed index as the file name  e.g. DOLC2.deck
- zonal stats .csv of PE grid for each subwatershed (run arcpy_zonal_stats.py)

step:
- get the peadj values
- peadj plots
- get the zonal stats table
- calculate weighted peadj

"""

import os
import calendar
import pandas as pd
import matplotlib.pyplot as plt

# User settings #######################################################################
watershed_group = 'Mcphee'

deck_folders = {
    'ueb': r'C:\Users\jamy\Desktop\weighted_PE_analysis\ueb_deck\mcphee',
    'snow17': r'C:\Users\jamy\Desktop\weighted_PE_analysis\snow17_deck\mcphee',
}

table_folder = r'C:\Users\jamy\Desktop\weighted_PE_analysis\pe_grid\zonal_stat_results'

result_dir = os.path.join(os.getcwd(), 'peadj_analysis_{}'.format(watershed_group))
if not os.path.isdir(result_dir):
    os.mkdir(result_dir)


# PE analysis #######################################################################
# get peadj result
peadj_df_list = []
watershed_list = []

for model, deck_folder in deck_folders.items():

    deck_file_list = [os.path.join(deck_folder, file_name) for file_name in os.listdir(deck_folder)]
    month_list = [x[:3].upper() for x in calendar.month_name if x]
    peadj_df = pd.DataFrame(index=range(1,13))

    for deck_file in deck_file_list:
        watershed = os.path.basename(deck_file)[0:5]
        if watershed not in watershed_list:
            watershed_list.append(watershed)

        col_name = '{}_{}'.format(model, watershed)
        parse_list = []
        with open(deck_file) as myfile:
            for num, line in enumerate(myfile, 1):
                if 'peadj_' in line:
                    str_list = line.replace('\n', '').split(' ')[2:]
                    parse_list.extend(str_list)

        para_values = []
        for i in range(0, len(parse_list)):
            para_values.append(float(parse_list[i].replace('peadj_'+ month_list[i] + '=', '')))

        peadj_df[col_name] = para_values

    peadj_df_list.append(peadj_df)

peadj_result = pd.concat(peadj_df_list,axis=1)
peadj_result.to_csv(os.path.join(result_dir,'peadj_result.csv'))

# plot: compare watersheds
for watershed in watershed_list:
    y = [col for col in peadj_result.columns if watershed in col]
    fig, ax = plt.subplots(figsize=(10, 6))
    peadj_result.plot(y=y, ax=ax,
                      title='Peadj from UEB and SNOW17 in {}'.format(watershed),
                      style='*-')
    ax.set_xticks(range(1,13))
    ax.set_xticklabels(month_list)
    fig.savefig(os.path.join(result_dir,'peadj_{}.png'.format(watershed)))

# plot: compare models
for model in deck_folders.keys():
    y = [col for col in peadj_result.columns if model in col]
    fig, ax = plt.subplots(figsize=(10, 6))
    peadj_result.plot(y=y,
                      title='Peadj from {} model for all watersheds'.format(model),
                      ax=ax,
                      style='*-')
    ax.set_ylabel('peadj')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_list)
    fig.savefig(os.path.join(result_dir, 'peadj_{}.png'.format(model)))

# Zonal PE analysis #################################################################################
# get zonal stats data
table_list = [os.path.join(table_folder, file_name) for file_name in os.listdir(table_folder)
              if '.csv' in file_name and 'pe_' in file_name]

table_df_list = []
for table_file in table_list:
    month = os.path.basename(table_file)[3:-4]
    table_df = pd.read_csv(table_file)
    table_df.drop(['OID', 'ZONE_CODE', 'COUNT'], axis=1, inplace=True)
    table_df.set_index('CH5_ID', inplace=True)
    table_df.columns = ['{}_{}'.format(month, col_name) for col_name in table_df.columns]
    table_df_list.append(table_df)

table_result = pd.concat(table_df_list, axis=1)
table_result.to_csv(os.path.join(result_dir, 'table_result.csv'))


# plot: compare min, max, mean in each watershed
var_list = ['MAX', 'MEAN', 'MIN', 'SUM', 'STD', 'RANGE']
for watershed in watershed_list:
    fig, ax = plt.subplots(figsize=(13, 8))

    for var in var_list[0:3]:
        index_list = []
        for month in month_list:
            index_list.append('{}_{}'.format(month, var))
        data = table_result.loc[watershed, index_list]
        data.plot(ax=ax, style='*-')

    ax.set_xticks(range(0, 13))
    ax.set_xticklabels(month_list)
    ax.set_ylabel('Potential ET (mm/day)')
    ax.legend(var_list)
    ax.set_title('Zone stats of PE in {} for {}'.format(watershed, ' '.join(var_list[0:3])))
    fig.savefig(os.path.join(result_dir, 'zonal_{}_{}'.format(watershed, '_'.join(var_list[0:3]))))

# plot: compare all stats among watersheds
for var in var_list:
    fig, ax = plt.subplots(figsize=(13, 8))
    for watershed in watershed_list:
        index_list = []
        for month in month_list:
            index_list.append('{}_{}'.format(month,var))
        data = table_result.loc[watershed, index_list]
        data.plot(ax=ax, style='*-')

    ax.set_xticks(range(0, 13))
    ax.set_xticklabels(month_list)
    ax.set_ylabel('Potential ET (mm/day)')
    ax.legend(watershed_list)
    ax.set_title('Zone stats of PE for {}'.format(var))
    fig.savefig(os.path.join(result_dir, 'zonal_{}'.format(var)))


# weighted Peadj  #################################################
model_list = ['ueb', 'snow17']
weight_peadj = pd.DataFrame(index=watershed_list, columns=model_list)

# calculate weight peadj
for watershed in weight_peadj.index:

    peadj_value = peadj_result[[col_name for col_name in peadj_result.columns if watershed in col_name]]
    col_list = []
    for month in month_list:
        col_list.append('{}_{}'.format(month, 'SUM'))
    pe_sum_value = table_result.ix[watershed, col_list]
    pe_sum_value.index = range(1,13)
    concat_df = pd.concat([peadj_value, pe_sum_value], axis=1)

    result_list = []
    for model in model_list:
        concat_df['{}_weight'.format(model)] = concat_df['{}_{}'.format(model, watershed)] * concat_df[watershed]
        result_list.append(concat_df['{}_weight'.format(model)].sum()/concat_df[watershed].sum())

    weight_peadj.ix[watershed] = result_list
    concat_df.to_csv(os.path.join(result_dir, 'weight_peadj_{}.csv'.format(watershed)))

weight_peadj.to_csv(os.path.join(result_dir, 'weight_peadj_final.csv'))


# plot: compare weight peadj
fig, ax = plt.subplots(figsize=(10, 6))
weight_peadj.plot.bar(ax=ax, rot=0)
ax.set_ylabel('weighted peadj')
ax.set_title('Weighted peadj for UEB and SNOW17')
fig.savefig(os.path.join(result_dir,'weighted_peadj.png'))
