#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products (MTG) - Example 5: RGBs
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
import hdf5plugin                               # for reading compressed data, a decompression library is needed
import matplotlib.pyplot as plt                 # plotting library
import glob                                     # unix style pathname pattern expansion
import os                                       # miscellaneous operating system interfaces
import numpy as np                              # import the Numpy package
import cartopy, cartopy.crs as ccrs             # produce maps and other geospatial data analyses
import cartopy.io.shapereader as shpreader      # import shapefiles
import pyproj                                   # python interface to PROJ (cartographic projections and coordinate transformations library)
from pyresample import geometry                 # classes for describing different geographic areas using a mesh of points or pixels
import matplotlib.patheffects as PathEffects    # define classes for path effects
from matplotlib.offsetbox import AnchoredText   # adds an anchored text box in the corner
from matplotlib.offsetbox import OffsetImage    # change the image size (zoom)
from matplotlib.offsetbox import AnnotationBbox # creates an annotation using an OffsetBox
from satpy import Scene                         # scene object to hold satellite data

#-------------------------------------------------------------------------------------------------------------------

# initialise Scene
path_to_testdata = '../samples/mtg/RC0073/'
scn = Scene(filenames=glob.glob(os.path.join(path_to_testdata, '*BODY*.nc')), reader='fci_l1c_nc')

#-------------------------------------------------------------------------------------------------------------------

# image extent (min lon, min lat, max lon, max lat)
extent = [-55.0, -25.00, -26.00, 5.00] # Brazilian northeast

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

# load the datasets/composites of interest. note: the data inside the FCI files is stored upside down. The upper_right_corner='NE' argument flips it automatically in upright position.
scn.load(["airmass"], upper_right_corner='NE')

# resample the scene to a specified area
scn_resampled = scn.resample(area_def, resampler='nearest', radius_of_influence=5000)

# read the crs
crs = scn_resampled["airmass"].attrs['area'].to_cartopy_crs()

#-------------------------------------------------------------------------------------------------------------------

# plot size (width x height, in inches)
plt.figure(figsize=(8,7))

# define the projection and add coastlines and gridlnes
ax = plt.axes(projection=crs)

# add a shapefile
shapefile = list(shpreader.Reader('BR_UF_2022.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='gold',facecolor='none', linewidth=0.3)

# add coastlines, borders and gridlines
ax.coastlines(resolution='50m', color='turquoise', linewidth=1.0)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='cyan', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.15, xlocs=np.arange(-180, 180, 10), ylocs=np.arange(-90, 90, 10), draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xpadding = -5
gl.ypadding = -5
gl.ylabel_style = {'color': 'white', 'size': 6, 'weight': 'bold'}
gl.xlabel_style = {'color': 'white', 'size': 6, 'weight': 'bold'}

############################
# ADD A LOGO
############################

# add a logo to the plot
my_logo = plt.imread('../ancillary/eumetsat_logo.png')
imagebox = OffsetImage(my_logo, zoom = 0.2)
ab = AnnotationBbox(imagebox, (0.83, 0.95), xycoords="axes fraction", frameon = True, zorder=6)
ax.add_artist(ab)

############################
# ADD LABELS
############################

def add_label(lon, lat, marker, mcolor, msize, text, tcolor, tsize):
  # add a marker
  ax.plot(lon, lat, marker, color=mcolor, markersize=msize, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))
  # add a text
  txt = ax.text(lon + 0.4, lat + 0.1, text, fontsize=tsize, fontweight='bold', color=tcolor, transform=ccrs.Geodetic())
  # stylise the text
  txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='black')])

add_label(-44.3027, -2.5297, 'o', 'red', 5, "São Luis", 'gold', '8')
add_label(-42.8038, -5.0920, 'o', 'red', 5, "Teresina", 'gold', '8')
add_label(-38.5266, -3.7318, 'o', 'red', 5, "Fortaleza", 'gold', '8')
add_label(-35.2551, -5.8127, 'o', 'red', 5, "Natal", 'gold', '8')
add_label(-34.8630, -7.1150, 'o', 'red', 5, "João Pessoa", 'gold', '8')
add_label(-34.8811, -8.0538, 'o', 'red', 5, "Recife", 'gold', '8')
add_label(-35.7172, -9.6481, 'o', 'red', 5, "Maceió", 'gold', '8')
add_label(-37.0731, -10.9472, 'o', 'red', 5, "Aracaju", 'gold', '8')
add_label(-38.5014, -12.9722, 'o', 'red', 5, "Salvador", 'gold', '8')

# read the time and date
date = scn_resampled["airmass"].attrs['start_time']
date = date.strftime('%Y-%m-%d %H:%M UTC')

# add a title
plt.title(f'MTG-I1 FCI Simulated Test Data - True Color RGB\n{date}' , fontweight='bold', fontsize=10, loc='left')
plt.title('Space Week Nordeste 2023', fontsize=10, loc='right')

#-------------------------------------------------------------------------------------------------------------------

# show the image
from satpy.writers import get_enhanced_image
rgb = np.moveaxis(get_enhanced_image(scn_resampled["airmass"]).data.values, 0, -1)
im = plt.imshow(rgb, transform=crs, extent=crs.bounds, origin='upper')
plt.show()