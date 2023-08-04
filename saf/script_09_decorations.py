#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 9: Adding logo, labels and a scale bar
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
import geopandas as gp                                               # make working with geospatial data in python easier
import regionmask                                                    # create masks of geographical regions
import matplotlib.patheffects as PathEffects                         # define classes for path effects
from matplotlib.image import imread                                  # read an image from a file into an array
from matplotlib.offsetbox import AnchoredText                        # adds an anchored text box in the corner
from matplotlib.offsetbox import OffsetImage                         # change the image size (zoom)
from matplotlib.offsetbox import AnnotationBbox                      # creates an annotation using an OffsetBox
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar # draw a horizontal scale bar with a center-aligned label underneath
import matplotlib.font_manager as fm                                 # a module for finding, managing, and using fonts across platforms

#==================================================================================================================#
# DATA READING AND MANIPULATION
#==================================================================================================================#

# open the file using the NetCDF4 library
file = Dataset("../samples/NETCDF4_LSASAF_MSG_DLST-MAX10D_MSG-Disk_202307112345.nc")

# select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-50.0, -20.00, -31.00, 0.00] # Brazilian northeast

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
data = file.variables['LST_MAX'][ 0 , latui:latli , lonli:lonui ]

############################
# MASKING A REGION
############################

# reading lats and lons (regional)
lats = file.variables['lat'][latui:latli]
lons = file.variables['lon'][lonli:lonui]

# read the shapefile with Geopandas
regions = gp.read_file('regioes_2010.shp')
#display(regions)

# read the subregions from the shapefile
brazilian_regions = regionmask.from_geopandas(regions, names="sigla", abbrevs="nome", name="sigla")
#print(brazilian_regions)

# create the mask with a lat lon array
mask = brazilian_regions.mask(lons, lats)

# get the index for a given subregion
index = brazilian_regions.names.index("NE")

# mask the data for a given subregion
data = np.where(mask==index, data, np.nan)

# fill value also as nan
fillvalue = file.variables['LST_MAX']._FillValue
data[data==fillvalue] = np.nan

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
plt.figure(figsize=(7,7))

# use the PlateCarree projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# add some various map elements to the plot
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)

# define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]
ax.set_extent([extent[0], extent[2], extent[1], extent[3]], crs=ccrs.PlateCarree())

# Add a background map
#ax.stock_img()
fname = '../ancillary/Nasa_land_ocean_ice_8192.jpg'
ax.imshow(imread(fname), origin='upper', transform=ccrs.PlateCarree(), extent=[-180, 180, -90, 90])

# plot the image
img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='upper', extent=img_extent, cmap=cmap)

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
gl.ylabel_style = {'color': 'white', 'size': 6, 'weight': 'bold'}
gl.xlabel_style = {'color': 'white', 'size': 6, 'weight': 'bold'}

# add a colorbar
plt.colorbar(img, label='Land Surface Temperature - Maximum (°C) - 10 Day Composite', extend='both', orientation='vertical', pad=0.05, fraction=0.05)

# get the date
date_str  = file.getncattr('time_coverage_start')
date_format = '%Y-%m-%dT%H:%M:%SZ'
date_obj = datetime.strptime(date_str, date_format)
date = date_obj.strftime('%Y-%m-%d %H:%M:%S UTC')

# add a title
plt.title(f'MSG/SEVIRI -  LST - 10 Day Composite (Pixel-Wise Maximum)\n{date}', fontweight='bold', fontsize=10, loc='left')
plt.title('Space Week Nordeste 2023', fontsize=10, loc='right')

# add an achored text inside the plot
text = AnchoredText("INPE / CGCT / DISSM", loc='lower left', prop={'size': 10}, frameon=True)
ax.add_artist(text)

############################
# VISUALIZE A PIXEL VALUE
############################

# desired coordinates
lat_point = -10.0
lon_point = -40.0

# calculate the indexes
lat_idx = np.argmin(np.abs(lats - lat_point))
lon_idx = np.argmin(np.abs(lons - lon_point))

# extract only the data for the desired region
data_point = data[ lat_idx , lon_idx ].round(2)

# add a circle
ax.plot(lon_point, lat_point, 'o', color='lightgreen', markersize=5, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))

# add a text
txt_offset_x = 0.3
txt_offset_y = 0.3
text = "Lat: " + str(lat_point) + "\n" + "Lon: " + str(lon_point) + "\n" + "LST: \n" + str(data_point) + ' °C'
plt.annotate(text, xy=(lon_point + txt_offset_x, lat_point + txt_offset_y), xycoords=ccrs.PlateCarree()._as_mpl_transform(ax), fontsize=10, fontweight='bold', color='gold', bbox=dict(boxstyle="round",fc=(0.0, 0.0, 0.0, 0.5), ec=(1., 1., 1.)), alpha = 1.0)

############################
# ADD A LOGO
############################

# add a logo to the plot
my_logo = plt.imread('../ancillary/lsa_saf_logo.png')
imagebox = OffsetImage(my_logo, zoom = 0.3)
ab = AnnotationBbox(imagebox, (0.86, 0.92), xycoords="axes fraction", frameon = True, zorder=6)
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

############################
# ADD SCALE BAR
############################

# add a scalebar
fontprops = fm.FontProperties(size=7)
distance = 500
scalebar = AnchoredSizeBar(ax.transData, (distance / 111), str(distance) + ' km', loc='lower right', pad=0.25, color='black',
                           frameon=True, label_top=True, sep=4, size_vertical=0.2, fontproperties=fontprops)
ax.add_artist(scalebar)

# plot the N arrow
buffer = [PathEffects.withStroke(linewidth=5, foreground="w")]
t1 = ax.text(0.87, 0.05, u'\u25B2\nN', transform=ax.transAxes, horizontalalignment='center', verticalalignment='bottom', path_effects=buffer)

#==================================================================================================================#
# SAVE AND VISUALIZE THE PLOT
#==================================================================================================================#

# save the image
plt.savefig('image_9.png')

# show the image
plt.show()