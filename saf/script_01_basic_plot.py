#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 1: Basic Plot
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
from netCDF4 import Dataset     # read / write NetCDF4 files
import matplotlib.pyplot as plt # plotting library

# open the file using the NetCDF4 library
file = Dataset("../samples/NETCDF4_LSASAF_MSG_DLST-MAX10D_MSG-Disk_202307112345.nc")

# extract the data (lines and columns for a single time)
data = file.variables['LST_MAX'][0,:,:]

# choose the plot size (width x height, in inches)
plt.figure(figsize=(7,7))

# plot the image
plt.imshow(data, origin='upper', cmap='jet')

# save the image
plt.savefig('image_1.png')

# show the image
plt.show()