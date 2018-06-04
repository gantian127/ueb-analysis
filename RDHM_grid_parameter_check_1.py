"""
This is used to convert the RDHM xmrg parameter grids for comparions and checking purpose

step1: convert .gz to clipped .tif
- unzip .gz
- convert xmrg to .asc and .asc to .tif with projf_string
- create clipper file with example model output
- clip the parameter files with clipper shape file



"""

import os

import gdalnumeric
import numpy as np
import matplotlib.pyplot as plt
import gzip
import subprocess
import shlex
import gdal
from time import strptime
import pandas as pd

# user settings  ####################################################################################################
data_folder = '/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/test/params1k.co_ueb/'
clipper_template = 'we0101198906z.gz'
parameter_folder = os.path.join(data_folder,'parameter_result')


if not os.path.isdir(parameter_folder):
        os.mkdir(parameter_folder)


proj4_string = 'PROJCS["Sphere_ARC_INFO_Stereographic_North_Pole",GEOGCS["GCS_Sphere_ARC_INFO",DATUM["Sphere_ARC_INFO",SPHEROID["Sphere_ARC_INFO",6370997,0]],PRIMEM["Greenwich",0],\
UNIT["degree",0.0174532925199433]],PROJECTION["Polar_Stereographic"],PARAMETER["latitude_of_origin",60.00681388888889],PARAMETER["central_meridian",-105],\
PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'


# step1: convert .gz to watershed .tif ################################################################################
# unzip .gz files as xmrg file
gz_path_list = [os.path.join(data_folder,file_name) for file_name in os.listdir(data_folder) if '.gz' in file_name]

xmrg_path_list = []
for gz_path in gz_path_list:
    xmrg_path = gz_path[:-3]
    if not os.path.isfile(xmrg_path):
        try:
            with gzip.open(gz_path, 'rb') as inf:
                with open(xmrg_path, 'wb') as outf:
                    content = inf.read()
                    outf.write(content)
        except Exception as e:
            print 'failed to unzip file !'
            print gz_path
            continue

    xmrg_path_list.append(xmrg_path)


# convert xmrg file as .asc files and .asc file as .tif with projection
tif_path_list = []
for xmrg_path in xmrg_path_list:
    asc_path = xmrg_path + '.asc'
    tif_path = asc_path.replace('.asc', '.tif')
    cmd_xmrgtoasc = 'xmrgtoasc -i {} -p ster -n -999'.format(xmrg_path)
    cmd_reproj = 'gdalwarp -overwrite -t_srs "{}" {} {}'.format(proj4_string, asc_path, tif_path)

    if not os.path.isfile(tif_path):
        for command in [cmd_xmrgtoasc, cmd_reproj]:
            try:
                for command in [cmd_xmrgtoasc, cmd_reproj]:
                    result = subprocess.call(shlex.split(command))

            except Exception as e:
                print 'failed to reproject data!'
                print xmrg_path
                continue
    tif_path_list.append(tif_path)


# create a template clip shape file
clipper_tif_path = os.path.join(data_folder, clipper_template.replace('.gz', '.tif'))
clipper_shape_path = os.path.join(data_folder, 'clipper.shp')

if os.path.isfile(clipper_tif_path):
    try:
        clipper_template = gdal.Open(clipper_tif_path)
        x_size = clipper_template .RasterXSize
        y_size = clipper_template .RasterYSize
        swe_template = None
        if not os.path.isfile(clipper_shape_path):
            cmd_clipper = "gdal_polygonize.py {} -f 'ESRI Shapefile' {}".format(clipper_tif_path, clipper_shape_path)
            subprocess.call(shlex.split(cmd_clipper))
    except Exception as e:
        print 'falied to create clipper shape file for modis data'


# clip the .tif using clipper
clip_path_list = []
for tif_path in tif_path_list:
    clip_path = os.path.join(parameter_folder, os.path.basename(tif_path))
    cmd_clip = "gdalwarp -overwrite -ts {} {} -cutline {} -crop_to_cutline -dstalpha {} {}".format(x_size, y_size,
                                                                                                   clipper_shape_path,
                                                                                                   tif_path,
                                                                                                   clip_path)
    if not os.path.isfile(clip_path):
        try:
            subprocess.call(shlex.split(cmd_clip))
        except Exception as e:
            print 'failed to clip data'
            print tif_path
            continue

    clip_path_list.append(clip_path)

print 'RDHM parameter analysis step1 is done!'


