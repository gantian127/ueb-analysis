"""
This is aimed to convert the raw STC-SSP snow data to raster data. This code is based on the RTI info and python code

steps: (30min/year)
- create hdf5 as asc
- convert asc to tif with RDHM projection

STC-SSP info:
- format: hdf5
- projection: sinusoidal projection http://spatialreference.org/ref/sr-org/modis-sinusoidal/
"""

import numpy as np
import pandas as pd
import subprocess
import shlex
import os
import h5py


# step 1: user settings  ################################################################
start_year = 2001
end_year = 2014

hdf5_dir = r'/Projects/STC-SSP/'
result_dir = os.path.join(os.getcwd(), 'STC_SSP_Snow_cover')
if not os.path.isdir(result_dir):
    os.mkdir(result_dir)

sinus_string = 'PROJCS["Sinusoidal",GEOGCS["GCS_Undefined",DATUM["D_Undefined",SPHEROID["User_Defined_Spheroid",6371007.181,0.0]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.017453292519943295]],PROJECTION["Sinusoidal"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],UNIT["Meter",1.0]]'
polar_string = 'PROJCS["Sphere_ARC_INFO_Stereographic_North_Pole",GEOGCS["GCS_Sphere_ARC_INFO",DATUM["Sphere_ARC_INFO",SPHEROID["Sphere_ARC_INFO",6370997,0]],PRIMEM["Greenwich",0],\
UNIT["degree",0.0174532925199433]],PROJECTION["Polar_Stereographic"],PARAMETER["latitude_of_origin",60.00681388888889],PARAMETER["central_meridian",-105],\
PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'

# step 2: .mat to .asc ################################################################
for year in range(start_year, end_year+1):

    mat_file = os.path.join(hdf5_dir, 'UpperColorado_CY{}.mat'.format(year))

    if os.path.isfile(mat_file):
        # Get data from hdf
        with h5py.File(mat_file, 'r') as f:
            sc_data = np.array(f['Sc'])
            RefMatrix = np.array(f['RefMatrix'])

        # Define asc header
        nrows = np.shape(np.transpose(sc_data[0]))[0]
        ncols = np.shape(np.transpose(sc_data[0]))[1]
        xll = RefMatrix[0][-1]
        yll = RefMatrix[1][-1] - (nrows * RefMatrix[0][1])

        header_txt = "ncols " + str(ncols) + "\n\
        nrows " + str(nrows) + "\n\
        xllcorner " + str(xll) + "\n\
        yllcorner " + str(yll) + "\n\
        cellsize " + str(RefMatrix[0][1]) + "\n\
        NODATA_value -32768"

        dates = pd.date_range('1/1/' + str(year), '12/31/' + str(year))
        for index, day in enumerate(dates):
            try:
                # Create .asc files
                asc_path = os.path.join(result_dir, 'STC_SSP_{}_Sc.asc'.format(dates[index].strftime("%Y%m%d")))
                tif_path = asc_path.replace('.asc', '.tif')
                np.savetxt(asc_path,
                           np.transpose(sc_data[index]),
                           delimiter=' ', fmt='%1.6e', header=header_txt, comments='')

                # convert .asc to .tif files
                cmd = 'gdalwarp -overwrite -s_srs "{}" -t_srs "{}"  -tr 463.3127165 463.3127165 {} {}'.format(sinus_string, polar_string,  asc_path, tif_path)
                subprocess.Popen(shlex.split(cmd))
            except Exception as e:
                print 'failed for {}'.format(day)

        # clear space
        del sc_data
        del RefMatrix
    else:
        print 'No hdf5 {}'.format(mat_file)

print 'File conversion is done!'