#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 7: Masking regions
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
from netCDF4 import Dataset                # read / write NetCDF4 files
import matplotlib.pyplot as plt            # plotting library
from datetime import datetime              # basic date and time types
import cartopy, cartopy.crs as ccrs        # produce maps and other geospatial data analyses
import cartopy.feature as cfeature         # common drawing and filtering operations
import cartopy.io.shapereader as shpreader # import shapefiles
import numpy as np                         # import the Numpy package
import matplotlib                          # comprehensive library for creating visualizations in Python
import geopandas as gp                     # make working with geospatial data in python easier
import regionmask                          # create masks of geographical regions

# open the file using the NetCDF4 library
file = Dataset("../samples/NETCDF4_LSASAF_MSG_DLST-MAX10D_MSG-Disk_202307112345.nc")

# select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-50.0, -20.00, -33.00, 0.00] # Brazilian northeast

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

# masking a region using a shapefile -------------------------------------------------------------------------------

# reading lats and lons
lats = file.variables['lat'][latui:latli]
lons = file.variables['lon'][lonli:lonui]

# read the shapefile with Geopandas
regions = gp.read_file('regioes_2010.shp')
#display(regions)

# read the subregions from the shapefile
brazilian_regions = regionmask.from_geopandas(regions, names="sigla", abbrevs="nome", name="sigla")
#print(brazilian_regions)

# create the mask with a lat lon array
mask = brazilian_regions.mask(lons, lats)

# get the index for a given subregion
index = brazilian_regions.names.index("NE")

# mask the data for a given subregion
data = np.where(mask==index, data, np.nan)

# fill value also as nan
fillvalue = file.variables['LST_MAX']._FillValue
data[data==fillvalue] = np.nan

#-------------------------------------------------------------------------------------------------------------------

# create a custom color scale:
# reference color scale from EUMETSAT: https://twitter.com/LSA_SAF/status/1493929742604673027
# HEX values got from: https://imagecolorpicker.com/:
colors = ["#18f6c3", "#19f6db", "#1adddf", "#2edcff", "#6edbf9",
          "#a1eaff", "#cce9ff", "#bdbede", "#a4a6d5", "#8b8cc2",
          "#8a6cc0", "#a36be0", "#8754c4", "#6b40a5", "#5222a6",
          "#4018a8", "#21198b", "#1a2f89", "#1856a0", "#1987c5",
          "#1990e0", "#1ac4ff", "#2eddff", "#6edbf9", "#cce9ff",
          "#ffffbf", "#ffff8d", "#ffff31", "#ffff31", "#ffc024",
          "#ffa130", "#ff6a3e", "#fd3d30", "#fe2323", "#fd1a1b",
          "#fe5657", "#fd6b8b", "#ff548b", "#fd408b", "#df53a3",
          "#c46ac4"]
cmap = matplotlib.colors.ListedColormap(colors)
cmap.set_over('#c46ac4')
cmap.set_under('#18f6c3')
vmin = -10
vmax = 35

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
img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='upper', extent=img_extent, cmap=cmap)

# add a shapefile
shapefile = list(shpreader.Reader('BR_UF_2022.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.3)

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
plt.savefig('image_7.png')

# show the image
plt.show()