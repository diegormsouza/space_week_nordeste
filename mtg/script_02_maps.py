#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products (MTG) - Example 2: Reading the CRS and Adding Maps with Cartopy
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
import hdf5plugin                               # for reading compressed data, a decompression library is needed
import matplotlib.pyplot as plt                 # plotting library
import glob                                     # unix style pathname pattern expansion
import os                                       # miscellaneous operating system interfaces
import numpy as np                              # import the Numpy package
import cartopy, cartopy.crs as ccrs             # produce maps and other geospatial data analyses
from satpy import Scene                         # scene object to hold satellite data

#-------------------------------------------------------------------------------------------------------------------

# initialise Scene
path_to_testdata = '../samples/mtg/RC0073/'
scn = Scene(filenames=glob.glob(os.path.join(path_to_testdata, '*BODY*.nc')), reader='fci_l1c_nc')

# load the datasets/composites of interest. note: the data inside the FCI files is stored upside down. The upper_right_corner='NE' argument flips it automatically in upright position.
scn.load(['ir_105'], upper_right_corner='NE')

# read the crs
crs = scn["ir_105"].attrs['area'].to_cartopy_crs()

#-------------------------------------------------------------------------------------------------------------------

# plot size (width x height, in inches)
plt.figure(figsize=(8,8))

# define the projection
ax = plt.axes(projection=crs)

# plot the image
plt.imshow(scn["ir_105"], transform=crs, extent=crs.bounds, vmin=180, vmax=320, origin='upper', cmap='jet')

# add coastlines and gridlnes
ax.coastlines(resolution='110m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 181, 10), ylocs=np.arange(-90, 91, 10), draw_labels=False)

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