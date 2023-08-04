#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 11: Daily LST retrieval (Metop)
# Author: Diego Souza (INPE/CGCT/DISSM)
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

#==================================================================================================================#
# DATA READING AND MANIPULATION
#==================================================================================================================#

# open the file using the NetCDF4 library
file = Dataset("../samples/NETCDF4_LSASAF_M01-AVHR_EDLST-DAY_GLOBE_202307220000.nc")

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
data = file.variables['LST-day'][ 0 , latli:latui , lonli:lonui ]

#==================================================================================================================#
# CREATE A CUSTOM COLOR SCALE
#==================================================================================================================#

# reference color scale from EUMETSAT: https://twitter.com/LSA_SAF/status/1493929742604673027
# HEX values got from: https://imagecolorpicker.com/:
colors = ["#18f6c3", "#19f6db", "#1adddf", "#2edcff", "#6edbf9",
          "#a1eaff", "#cce9ff", "#bdbede", "#a4a6d5", "#8b8cc2",
          "#8a6cc0", "#a36be0", "#8754c4", "#6b40a5", "#5222a6",
          "#4018a8", "#21198b", "#1a2f89", "#1856a0", "#1987c5",
          "#1990e0", "#1ac4ff", "#2eddff", "#6edbf9", "#cce9ff",
          "#ffffbf", "#ffff8d", "#ffff31", "#ffff31", "#ffc024",
          "#ffa130", "#ff6a3e", "#fd3d30", "#fe2323", "#fd1a1b",
          "#fe5657", "#fd6b8b", "#ff548b", "#fd408b", "#df53a3",
          "#c46ac4"]
cmap = matplotlib.colors.ListedColormap(colors)
cmap.set_over('#c46ac4')
cmap.set_under('#18f6c3')
vmin = -10
vmax = 35

#==================================================================================================================#
# CREATE THE PLOT
#==================================================================================================================#

# choose the plot size (width x height, in inches)
plt.figure(figsize=(8,9))

# use the PlateCarree projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# add some various map elements to the plot
ax.add_feature(cfeature.LAND)
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
plt.colorbar(img, label='Land Surface Temperature (°C) - Day', extend='both', orientation='vertical', pad=0.03, fraction=0.05)

# get the date
date_str = file.getncattr('image_reference_time')
date_format = '%Y-%m-%dT%H:%M:%SZ'
date_obj = datetime.strptime(date_str, date_format)
date = date_obj.strftime('%Y-%m-%d')

# get the platform
platform = file.getncattr('platform')
if platform == 'M01':
  platform = 'B'
elif platform == 'M02':
  platform = 'C'

# add a title
plt.title(f'Metop-{platform}/AVHRR - Daily Land Surface Temperature (Daytime)\n{date}', fontweight='bold', fontsize=10, loc='left')
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
# PLOT THE AQUISITION TIME
#==================================================================================================================#

# get the reference time and create a date object
date_str  = file.getncattr('image_reference_time')
date_format = '%Y-%m-%dT%H:%M:%SZ'
date_obj = datetime.strptime(date_str, date_format)

# get the aquisition time (minutes)
aquisition_time = file.variables['aquisition_time-day'][ 0 , latli:latui , lonli:lonui ]

# get the aqcuisition time fill value
fill_value = file.variables['aquisition_time-day']._FillValue

# reading lats and lons and creating 2d arrays
lats = file.variables['lat'][latli:latui]
lons = file.variables['lon'][lonli:lonui]
lons, lats = np.meshgrid(lons, lats)

# get a sub sample of the aquisition time, lats and lons
int_x = 600
int_y = 2000
aquisition_time = aquisition_time[::int_x,::int_y]
lons_text = lons[::int_x,::int_y]
lats_text = lats[::int_x,::int_y]

# plot the aquisition time over the image
for (j,i),atime in np.ndenumerate(aquisition_time):
    if (atime != fill_value):
      adate = date_obj + timedelta(minutes=int(atime))
      fdate = adate.strftime('%H:%M')
      plt.annotate(fdate, xy=(lons_text[j][i], lats_text[j][i]), xycoords=ccrs.PlateCarree()._as_mpl_transform(ax), fontsize=8, fontweight='bold',
                   color='white', bbox=dict(boxstyle="round",fc=(0.0, 0.0, 0.0, 0.5), ec=(1., 1., 1.)), alpha = 1.0, clip_on=True)

#==================================================================================================================#
# SAVE AND VISUALIZE THE PLOT
#==================================================================================================================#

# save the image
plt.savefig('image_11.png', bbox_inches='tight', pad_inches=0, dpi=300)

# show the image
plt.show()