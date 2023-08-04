#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 17: Root Zone Soil Moisture Profile Index (Metop/ASCAT)
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

#==================================================================================================================#
# REQUIRED MODULES
#==================================================================================================================#

from netCDF4 import Dataset                                          # read / write NetCDF4 files
import matplotlib.pyplot as plt                                      # plotting library
from datetime import datetime                                        # basic date and time types
import cartopy, cartopy.crs as ccrs                                  # produce maps and other geospatial data analyses
import cartopy.feature as cfeature                                   # common drawing and filtering operations
import cartopy.io.shapereader as shpreader                           # import shapefiles
import numpy as np                                                   # import the Numpy package
import matplotlib                                                    # comprehensive library for creating visualizations in Python
from matplotlib.offsetbox import AnchoredText                        # adds an anchored text box in the corner
from matplotlib.offsetbox import OffsetImage                         # change the image size (zoom)
from matplotlib.offsetbox import AnnotationBbox                      # creates an annotation using an OffsetBox

#==================================================================================================================#
# DATA READING AND MANIPULATION
#==================================================================================================================#

# open the file using the NetCDF4 library
file_name = "h26_2023072500_R01.nc"
file = Dataset(f'../samples/{file_name}')

# select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-80.0 + 360, -45.00, -30.00 + 360, 10.00]

# reading lats and lons (whole image)
lats = file.variables['lat'][:]
lons = file.variables['lon'][:]

# latitude lower and upper index
latli = np.argmin( np.abs( lats - extent[1] ) )
latui = np.argmin( np.abs( lats - extent[3] ) )

# longitude lower and upper index
lonli = np.argmin( np.abs( lons - extent[0] ) )
lonui = np.argmin( np.abs( lons - extent[2] ) )

# extract the data (based on the indexes)
data = file.variables['var42'][0, latui:latli , lonli:lonui ]

#==================================================================================================================#
# CREATE A CUSTOM COLOR SCALE
#==================================================================================================================#

# create a custom color scale:
# reference: https://hsaf.meteoam.it/Products/ProductsList?type=soil_moisture
# HEX values got from: https://imagecolorpicker.com/:
colors = ["#a68138", "#e5be5e", "#d2dc77", "#a8ef92", "#58efce",
          "#22cced", "#0785f0", "#1239d3", "#1e01b2", "#091f88"]

cmap = matplotlib.colors.ListedColormap(colors)
cmap.set_over('#c46ac4')
cmap.set_under('#18f6c3')
vmin = 0
vmax = 1

#==================================================================================================================#
# CREATE THE PLOT
#==================================================================================================================#

# choose the plot size (width x height, in inches)
plt.figure(figsize=(8,9))

# use the PlateCarree projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# add some various map elements to the plot
ax.add_feature(cfeature.LAND, facecolor='white')
ax.add_feature(cfeature.OCEAN, facecolor='dimgray')

# define the image extent
img_extent = [extent[0] - 360, extent[2] - 360, extent[1], extent[3]]

# plot the image
img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='upper', extent=img_extent, cmap=cmap)

# add a shapefile
shapefile = list(shpreader.Reader('BR_UF_2022.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='white',facecolor='none', linewidth=0.3)

# add coastlines, borders and gridlines
ax.coastlines(resolution='50m', color='white', linewidth=1.5)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=1.0)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 10), ylocs=np.arange(-90, 90, 10), draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xpadding = -5
gl.ypadding = -5

# define the ticks to be shown
ticks = [0.0 , 0.1 , 0.2 , 0.3 , 0.4 , 0.5 , 0.6 , 0.7 , 0.8 , 0.9, 1.0]

# add a colorbar
plt.colorbar(img, label='Root Zone Soil Moisture (%)', extend='neither', orientation='vertical', pad=0.03, fraction=0.05, ticks=ticks)

# get the date from the file name
date_str = (file_name[file_name.find("h26_")+4:file_name.find("_R01")])
date_format = '%Y%m%d%H%M'
date = datetime.strptime(date_str, date_format)
date = date.strftime('%Y-%m-%d')

# add a title
plt.title(f'Metop/ASCAT NRT Root Zone Soil Moisture Profile Index\n{date}', fontweight='bold', fontsize=10, loc='left')
plt.title('Space Week Nordeste 2023', fontsize=10, loc='right')

# add an achored text inside the plot
text = AnchoredText("INPE / CGCT / DISSM", loc='lower left', prop={'size': 10}, frameon=True)
ax.add_artist(text)

############################
# ADD A LOGO
############################

# add a logo to the plot
my_logo = plt.imread('../ancillary/lsa_saf_logo.png')
imagebox = OffsetImage(my_logo, zoom = 0.5)
ab = AnnotationBbox(imagebox, (0.83, 0.92), xycoords="axes fraction", frameon = True, zorder=6)
ax.add_artist(ab)

#==================================================================================================================#
# SAVE AND VISUALIZE THE PLOT
#==================================================================================================================#

# save the image
plt.savefig('image_17.png')

# show the image
plt.show()