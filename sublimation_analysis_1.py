"""
This is the 1st version sublimation analysis

step 1: unzip .gz file

step:
- create xmrg dataframe
- unzip .gz file and store file name in the dataframe

"""


import gzip
import os

import pandas as pd


# step 1 user settings  ####################################################
watershed = 'McPhee'

start_date = '1992/10/1'
end_date = '1993/09/30'

var_gz_folders = {

    'uebPrec': r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/ueb_sublimation_test/SAC_out/uebPrec',
    'ueb_Ec': r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/ueb_sublimation_test/SAC_out/ueb_Ec',
    'ueb_Es': r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/ueb_sublimation_test/SAC_out/ueb_Es',
    'ueb_tet': r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/ueb_sublimation_test/SAC_out/tet',
    'ueb_rmlt': r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/ueb_sublimation_test/SAC_out/xmrg',

    'snow17_xmrg': r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/snow17_best/SAC_out_sublimation_test/xmrg',
    'snow17_rmlt': r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/snow17_best/SAC_out_sublimation_test/rmlt',
    'snow17_tet': r'/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/snow17_best/SAC_out_sublimation_test/tet',
}

# create results folder
folder_name = '{}_sublimation_analysis'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
if not os.path.isdir(result_folder):
    os.mkdir(result_folder)


# step2 : unzip .gz file to assigned folder ####################################
date_index = pd.date_range(start_date,end_date, freq='6H')
xmrg_df = pd.DataFrame(index=date_index, columns=var_gz_folders.keys())

for var, var_gz_folder in var_gz_folders.items():

    print 'start unzip {}'.format(var)
    if os.path.isdir(var_gz_folder):
        fail_files = []
        var_xmrg_folder = os.path.join(result_folder, 'xmrg_folder_{}'.format(var))
        if not os.path.isdir(var_xmrg_folder):
            os.mkdir(var_xmrg_folder)

        for time in xmrg_df.index:
            var_gz_name = '{}{}z.gz'.format(os.path.basename(var_gz_folder), time.strftime('%m%d%Y%H'))
            var_gz_path = os.path.join(var_gz_folder, var_gz_name)
            var_xmrg_path = os.path.join(var_xmrg_folder, var_gz_name.replace('.gz', ''))

            if not os.path.isfile(var_xmrg_path):
                try:
                    if os.path.isfile(var_gz_path):
                        with gzip.open(var_gz_path, 'rb') as inf:
                            with open(var_xmrg_path, 'wb') as outf:
                                content = inf.read()
                                outf.write(content)
                        xmrg_df[var].ix[time] = os.path.basename(var_xmrg_path)
                    else:
                        print 'no .gz file {}'.format(var_gz_path)
                except Exception as e:
                    print 'failed to unzip file {}'.format(var_gz_name)
                    fail_files.append(var_gz_path)
                    continue
            else:
                xmrg_df[var].ix[time] = os.path.basename(var_xmrg_path)

        if fail_files:
            with open(os.path.join(result_folder, 'fail_xrmg_{}.txt'.format(var)), 'w') as f:
                f.write('\n'.join(fail_files))
    else:
        print 'failed to find .gz folder for {}'.format(var)

xmrg_df.to_csv(os.path.join(result_folder, 'xmrg_df.csv'))

print 'sublimation_analysis_1: unzip files is done'
