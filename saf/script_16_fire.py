#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 16: Fire Radiative Power Pixel (MSG)
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
from matplotlib.image import imread                                  # read an image from a file into an array
from matplotlib.offsetbox import AnchoredText                        # adds an anchored text box in the corner
from matplotlib.offsetbox import OffsetImage                         # change the image size (zoom)
from matplotlib.offsetbox import AnnotationBbox                      # creates an annotation using an OffsetBox
from cartopy.feature.nightshade import Nightshade                    # draws a polygon where there is no sunlight for the given datetime

#==================================================================================================================#
# DATA READING AND MANIPULATION
#==================================================================================================================#

# open the file using the NetCDF4 library
file = Dataset("../samples/HDF5_LSASAF_MSG_FRP-PIXEL-ListProduct_MSG-Disk_202307251500")

# read the latitudes
lats = file.variables['LATITUDE'][:] / 100

# read the longitudes
lons = file.variables['LONGITUDE'][:] / 100

# read the data
data = file.variables['FRP'][:] / 10

#==================================================================================================================#
# CREATE A CUSTOM COLOR SCALE
#==================================================================================================================#

# create a custom color scale:
# reference: https://landsaf.ipma.pt/en/
colors = ["#044dfe", "#d1e3f2", "#ffed03", "#ff9e02", "#b21e1c", "#fe3002"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list('my_palette', colors, N=256)

#==================================================================================================================#
# CREATE THE PLOT
#==================================================================================================================#

# choose the plot size (width x height, in inches)
plt.figure(figsize=(8,9))

# use the Plate Carree projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-50.0, -20.00, -31.00, 0.00] # Brazilian northeast
ax.set_extent([extent[0], extent[2], extent[1], extent[3]], crs=ccrs.PlateCarree())

# get the date
date_str  = file.getncattr('SENSING_START_TIME')
date_format = '%Y%m%d%H%M%S'
date_obj = datetime.strptime(date_str, date_format)
date = date_obj.strftime('%Y-%m-%d %H:%M:%S UTC')

# add a background map and night shade
fname = '../ancillary/Nasa_land_ocean_ice_8192.jpg'
ax.imshow(imread(fname), origin='upper', transform=ccrs.PlateCarree(), extent=[-180, 180, -90, 90], zorder=1)
ax.add_feature(Nightshade(date_obj, alpha=0.5))

# normalize bound values
bounds = [0, 30, 40, 60, 80, 120, 500]
norm = matplotlib.colors.BoundaryNorm(bounds, ncolors=256)

# plot the image
img = ax.scatter(lons, lats, c=data, s=60, norm=norm, cmap=cmap, transform=ccrs.PlateCarree())

# add a shapefile
shapefile = list(shpreader.Reader('BR_UF_2022.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='white',facecolor='none', linewidth=0.3)

# add coastlines, borders and gridlines
ax.coastlines(resolution='50m', color='white', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 181, 5), ylocs=np.arange(-90, 91, 5), draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xpadding = -5
gl.ypadding = -5
gl.ylabel_style = {'color': 'gray', 'weight': 'bold'}
gl.xlabel_style = {'color': 'gray', 'weight': 'bold'}

# Add a colorbar
cb = plt.colorbar(img, label='Fire Radiative Power [MW]', extend='neither', orientation='vertical', pad=0.03, fraction=0.05)
ticks = [0, 30, 40, 60, 80, 120, 500]
cb.set_ticks(ticks)

# add a title
plt.title(f'MSG/SEVIRI Fire Radiative Power Pixel\n{date}', fontweight='bold', fontsize=10, loc='left')
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
plt.savefig('image_16.png')

# show the image
plt.show()