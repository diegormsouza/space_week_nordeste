#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 10: Reading information every "x" pixels
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
from netCDF4 import Dataset                 # wead / rrite NetCDF4 files
import matplotlib.pyplot as plt             # plotting library
import time as t                            # time access and conversion

# start the time counter
print('script started.')
start = t.time()

# open the file using the NetCDF4 library
file = Dataset("../samples/NETCDF4_LSASAF_M01-AVHR_EDLST-DAY_GLOBE_202307220000.nc")

# extract the data
data = file.variables['LST-day'][0,::10,::10]

# choose the plot size (width x height, in inches)
plt.figure(figsize=(10,5))

# plot the image
plt.imshow(data, origin='lower', cmap='jet')

# show the image
plt.show()

# print the total processing time
print('total processing time:', round((t.time() - start),2), 'seconds.')