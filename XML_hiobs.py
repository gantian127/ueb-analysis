"""
This is used to convert the RTI USGS daily discharge xml file as ascii files
"""

import glob
import os
import xml.etree.ElementTree as ET
import re
import gzip

# convert all the files
data_dir = r'D:\3_NASA_Project\hisobs_natural_flow_RTI\hisobs_natural_flow'
data_type = 'QME'   # if need to convert QINE data as ascii change this variable as 'QINE'
allfiles = glob.glob(os.path.join(data_dir, '*{}.xml*'.format(data_type)))

error_file = []

for file in allfiles:
    try:
        with gzip.open(file, 'rb') as f:
            file_content = f.read()
        root = ET.fromstring(file_content)

        # get the station, units and location info
        for child in root:
            t = child.tag
            a = child.attrib
        for x in child.iter("{http://www.wldelft.nl/fews/PI}locationId"):
            loc = x.text
        for x in child.iter("{http://www.wldelft.nl/fews/PI}stationName"):
            station = x.text
        for x in child.iter("{http://www.wldelft.nl/fews/PI}units"):
            units = x.text

        # write data to asci file
        events = child.findall('{http://www.wldelft.nl/fews/PI}event')
        fileBASE = os.path.basename(file)
        filename = re.split(r'[.\s]\s*', fileBASE)[0]

        with open(os.path.join(data_dir, filename + '.{}.txt'.format(data_type)), 'a') as ascfile:
            ascfile.write('# stationName: ' + station + '\n')
            ascfile.write('# locationId: ' + loc + '\n')
            ascfile.write('# units: ' + units + '\n')
            for event in events:
                ascfile.write('{} {}, {}'.format(event.attrib.get('date'), event.attrib.get('time'),
                                                 event.attrib.get('value')) + '\n')

        del root
        del child

    except Exception as e:
        error_file.append(file)