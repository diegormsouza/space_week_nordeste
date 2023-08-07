#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products (MTG) - Example 6: Lightning Imager (LI) Data - Flash Area
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

#==================================================================================================================#
# REQUIRED MODULES
#==================================================================================================================#

import matplotlib.pyplot as plt                 # plotting library
import hdf5plugin                               # for reading compressed data, a decompression library is needed
import glob                                     # unix style pathname pattern expansion
import os                                       # miscellaneous operating system interfaces
import numpy as np                              # import the Numpy package
import cartopy, cartopy.crs as ccrs             # produce maps and other geospatial data analyses
import cartopy.feature as cfeature              # common drawing and filtering operations
import pyproj                                   # python interface to PROJ (cartographic projections and coordinate transformations library)
from pyresample import geometry                 # classes for describing different geographic areas using a mesh of points or pixels
from matplotlib.offsetbox import OffsetImage    # change the image size (zoom)
from matplotlib.offsetbox import AnnotationBbox # creates an annotation using an OffsetBox
from satpy import Scene                         # scene object to hold satellite data
from satpy.writers import get_enhanced_image    # get an enhanced version of dataset as an XRImage instance

#==================================================================================================================#
# CREATE A CUSTOM AREA
#==================================================================================================================#

# image extent (min lon, min lat, max lon, max lat)
extent = [3.0, 43.00, 17.00, 57.00] # Germany

# pyproj definitions
P = pyproj.Proj(proj='eqc', ellps='WGS84', preserve_units=True)
G = pyproj.Geod(ellps='WGS84')
x1,y1 = P(extent[1],extent[0])
x2,y2 = P(extent[3],extent[2])

# define km per degree
km_per_degree = 111.32

# calculate the total number of degrees in lat and lon extent
deg_lon = extent[2] - extent[0]
deg_lat = extent[3] - extent[1]

# calculate the number of pixels (width and height)
resolution = 2.0
width = (km_per_degree * deg_lon) /  resolution
height = (km_per_degree * deg_lat) /  resolution

# creating an area definition on the fly
area_id = 'my_area'
description = 'custom area'
proj_id = 'my_area'
x_size = int(width)
y_size = int(height)
area_extent = (y1,x1,y2,x2)
proj_dict = {'a': 6378169.0, 'b': 6378169.0,'units': 'm', 'lon_0': 0.0,'proj': 'eqc', 'lat_0': 0.0}
area_def = geometry.AreaDefinition(area_id, description, proj_id, proj_dict, x_size, y_size, area_extent)

#==================================================================================================================#
# DATA READING AND MANIPULATION
#==================================================================================================================#

# initialise Scene
path_to_testdata = '../samples/mtg/L2_run_flashes_201306201500_201306201501/'
scn = Scene(filenames=glob.glob(os.path.join(path_to_testdata, '*BODY*.nc')), reader='li_l2_nc', reader_kwargs={'with_area_definition': True})

# load the datasets/composites of interest.
scn.load(["flash_area"], upper_right_corner='NE')

# resample the scene to a specified area
scn_resampled = scn.resample(area_def)

#==================================================================================================================#
# PLOT THE IMAGE
#==================================================================================================================#

# plot size (width x height, in inches)
plt.figure(figsize=(8,8))

# define the projection and add coastlines and gridlnes
ax = plt.axes(projection=ccrs.PlateCarree())

# define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# add some map elements to the plot
ax.add_feature(cfeature.LAND, facecolor='dimgray')
ax.add_feature(cfeature.OCEAN, facecolor='black')

# add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='turquoise', linewidth=1.0)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.15, xlocs=np.arange(-180, 180, 5), ylocs=np.arange(-90, 90, 5), draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xpadding = -5
gl.ypadding = -5
gl.ylabel_style = {'color': 'white', 'size': 6, 'weight': 'bold'}
gl.xlabel_style = {'color': 'white', 'size': 6, 'weight': 'bold'}

# add a logo to the plot
my_logo = plt.imread('../ancillary/eumetsat_logo.png')
imagebox = OffsetImage(my_logo, zoom = 0.2)
ab = AnnotationBbox(imagebox, (0.85, 0.95), xycoords="axes fraction", frameon = True, zorder=6)
ax.add_artist(ab)

# read the time and date
date = scn_resampled["flash_area"].attrs['start_time']
date = date.strftime('%Y-%m-%d %H:%M UTC')

# add a title
plt.title(f'MTG-I1 LI Scientific Test Data - Flash Area\n{date}' , fontweight='bold', fontsize=10, loc='left')
plt.title('Space Week Nordeste 2023', fontsize=10, loc='right')

#==================================================================================================================#
# SHOW THE PLOT
#==================================================================================================================#

# show the image
from satpy.writers import get_enhanced_image
rgb = np.moveaxis(get_enhanced_image(scn_resampled["flash_area"]).data.values, 0, -1)
im = plt.imshow(rgb, extent=img_extent, origin='upper', interpolation='none')
plt.show()