"""
This is to calculate the zonal stats table of the RDHM parameter grid

requirements:
- provide the parameter tif files
- provide the shape file as zone mask (same projection)

step:
- calculate zonal stats
- convert stats dbf table as csv

"""
import os
import arcpy
from arcpy import env


# arcpy settings
arcpy.CheckOutExtension("Spatial")  # remember this otherwise will show licence error
arcpy.env.overwriteOutput = True

# user settings
tif_folder_list = [r'C:\Users\jamy\Desktop\pe_grid']
zone_shape = r'C:\Users\jamy\Desktop\test\reproject.shp'
zone_field = 'CH5_ID'

for tif_folder in tif_folder_list:
    try:
        # setup
        env.workspace = tif_folder

        result_dir = os.path.join(tif_folder, 'zonal_stat_results')
        if not os.path.isdir(result_dir):
            os.mkdir(result_dir)

        tif_file_list = [os.path.join(tif_folder, file_name) for file_name in os.listdir(tif_folder) if '.tif' in file_name]

        for tif_file in tif_file_list:
            # get zonal stats
            dbf_table = os.path.join(result_dir, os.path.basename(tif_file).replace('.tif', '.dbf'))
            arcpy.sa.ZonalStatisticsAsTable(zone_shape, zone_field, tif_file, dbf_table, "DATA", 'ALL')

            # convert dbf table as .csv
            outLocation=result_dir
            outTable = os.path.basename(dbf_table).replace('.dbf', '.csv')
            arcpy.TableToTable_conversion(dbf_table, outLocation, outTable)
    except Exception as e:
        print 'Failed zonal stats for {}'.format(tif_folder)
        continue

print 'Zonal Stat is done !'
