"""
This is used to download the cbrfc climate forcing data from 20100801 - 20170930
http://www.cbrfc.noaa.gov/outgoing/rti/netcdf800m/
download the wyXXXX folders
"""

import os
from datetime import datetime, timedelta
import urllib
import tarfile
import gzip
import shutil
import csv

# create data folder for final results
data_folder = './final_data'
if os.path.isdir(data_folder):
    shutil.rmtree(data_folder)

os.mkdir(data_folder)

# set date for data download
start_date = datetime(2010, 8, 1)
end_date = datetime(2017, 9, 30)
total_days = (end_date - start_date).days

fail_list = {}
for i in range(0, total_days+1):

    # form date index and url
    date_index = start_date + timedelta(days=i)
    date_index_str = date_index.strftime('%Y%m%d')
    if date_index.month > 9:
        water_year = date_index.year + 1
    else:
        water_year = date_index.year

    url = 'http://www.cbrfc.noaa.gov/outgoing/rti/netcdf800m/wy{}/obs.cbrfc.{}.tar.gz'.format(water_year, date_index_str)
    gz_name = url.split('/')[-1]

    print 'download ' + date_index_str
    try:
        # download file
        urllib.urlretrieve(url, gz_name)  # download .gz file

        # unzip .tar.gz file
        tar = tarfile.open(gz_name, 'r:gz')
        tar.extractall()
        tar.close()

        # gzip .nc file and move to folder
        nc_name = 'mm_{}.nc'.format(date_index_str)
        nc_gz_name = '{}.gz'.format(nc_name)
        with open(nc_name, 'rb') as f_in, gzip.open(nc_gz_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        shutil.move(nc_gz_name, data_folder)

    except Exception as e:
        fail_list[date_index_str] = url

with open('fail_list.csv', 'wb') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in fail_list.items():
       writer.writerow([key, value])

print 'data download finished'