#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 18: Daily LST retrieval (Metop)
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

#==================================================================================================================#
# REQUIRED MODULES
#==================================================================================================================#

from netCDF4 import Dataset                                          # read / write NetCDF4 files
import matplotlib.pyplot as plt                                      # plotting library
from datetime import datetime                                        # basic date and time types
import cartopy, cartopy.crs as ccrs                                  # produce maps and other geospatial data analyses
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
file_name = "h64_20230725_0000_24_hea.nc"
file = Dataset(f'../samples/{file_name}')

# select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-60.0, -20.00, -10.00, 20.00] # Brazilian northeast + atlantic

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
data = file.variables['acc_rr'][ latli:latui , lonli:lonui ]

#==================================================================================================================#
# CREATE A CUSTOM COLOR SCALE
#==================================================================================================================#

# create a custom color scale:
# reference: https://disc.gsfc.nasa.gov/datasets/TRMM_3B42_Daily_7/summary
# HEX values got from: https://imagecolorpicker.com/:
colors = ["#b9d3f1", "#1751bb", "#80e7cd", "#49bd75", "#3d9942",
        "#fdf850", "#fed919", "#fb7c07", "#d34800", "#a71d00",
        "#9a3273"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
cmap.set_under('#b9d3f1')
cmap.set_over('#9a3273')
vmin = 0
vmax = 100

#==================================================================================================================#
# CREATE THE PLOT
#==================================================================================================================#

# choose the plot size (width x height, in inches)
plt.figure(figsize=(8,7))

# use the PlateCarree projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# plot the image
img = ax.imshow(data, vmin=vmin, vmax=vmax, interpolation='bilinear', origin='lower', extent=img_extent, cmap=cmap)

# add a shapefile
shapefile = list(shpreader.Reader('BR_UF_2022.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.3)

# add coastlines, borders and gridlines
ax.coastlines(resolution='50m', color='black', linewidth=1.5)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=1.0)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 10), ylocs=np.arange(-90, 90, 10), draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xpadding = -5
gl.ypadding = -5

# add a colorbar
plt.colorbar(img, label='24h Precipitation (mm)', extend='both', orientation='horizontal', pad=0.03, fraction=0.05)

# get the date from the file name
date_str = (file_name[file_name.find("h64_")+4:file_name.find("_0000")])
date_format = '%Y%m%d'
date = datetime.strptime(date_str, date_format)
date = date.strftime('%Y-%m-%d')

# add a title
plt.title(f'Multimission - Gridded 24h Accumulated Precipitation\n{date}', fontweight='bold', fontsize=10, loc='left')
plt.title('Space Week Nordeste 2023', fontsize=10, loc='right')

# add an achored text inside the plot
text = AnchoredText("INPE / CGCT / DISSM", loc='lower left', prop={'size': 10}, frameon=True)
ax.add_artist(text)

############################
# ADD A LOGO
############################

# add a logo to the plot
my_logo = plt.imread('../ancillary/h_saf_logo.png')
imagebox = OffsetImage(my_logo, zoom = 0.5)
ab = AnnotationBbox(imagebox, (0.83, 0.13), xycoords="axes fraction", frameon = True, zorder=10)
ax.add_artist(ab)

#==================================================================================================================#
# SAVE AND VISUALIZE THE PLOT
#==================================================================================================================#

# save the image
plt.savefig('image_18.png')

# show the image
plt.show()