#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 25: Total Downward Surface Shortwave Flux (MSG)
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
file = Dataset("../samples/NETCDF4_LSASAF_MSG_DIDSSF_MSG-Disk_202307260000.nc")

# select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-75.0, -37.00, -33.00, 8.00] # Brazil

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
data = file.variables['DSSF'][ 0 , latui:latli , lonli:lonui ]
data = data / 10000000

#==================================================================================================================#
# CREATE A CUSTOM COLOR SCALE
#==================================================================================================================#

# reference: https://landsaf.ipma.pt/media/filer_public_thumbnails/filer_public/2b/3c/2b3cf2c2-7036-4f37-8a09-12d802236588/thumbnail_didssf.png__1170x0_q55_subsampling-2.png
# HEX values got from: https://imagecolorpicker.com/:
colors = ["#010044", "#001856", "#0f2187", "#0f30b1", "#0d62bc", "#2183e8",
          "#4ba7fc", "#94d3ff", "#e5fdff", "#fce875", "#ffbd33", "#ff9d02", "#ff5d00",
          "#e72000", "#d20e02", "#b7270c", "#971515", "#860000", "#6b014b", "#500059"]
cmap = matplotlib.colors.ListedColormap(colors)
cmap.set_over('#500059')
cmap.set_under('#010044')
vmin = 0
vmax = 5.4

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
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# plot the image
img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='upper', extent=img_extent, cmap=cmap)

# add a shapefile
shapefile = list(shpreader.Reader('BR_UF_2022.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.3)

# add coastlines, borders and gridlines
ax.coastlines(resolution='50m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 181, 5), ylocs=np.arange(-90, 91, 5), draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xpadding = -5
gl.ypadding = -5

# add a colorbar
plt.colorbar(img, label='Daily Downward Surface Shortwave Flux (Jm\u207B²) 1e7', extend='both', orientation='vertical', pad=0.03, fraction=0.05)

# get the date
date_str = file.getncattr('image_reference_time')
date_format = '%Y-%m-%dT%H:%M:%SZ'
date_obj = datetime.strptime(date_str, date_format)
date = date_obj.strftime('%Y-%m-%d')

# add a title
plt.title(f'MSG/SEVIRI - Daily Downward Surface Shortwave Flux\n{date}', fontweight='bold', fontsize=10, loc='left')
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
ab = AnnotationBbox(imagebox, (0.84, 0.92), xycoords="axes fraction", frameon = True, zorder=6)
ax.add_artist(ab)

#==================================================================================================================#
# SAVE AND VISUALIZE THE PLOT
#==================================================================================================================#

# save the image
plt.savefig('image_25.png')

# show the image
plt.show()