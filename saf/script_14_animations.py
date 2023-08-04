#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 14: NDVI (Creating animations)
# Author: Diego Souza (INPE/CGCT/DISSM)
# Note: It is necessary to run script 13 before
#-------------------------------------------------------------------------------------------------------------------

#==================================================================================================================#
# REQUIRED MODULES
#==================================================================================================================#

from netCDF4 import Dataset                                          # read / write NetCDF4 files
import matplotlib.pyplot as plt                                      # plotting library
from datetime import datetime, timedelta                             # basic date and time types
import cartopy, cartopy.crs as ccrs                                  # produce maps and other geospatial data analyses
import cartopy.feature as cfeature                                   # common drawing and filtering operations
import cartopy.io.shapereader as shpreader                           # import shapefiles
import numpy as np                                                   # import the Numpy package
import matplotlib                                                    # comprehensive library for creating visualizations in Python
from matplotlib.offsetbox import AnchoredText                        # adds an anchored text box in the corner
from matplotlib.offsetbox import OffsetImage                         # change the image size (zoom)
from matplotlib.offsetbox import AnnotationBbox                      # creates an annotation using an OffsetBox
import glob                                                          # unix style pathname pattern expansion
import os                                                            # miscellaneous operating system interfaces

#-------------------------------------------------------------------------------------------------------------------

# local directory
local_dir = "samples_script_13"; os.makedirs(local_dir, exist_ok=True)
files = sorted(glob.glob(f'{local_dir}/METOP_AVHRR_*_S10_AMs_NDV.img'), key=os.path.getmtime)
print("\n".join(files))

#==================================================================================================================#
# DATA READING AND MANIPULATION
#==================================================================================================================#

for file in files:

  print(f'Processing file: {file}')

  # 1. open the image file ("flat binary" format)
  file_name = file.rsplit('/', 1)[-1]
  data = np.fromfile(file,dtype='uint8')

  # 2. basic information from manual
  nrow = 9072
  ncol = 6720
  min_lon = -93.0
  min_lat = -56.0
  max_lon = -33.0
  max_lat =  25.0
  res = (max_lon - min_lon) / ncol
  fill_value = 255

  # 3. geographic grid
  lats = np.arange(min_lat+(res/2), max_lat-(res/2), res)
  lons = np.arange(min_lon+(res/2), max_lon-(res/2), res)

  # 4. convert to 2D array
  data.shape=(nrow, ncol)

  # 5. convert to float64 datatype
  data = np.float64(data)

  # 6. mask out the missing value
  data[data > 250] = np.nan

  # 7. apply scale and offset
  data = - 0.08 + 0.004 * data

  ############################
  # DATA QUALITY FLAGS
  ############################

  # 8. open the data flag file
  data_flag = np.fromfile(file.replace("NDV", "STM"),dtype='uint8')

  # 9. convert to 2D array
  data_flag.shape=(nrow, ncol)

  # 10. get specific bit from byte array (clouds)
  data_flag = (data_flag >> 1) & 1

  # 12. apply the flag
  data[data_flag == 1] = np.nan

  ############################
  # READ ONLY A REGION
  ############################

  # select the extent [min. lon, min. lat, max. lon, max. lat]
  #extent = [-75.0, -37.00, -33.00, 8.00] # Brazil
  extent = [-50.0, -20.00, -33.00, 0.00] # Brazilian northeast

  # latitude lower and upper index
  latli = np.argmin( np.abs( lats - extent[1] ) )
  latui = np.argmin( np.abs( lats - extent[3] ) )

  # longitude lower and upper index
  lonli = np.argmin( np.abs( lons - extent[0] ) )
  lonui = np.argmin( np.abs( lons - extent[2] ) )

  # extract the data
  data = np.flipud(data)
  data = data[ latli:latui , lonli:lonui ]

  #==================================================================================================================#
  # CREATE A CUSTOM COLOR SCALE
  #==================================================================================================================#

  # NDVI colormap creation
  colors = ["#653700","yellow","limegreen","green"]
  cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
  cmap.set_over('green')
  cmap.set_under('#653700')
  vmin = 0.1
  vmax = 0.8

  #==================================================================================================================#
  # CREATE THE PLOT
  #==================================================================================================================#

  # choose the plot size (width x height, in inches)
  plt.figure(figsize=(10,10))

  # use the PlateCarree projection in cartopy
  ax = plt.axes(projection=ccrs.PlateCarree())

  # add some various map elements to the plot
  ax.add_feature(cfeature.LAND, facecolor='lightgray')
  ax.add_feature(cfeature.OCEAN, facecolor='dimgray')
  ax.add_feature(cfeature.RIVERS, edgecolor='blue')

  # define the image extent
  img_extent = [extent[0], extent[2], extent[1], extent[3]]

  # plot the image
  img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='lower', extent=img_extent, cmap=cmap)

  # add a shapefile
  shapefile = list(shpreader.Reader('BR_UF_2022.shp').geometries())
  ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.5)

  # add coastlines, borders and gridlines
  ax.coastlines(resolution='50m', color='black', linewidth=0.8)
  ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
  gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 181, 5), ylocs=np.arange(-90, 91, 5), draw_labels=True)
  gl.top_labels = False
  gl.right_labels = False
  gl.xpadding = -5
  gl.ypadding = -5

  # add a colorbar
  plt.colorbar(img, label='NDVI', extend='both', orientation='vertical', pad=0.03, fraction=0.05)

  # get start the date from the file name
  date_str = (file_name[file_name.find("AVHRR_")+6:file_name.find("_S10")])
  date_format = '%Y%m%d'
  date_start = datetime.strptime(date_str, date_format)
  date_start_str = date_start.strftime('%Y-%m-%d')

  # calculate the end date (+10 days)
  date_end = date_start + timedelta(days=10)
  date_end_str = date_end.strftime('%Y-%m-%d')

  # add a title
  plt.title(f'METOP/AVHRR - NDVI - 10-Daily Synthesis\n{date_start_str} - {date_end_str}', fontweight='bold', fontsize=10, loc='left')
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
  plt.savefig(f'{local_dir}/NDVI_{date_start_str}.png', bbox_inches='tight', pad_inches=0, dpi=300)

  # show the image 
  #plt.gcf().set_dpi(300)
  #plt.show()


#==================================================================================================================#
# CREATING THE ANIMATION
#==================================================================================================================#

import imageio.v2 as imageio # python interface to read and write a wide range of image data
import glob                  # unix style pathname pattern expansion
import os                    # miscellaneous operating system interfaces

# images we want to include in the GIF
files = sorted(glob.glob(f'{local_dir}/NDVI_*.png'), key=os.path.getmtime)

# create the GIF
images = []
for file in files:
    images.append(imageio.imread(file))
imageio.mimsave(f'{local_dir}/animation.gif', images, duration=1000)