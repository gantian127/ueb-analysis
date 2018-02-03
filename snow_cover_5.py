"""
This is the formal script for snow cover area analysis

step5: prepare terrain data and analyze oa results

requirements:
- make sure snow_cover_1.py and snow_cover_2.py is executed.
- add hydrods_python_client

step:
- create 30m slope, aspect, land cover data
- reproject and clip terrain data using template raster

"""

import os
import subprocess
import shlex

import pandas as pd
import gdal

from hydrods_python_client import HydroDS


# User settings #############################################################################################
leftX, topY, rightX, bottomY = -108.15, 38.06, -107.41, 37.16  # watershed bounding box
watershed = 'animas'
epsgCode = 26912
proj4_string = '+proj=stere +lat_0=90.0 +lat_ts=60.0 +lon_0=-105.0 +k=1 +x_0=0.0 +y_0=0.0 +a=6371200 +b=6371200 +units=m +no_defs'


folder_name = '{}_snow_analysis_result'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
model_snow_date_path = os.path.join(result_folder, 'model_snow_date.csv')
terrain_folder = os.path.join(result_folder, 'terrain')
if not os.path.isdir(terrain_folder):
    os.mkdir(terrain_folder)

# step1 create slope, aspect, land cover data ##############################################################
# login HydroDS and clean space
HDS = HydroDS(username='tianG', password='tianGan_2016')
MyFiles = HDS.list_my_files()
for item in HDS.list_my_files():
    try:
        HDS.delete_my_file(item.split('/')[-1])
    except Exception as e:
        print('failed to delete:')
        print(item)
        continue


# Subset DEM and Delineate Watershed
input_static_DEM = 'nedWesternUS.tif'
subset_raster = watershed + '_dem.tif'
subsetDEM = HDS.subset_raster(input_raster=input_static_DEM, left=leftX, top=topY, right=rightX,
                                      bottom=bottomY, output_raster=subset_raster)

watershed_raster = subset_raster[:-4]+'_watershed.tif'
watershedDEM = HDS.project_resample_raster(input_raster_url_path=subsetDEM['output_raster'],
                                           cell_size_dx=30, cell_size_dy=30, epsg_code=epsgCode,
                                           output_raster=watershed_raster, resample='bilinear')
# aspect, slope, landcover
aspect_raster = watershed + '_aspect.tif'
aspect = HDS.create_raster_aspect(input_raster_url_path=watershedDEM['output_raster'],
                                  output_raster=aspect_raster)

slope_raster = watershed + '_slope.tif'
slope = HDS.create_raster_slope(input_raster_url_path=watershedDEM['output_raster'],
                                output_raster=slope_raster)

nlcd_raster_resource = 'nlcd2011CONUS.tif'
nlcd_raster = watershed + '_nlcd.tif'
nlcd = HDS.project_clip_raster(input_raster=nlcd_raster_resource,
                               ref_raster_url_path=watershedDEM['output_raster'],
                               output_raster=nlcd_raster)

# download to local disk
results = [subsetDEM, watershedDEM, aspect, slope, nlcd]
for result in results:
    file_name = os.path.basename(result['output_raster'])
    HDS.download_file(file_url_path=result['output_raster'], save_as=os.path.join(terrain_folder, file_name))

print 'HydroDS data processing is done'


# step2: resample and clip raster ########################################################
# load snow date info
snow_date = pd.DataFrame.from_csv(model_snow_date_path, header=0)

# create a template clip shape file
try:
    swe_proj_path = snow_date['snow17_proj_folder'][0]  # provide a path that is the projected swe tif file
    clipper_file_path = os.path.join(terrain_folder, 'terrain_clipper.shp')

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
tif_names = [watershed_raster, aspect_raster, slope_raster, nlcd_raster]
for tif_name in tif_names:
    tif_path = os.path.join(terrain_folder, tif_name)
    if os.path.isfile(tif_path):
        terrain_proj_path = tif_path[:-4]+'_proj.tif'
        terrain_clip_path = terrain_proj_path.replace('_proj.tif', '_clip.tif')

        cmd_reproj = 'gdalwarp -overwrite -t_srs "{}" -tr 30 30 {} {}'.format(proj4_string, tif_path, terrain_proj_path)
        cmd_clip = "gdalwarp -overwrite -ts {} {} -cutline {} -crop_to_cutline -dstalpha {} {} ".format(x_size, y_size,
                                                                                                       clipper_file_path,
                                                                                                       terrain_proj_path,
                                                                                                       terrain_clip_path)
        try:
            for command in [cmd_reproj, cmd_clip]:
                subprocess.call(shlex.split(command))
        except Exception as e:
            continue

print 'snow_cover_5: terrain data reprojection, clip, resample is done'