"""
This is the 2nd version formal script for snow cover area analysis

step2: process modis and swe with same projection and resolution

step:
- swe: xmrg -> tif -> reproject
- modis: reproject -> clip -> resample

result:
- swe: outside watershed boundary, no data value is -1;
       inside watershed, no missing data all values are >=0
- modis: band 0 as the actual value (255 as no data area).
         band1 as mask (0 as no data area) recomended as mask to find out the watershed boundary

"""

import os
import subprocess
import shlex

import pandas as pd
import gdal


# default user settings apply to all steps ####################################################
watershed = 'DOLC2'
folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)

# folders/files created by step 1 script
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')
modis_snowdate_folder = os.path.join(result_folder, 'modis_snowdate_folder')
swe_snowdate_folders = [os.path.join(result_folder, name) for name in ['snow17_snowdate_folder', 'ueb_snowdate_folder']]

# reprojection info
# proj4_string = '+proj=stere +lat_0=90.0 +lat_ts=60.0 +lon_0=-105.0 +k=1 +x_0=0.0 +y_0=0.0 +a=6371200 +b=6371200 +units=m +no_defs'  # polar stereographic
proj4_string = 'PROJCS["Sphere_ARC_INFO_Stereographic_North_Pole",GEOGCS["GCS_Sphere_ARC_INFO",DATUM["Sphere_ARC_INFO",SPHEROID["Sphere_ARC_INFO",6370997,0]],PRIMEM["Greenwich",0],\
UNIT["degree",0.0174532925199433]],PROJECTION["Polar_Stereographic"],PARAMETER["latitude_of_origin",60.00681388888889],PARAMETER["central_meridian",-105],\
PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'


# Step 1 swe: format conversion and reprojection  ##############################################
print 'step1 : convert swe xmrg as tif and reproject'

# load snow date info
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)

# data processing
for swe_xmrg_folder in swe_snowdate_folders:

    if os.path.isdir(swe_xmrg_folder):
        fail_swe_xmrg = []
        # create projection folder and dataframe column
        xmrg_col_name = os.path.basename(swe_xmrg_folder)
        proj_col_name = os.path.basename(swe_xmrg_folder).replace('snowdate', 'proj')
        snow_date[proj_col_name] = 'invalid'
        swe_proj_folder = os.path.join(result_folder, proj_col_name)

        if not os.path.isdir(swe_proj_folder):
            os.mkdir(swe_proj_folder)

        # file conversion and reprojection
        for time in snow_date.index:
            swe_xmrg_path = snow_date[xmrg_col_name].ix[time]
            if os.path.isfile(swe_xmrg_path):
                swe_tif_path = swe_xmrg_path+'.asc'
                swe_proj_name = os.path.basename(swe_xmrg_path)+'_proj.tif'
                swe_proj_path = os.path.join(swe_proj_folder, swe_proj_name)
                cmd_xmrgtoasc = 'xmrgtoasc -i {} -p ster -n -999'.format(swe_xmrg_path)
                cmd_reproj = 'gdalwarp -overwrite -t_srs "{}" {} {}'.format(proj4_string, swe_tif_path, swe_proj_path)

                if not os.path.isfile(swe_proj_path):
                    try:
                        for command in [cmd_xmrgtoasc, cmd_reproj]:
                            result1 = subprocess.call(shlex.split(command))
                        snow_date[proj_col_name].ix[time] = swe_proj_path
                    except Exception as e:
                        print 'failed to reproject model swe!'
                        print swe_xmrg_path
                        print os.path.isfile(swe_xmrg_path)
                        fail_swe_xmrg.append(swe_xmrg_path)
                        continue
                else:
                    snow_date[proj_col_name].ix[time] = swe_proj_path

        snow_date.to_csv(model_snow_date_path)
        with open(os.path.join(result_folder, 'fail_{}.txt'.format(proj_col_name)), 'w') as f:
            f.write('\n'.join(fail_swe_xmrg))
    else:
        print 'no folder {}'.format(swe_xmrg_folder)

print 'swe xmrg conversion and reprojection is done'


# step2  modis: reproject -> clip -> resample #######################################################
print 'step2 : modis reproject, clip , resample'

# load snow date info
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)

# create modis proj folder
modis_proj_folder = os.path.join(result_folder, 'modis_proj_folder')
if not os.path.isdir(modis_proj_folder):
    os.mkdir(modis_proj_folder)

# create a template clip shape file
try:
    swe_proj_path = snow_date['snow17_proj_folder'][0]  # provide a path that is the projected swe tif file
    clipper_file_path = os.path.join(modis_proj_folder, 'modis_clipper.shp')

    if swe_proj_path:
        swe_template = gdal.Open(swe_proj_path)
        x_size = swe_template.RasterXSize
        y_size = swe_template.RasterYSize
        swe_template = None

    cmd_clipper = "gdal_polygonize.py {} -f 'ESRI Shapefile' {}".format(swe_proj_path, clipper_file_path)
    subprocess.call(shlex.split(cmd_clipper))
except Exception as e:
    print 'falied to create clipper shape file for modis data'


# reprojection and clip
tif_col_name = os.path.basename(modis_snowdate_folder)
proj_col_name = tif_col_name.replace('snowdate','proj')
snow_date[proj_col_name] = 'invalid'
fail_modis_proj = []
for time in snow_date.index:
    modis_tif_path = snow_date[tif_col_name].ix[time]
    if os.path.isfile(modis_tif_path):
        modis_proj_path = modis_tif_path[:-4]+'_proj.tif'
        modis_clip_name = os.path.basename(modis_proj_path).replace('_proj.tif', '_clip.tif')
        modis_clip_path = os.path.join(modis_proj_folder, modis_clip_name)

        # reproject and clip as two step: because if with 1 step, the x and y resolution will not be the same as the swe xmrg resolution.
        if not os.path.isfile(modis_proj_path):
            cmd_reproj = 'gdalwarp -overwrite -t_srs "{}" -tr 463 463 {} {}'.format(proj4_string, modis_tif_path, modis_proj_path)
        else:
            cmd_reproj = ''
        cmd_clip = "gdalwarp -overwrite -ts {} {} -cutline {} -crop_to_cutline -dstalpha {} {}".format(x_size, y_size, clipper_file_path, modis_proj_path, modis_clip_path)

        if not os.path.isfile(modis_clip_path):
            try:
                for command in [cmd_reproj, cmd_clip]:
                    if command:
                        subprocess.call(shlex.split(command))
                snow_date[proj_col_name].ix[time] = modis_clip_path
            except Exception as e:
                print 'failed to reproject modis swe!'
                print modis_tif_path
                print os.path.isfile(modis_tif_path)
                fail_modis_proj.append(modis_tif_path)
                continue
        else:
            snow_date[proj_col_name].ix[time] = modis_clip_path

snow_date.to_csv(model_snow_date_path)
with open(os.path.join(result_folder, 'fail_{}.txt'.format(proj_col_name)), 'w') as f:
    f.write('\n'.join(fail_modis_proj))

print 'snow_area_analysis_2: swe, modis reprojection, clip, resample is done'