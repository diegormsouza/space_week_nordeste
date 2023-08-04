#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 20: 10-day Fraction of Absorved Photosynthetic Active Radiation
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
file = Dataset("../samples/NETCDF4_LSASAF_M01-AVHR_ETFAPAR_GLOBE_202307250000.nc")

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
data = file.variables['FAPAR'][ 0 , latli:latui , lonli:lonui ]

#==================================================================================================================#
# CREATE A CUSTOM COLOR SCALE
#==================================================================================================================#

# reference: https://navigator.eumetsat.int/preview/HDF5_LSASAF_MSG_FAPAR-D10_MSG-Disk.png
# HEX values got from: https://imagecolorpicker.com/:
colors = ["#ce6800", "#d3840f", "#d49618", "#e0ad1b", "#eec00f",
          "#ffd700", "#fce300", "#fff400", "#f4f905", "#c9e41b",
          "#a3d02b", "#8bcd23", "#75ca0f", "#56c100", "#35a600",
          "#008002", "#00801d", "#008052", "#00817e"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
cmap.set_over('#00817e')
cmap.set_under('#ce6800')
vmin = 0
vmax = 0.9

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
img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='lower', extent=img_extent, cmap=cmap)

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
plt.colorbar(img, label='10-day Fraction of Absorved Photosynthetic Active Radiation', extend='both', orientation='vertical', pad=0.03, fraction=0.05)

# get the date
date_str = file.getncattr('image_reference_time')
date_format = '%Y-%m-%dT%H:%M:%SZ'
date_obj = datetime.strptime(date_str, date_format)
date = date_obj.strftime('%Y-%m-%d')

# add a title
plt.title(f'Metop/AVHRR - 10-day Fraction of Absorved Photosynthetic Active Radiation\n{date}', fontweight='bold', fontsize=10, loc='left')
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
plt.savefig('image_20.png', bbox_inches='tight', pad_inches=0, dpi=300)

# show the image
plt.show()