"""
This is the 1st version sublimation analysis

step2: convert xmrg file as tif file with projection

step:
- convert file : xmrg -> asc -> tif with reproject

"""


import os
import subprocess
import shlex

import pandas as pd
import gdal

# default user settings apply to all steps ####################################################
watershed = 'McPhee'
folder_name = '{}_sublimation_analysis'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
xmrg_df_path = os.path.join(result_folder, 'xmrg_df.csv')

# reprojection info
# proj4_string = '+proj=stere +lat_0=90.0 +lat_ts=60.0 +lon_0=-105.0 +k=1 +x_0=0.0 +y_0=0.0 +a=6371200 +b=6371200 +units=m +no_defs'  # polar stereographic
proj4_string = 'PROJCS["Sphere_ARC_INFO_Stereographic_North_Pole",GEOGCS["GCS_Sphere_ARC_INFO",DATUM["Sphere_ARC_INFO",SPHEROID["Sphere_ARC_INFO",6370997,0]],PRIMEM["Greenwich",0],\
UNIT["degree",0.0174532925199433]],PROJECTION["Polar_Stereographic"],PARAMETER["latitude_of_origin",60.00681388888889],PARAMETER["central_meridian",-105],\
PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'


# Step 1 xmrg format conversion and reprojection  ##############################################
# load xmrg file info
xmrg_df = pd.DataFrame.from_csv(xmrg_df_path, header=0)

# data processing
for var in xmrg_df.columns:
    var_xmrg_folder = os.path.join(result_folder, 'xmrg_folder_{}'.format(var))

    if os.path.isdir(var_xmrg_folder):
        fail_files = []

        # create tif folder
        var_tif_folder = os.path.join(result_folder, 'tif_folder_{}'.format(var))
        if not os.path.isdir(var_tif_folder):
            os.mkdir(var_tif_folder)

        # file conversion and reprojection
        for time in xmrg_df.index:
            var_xmrg_path = os.path.join(var_xmrg_folder, xmrg_df[var].ix[time])
            if os.path.isfile(var_xmrg_path):
                var_asc_path = var_xmrg_path+'.asc'
                var_tif_name = os.path.basename(var_xmrg_path)+'.tif'
                var_tif_path = os.path.join(var_tif_folder, var_tif_name)
                cmd_xmrgtoasc = 'xmrgtoasc -i {} -p ster -n -999'.format(var_xmrg_path)
                cmd_reproj = 'gdalwarp -overwrite -t_srs "{}" {} {}'.format(proj4_string, var_asc_path, var_tif_path)

                if not os.path.isfile(var_tif_path):
                    try:
                        for command in [cmd_xmrgtoasc, cmd_reproj]:
                            result1 = subprocess.call(shlex.split(command))
                        xmrg_df[var].ix[time] = os.path.basename(var_tif_path)
                    except Exception as e:
                        print 'failed to convert {}'.format(var_xmrg_path)
                        fail_files.append(var_xmrg_path)
                        continue
                else:
                    xmrg_df[var].ix[time] = os.path.basename(var_tif_path)
            else:
                print 'no xmrg file {}'.format(var_xmrg_path)
                fail_files.append(var_xmrg_path)

        if fail_files:
            with open(os.path.join(result_folder, 'fail_tif_{}.txt'.format(var)), 'w') as f:
                f.write('\n'.join(fail_files))
    else:
        print 'no {} found'.format(var_xmrg_folder)

xmrg_df.to_csv(os.path.join(result_folder, 'tif_df.csv'))

print 'sublimation_analysis_2: xrmg file conversion and reprojection is done'
