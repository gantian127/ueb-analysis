"""
This is the 1st version sublimation analysis

step4: convert terrain xmrg file as tif file

requirment:
- folder includes all the xmrg terrain input: slope, aspect, lai, hcan, cc

step:
- terrain: xmrg -> tif -> reproject

"""

import os

import gzip
import subprocess
import shlex
import gdal

from hydrods_python_client import HydroDS

# user settings  ####################################################################################################
watershed = 'McPhee'
leftX, topY, rightX, bottomY = -108.80, 38.05, -107.66, 37.22 # watershed bounding box
epsgCode = 26912

folder_name = '{}_sublimation_analysis'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
terrain_folder = '/Projects/Tian_workspace/rdhm_ueb_modeling/McPhee_MPHC2/Sublimation_analysis/terrain/'

proj4_string = 'PROJCS["Sphere_ARC_INFO_Stereographic_North_Pole",GEOGCS["GCS_Sphere_ARC_INFO",DATUM["Sphere_ARC_INFO",SPHEROID["Sphere_ARC_INFO",6370997,0]],PRIMEM["Greenwich",0],\
UNIT["degree",0.0174532925199433]],PROJECTION["Polar_Stereographic"],PARAMETER["latitude_of_origin",60.00681388888889],PARAMETER["central_meridian",-105],\
PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'


# step1: convert terrain xmrg as tif ################################################################################
# unzip .gz files as xmrg file
gz_path_list = [os.path.join(terrain_folder , file_name) for file_name in os.listdir(terrain_folder) if '.gz' in file_name]

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


# step2 use HydroDS to download dem data ##############################################################
# login HydroDS and clean space
HDS = HydroDS(username='tianG', password='tianGan_2016')
MyFiles = HDS.list_my_files()
for item in HDS.list_my_files():
    try:
        print item
        #HDS.delete_my_file(item.split('/')[-1])
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


# step3: resample and clip raster ########################################################
# create a template clip shape file
try:
    swe_proj_path = os.path.join(terrain_folder, 'ueb_lai.tif')  # provide a path that is the projected swe tif file
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

print 'sublimation_analysis_4: terrain data processing is done'