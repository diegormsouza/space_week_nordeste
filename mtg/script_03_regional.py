#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products (MTG) - Example 3: Regional Plots
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
from satpy import Scene                         # scene object to hold satellite data

#-------------------------------------------------------------------------------------------------------------------

# initialise Scene
path_to_testdata = '../samples/mtg/RC0073/'
scn = Scene(filenames=glob.glob(os.path.join(path_to_testdata, '*BODY*.nc')), reader='fci_l1c_nc')

# load the datasets/composites of interest. note: the data inside the FCI files is stored upside down. The upper_right_corner='NE' argument flips it automatically in upright position.
scn.load(['ir_105'], upper_right_corner='NE')

# resample the scene to a specified area (e.g. "eurol1" for Europe in 1km resolution)
scn_resampled = scn.resample("south_america", resampler='nearest', radius_of_influence=5000)

# read the crs
crs = scn_resampled["ir_105"].attrs['area'].to_cartopy_crs()

#-------------------------------------------------------------------------------------------------------------------

# plot size (width x height, in inches)
plt.figure(figsize=(8,7))

# define the projection
ax = plt.axes(projection=crs)

# show the image
plt.imshow(scn_resampled["ir_105"], extent=crs.bounds, vmin=180, vmax=320, origin='upper', cmap='jet')

# add some various map elements to the plot
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)

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
cbar = plt.colorbar(label='Brightness Temperature (K)', extend='both', orientation='horizontal', pad=0.03, fraction=0.05)

# read the time and date
date = scn["ir_105"].attrs['start_time']
date = date.strftime('%Y-%m-%d %H:%M UTC')

# add a title
plt.title(f'MTG-I1 FCI Simulated Test Data\n{date}' , fontweight='bold', fontsize=10, loc='left')
plt.title('Space Week Nordeste 2023', fontsize=10, loc='right')

# show the image
plt.show()