#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 4: Regional plot
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
from netCDF4 import Dataset         # read / write NetCDF4 files
import matplotlib.pyplot as plt     # plotting library
from datetime import datetime       # basic date and time types
import cartopy, cartopy.crs as ccrs # produce maps and other geospatial data analyses
import cartopy.feature as cfeature  # common drawing and filtering operations
import numpy as np                  # import the Numpy package

# open the file using the NetCDF4 library
file = Dataset("../samples/NETCDF4_LSASAF_MSG_DLST-MAX10D_MSG-Disk_202307112345.nc")

# select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-75.0, -37.00, -33.00, 8.00] # Brazil

#-------------------------------------------------------------------------------------------------------------------

# reading lats and lons
lats = file.variables['lat'][:]
lons = file.variables['lon'][:]

# latitude lower and upper index
latli = np.argmin( np.abs( lats - extent[1] ) )
latui = np.argmin( np.abs( lats - extent[3] ) )

# longitude lower and upper index
lonli = np.argmin( np.abs( lons - extent[0] ) )
lonui = np.argmin( np.abs( lons - extent[2] ) )

# extract the data
data = file.variables['LST_MAX'][ 0 , latui:latli , lonli:lonui ]

#-------------------------------------------------------------------------------------------------------------------

# choose the plot size (width x height, in inches)
plt.figure(figsize=(7,7))

# use the PlateCarree projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# add some various map elements to the plot
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)

# define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# plot the image
img = ax.imshow(data, vmin=-10, vmax=35, origin='upper', extent=img_extent, cmap='jet')

# add coastlines, borders and gridlines
ax.coastlines(resolution='50m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='gray', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 181, 5), ylocs=np.arange(-90, 91, 5), draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xpadding = -5
gl.ypadding = -5

# add a colorbar
plt.colorbar(img, label='Land Surface Temperature - Maximum (°C) - 10 Day Composite', extend='both', orientation='vertical', pad=0.05, fraction=0.05)

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
plt.savefig('image_4.png')

# show the image
plt.show()