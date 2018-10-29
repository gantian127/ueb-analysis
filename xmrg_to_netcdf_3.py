"""
This is used for the use case in netCDF paper. It converts the RDHM xmrg output as one netCDF file for sharing.

step3: get tif data and write as netCDF file

steps: (17min/22yr)
- get tif file and create netCDF template
- read all the tif file and create as numpy array
- add numpy array in the netCDF template
- add time dimension in the netCDF template

"""

import os
import subprocess
import shlex

import gdalnumeric
import netCDF4
import numpy as np
import pandas as pd

# step1: user settings #####################################################
watershed = 'McPhee'
folder_name = '{}_xmrg_to_netCDF'.format(watershed)
result_folder = os.path.join(os.getcwd(), folder_name)
tif_df_path = os.path.join(result_folder, 'tif_df.csv')

tif_flip = True
flip_axis = 1

start_date = '1988-10-1'
end_date = '2010-06-30'

# step2: get tif data #######################################################
tif_df = pd.read_csv(tif_df_path, header=0, index_col=0)
tif_df.index = tif_df.index.to_datetime()
if start_date and end_date:
    tif_df = tif_df[(tif_df.index>=start_date) & (tif_df.index<end_date)]

for var in tif_df.columns:
    var_tif_folder = os.path.join(result_folder, 'tif_folder_{}'.format(var))
    var_stack_list = []

    if os.path.isdir(var_tif_folder):
        for time in tif_df.index:
            tif_path = os.path.join(var_tif_folder, tif_df[var].ix[time])
            tif_array = gdalnumeric.LoadFile(tif_path)
            var_stack_list.append(tif_array)

        # create tif array
        var_tif_array = np.stack(var_stack_list)
        if tif_flip:
            var_tif_array = np.flip(var_tif_array, axis=flip_axis)  # this is aimed to make the tif array y axis same as netcdf array y axis
        np.save(os.path.join(result_folder, '{}_tif_array'.format(var)), var_tif_array)

        # create template nc file
        nc_tem_path = os.path.join(result_folder,'{}_temp.nc'.format(var))
        cmd = "gdal_translate -of netCDF -co 'FORMAT=NC4' {} {}".format(tif_path, nc_tem_path)
        subprocess.Popen(shlex.split(cmd)).wait()

    else:
        print 'No folder for {}'.format(var_tif_folder)

# step3: create netCDF file ##############################################################
for var in tif_df.columns:
    nc_tem_path = os.path.join(result_folder, '{}_temp.nc'.format(var))
    root = netCDF4.Dataset(nc_tem_path, 'a')

    # define time variable
    time_dim = root.createDimension("time", None)
    time_var = root.createVariable("time", "f4", ("time",))
    time_var.units = 'hours since {} 00:00:00.0 UTC'.format(tif_df.index[0].strftime('%Y-%m-%d'))
    time_var.calendar = 'standard'
    time_dates = tif_df.index.tolist() # use netcdf string conversion function
    time_var[:] = netCDF4.date2num(time_dates, units=time_var.units, calendar=time_var.calendar)

    # define data variable
    band = root.variables['Band1']
    band_data = band[:]
    mask = np.ma.getmask(band_data)
    grid_mapping = band.grid_mapping
    fill_value = band_data.get_fill_value()

    # remember to specify fill value otherwise will show strange data, the data type is 32 float.
    nc_var = root.createVariable(var, 'f4', ("time", "y", "x"), fill_value=fill_value)
    nc_var.grid_mapping = grid_mapping
    tif_array_data = np.load(os.path.join(result_folder, '{}_tif_array.npy'.format(var)))
    tif_array_mask = np.repeat(mask[np.newaxis, :, :], tif_array_data.shape[0], axis=0)
    nc_var_data = np.ma.masked_array(tif_array_data, mask=tif_array_mask)
    nc_var[:] = nc_var_data

    # # define global attributes
    # root.title = 'Model simulation of snow water equivalent in '
    # root.abstract = ''
    # root.creator_name = 'Tian Gan'
    # root.summary = ''
    # root.keywords = 'snow water equivalent '
    root.close()

    # remove band variable
    nc_path = os.path.join(result_folder, '{}_netcdf.nc'.format(var))
    nco_cmd = 'ncks -x -v Band1 {} {}'.format(nc_tem_path, nc_path)
    subprocess.Popen(shlex.split(nco_cmd)).wait()

print 'xmrg to netCDF is done!'


