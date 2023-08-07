#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products (MTG) - Example 4: Custom Area
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
import hdf5plugin                               # for reading compressed data, a decompression library is needed
import matplotlib.pyplot as plt                 # plotting library
import glob                                     # unix style pathname pattern expansion
import os                                       # miscellaneous operating system interfaces
import numpy as np                              # import the Numpy package
import cartopy, cartopy.crs as ccrs             # produce maps and other geospatial data analyses
import cartopy.feature as cfeature              # common drawing and filtering operations
import cartopy.io.shapereader as shpreader      # import shapefiles
import pyproj                                   # python interface to PROJ (cartographic projections and coordinate transformations library)
from pyresample import geometry                 # classes for describing different geographic areas using a mesh of points or pixels
from satpy import Scene                         # scene object to hold satellite data

#-------------------------------------------------------------------------------------------------------------------

# initialise Scene
path_to_testdata = '../samples/mtg/RC0073/'
scn = Scene(filenames=glob.glob(os.path.join(path_to_testdata, '*BODY*.nc')), reader='fci_l1c_nc')

# load the datasets/composites of interest. note: the data inside the FCI files is stored upside down. The upper_right_corner='NE' argument flips it automatically in upright position.
scn.load(['ir_105'], upper_right_corner='NE')

#-------------------------------------------------------------------------------------------------------------------

# image extent (min lon, min lat, max lon, max lat)
#extent = [-70.0, -40.0, 30.0, 30.0] # Brazil and Africa
extent = [-75.0, -37.00, -33.00, 8.00] # Brazil

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
resolution = 4.0
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

#-------------------------------------------------------------------------------------------------------------------

# resample the scene to a specified area
scn_resampled = scn.resample(area_def)

# plot size (width x height, in inches)
plt.figure(figsize=(8,7))

# define the projection
ax = plt.axes(projection=ccrs.PlateCarree())

# add some various map elements to the plot
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)

# define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# show the image
img = ax.imshow(scn_resampled["ir_105"], extent=img_extent, vmin=180, vmax=320, origin='upper', cmap='jet')

# add a shapefile
shapefile = list(shpreader.Reader('BR_UF_2022.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.3)

# add coastlines and gridlnes
ax.coastlines(resolution='110m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 181, 10), ylocs=np.arange(-90, 91, 10), draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xpadding = -5
gl.ypadding = -5

# add a colorbar
plt.colorbar(img, label='Brightness Temperature (K)', extend='both', orientation='vertical', pad=0.03, fraction=0.05)

# read the time and date
date = scn["ir_105"].attrs['start_time']
date = date.strftime('%Y-%m-%d %H:%M UTC')

# add a title
plt.title(f'MTG-I1 FCI Simulated Test Data\n{date}' , fontweight='bold', fontsize=10, loc='left')
plt.title('Space Week Nordeste 2023', fontsize=10, loc='right')

# show the image
plt.show()