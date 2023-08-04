#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 2: Metadata, title, legend and date
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
from netCDF4 import Dataset     # read / write NetCDF4 files
import matplotlib.pyplot as plt # plotting library
from datetime import datetime   # basic date and time types

# open the file using the NetCDF4 library
file = Dataset("../samples/NETCDF4_LSASAF_MSG_DLST-MAX10D_MSG-Disk_202307112345.nc")

# extract the data
data = file.variables['LST_MAX'][0,:,:]

#-------------------------------------------------------------------------------------------------------------------

# choose the plot size (width x height, in inches)
plt.figure(figsize=(7,7))

# plot the image
plt.imshow(data, vmin=-10, vmax=35, origin='upper', cmap='jet')

# add a colorbar
plt.colorbar(label='Land Surface Temperature - Maximum (°C) - 10 Day Composite', extend='both', orientation='horizontal', pad=0.05, fraction=0.05)

# get the date
date_str  = file.getncattr('time_coverage_start')
date_format = '%Y-%m-%dT%H:%M:%SZ'
date_obj = datetime.strptime(date_str, date_format)
date = date_obj.strftime('%Y-%m-%d %H:%M:%S UTC')

# add a title
plt.title(f'MSG/SEVIRI -  LST - 10 Day Composite (Pixel-Wise Maximum)\n{date}', fontweight='bold', fontsize=10, loc='left')
plt.title('Space Week Nordeste 2023', fontsize=10, loc='right')

#-------------------------------------------------------------------------------------------------------------------

# save the image
plt.savefig('image_2.png')

# show the image
plt.show()