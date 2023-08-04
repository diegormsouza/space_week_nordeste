#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 15: NDVI (Time Series)
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

#==================================================================================================================#
# REQUIRED MODULES
#==================================================================================================================#

from netCDF4 import Dataset                                          # read / write NetCDF4 files
import matplotlib.pyplot as plt                                      # plotting library
from datetime import datetime, timedelta                             # basic date and time types
import numpy as np                                                   # import the Numpy package
import os                                                            # miscellaneous operating system interfaces
import glob                                                          # unix style pathname pattern expansion

#-------------------------------------------------------------------------------------------------------------------

# local directory
local_dir = "samples_script_13"; os.makedirs(local_dir, exist_ok=True)
files = sorted(glob.glob(f'{local_dir}/METOP_AVHRR_*_S10_AMs_NDV.img'), key=os.path.getmtime)
print("\n".join(files))

#-------------------------------------------------------------------------------------------------------------------

# Create the lists that will store our data
ndvi = []; dates = []

for file in files:

  #==================================================================================================================#
  # DATA READING AND MANIPULATION
  #==================================================================================================================#

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
  # EXTRACTING PIXEL VALUES
  #==================================================================================================================#

  # reading lats and lons
  lats = lats[latli:latui]
  lons = lons[lonli:lonui]

  # example with high NDVI
  lat_point = -7.5
  lon_point = -41.0

  # example with missing data
  #lat_point = -11.0
  #lon_point = -41.5

  # calculate the indexes
  lat_idx = np.argmin(np.abs(lats - lat_point))
  lon_idx = np.argmin(np.abs(lons - lon_point))

  # extract only the data for the desired region
  data_point = data[ lat_idx , lon_idx ].round(2)

  # add the data to the list
  ndvi.append(data_point)

  # get start the date from the file name
  date_str = (file_name[file_name.find("AVHRR_")+6:file_name.find("_S10")])
  date_format = '%Y%m%d'
  date_start = datetime.strptime(date_str, date_format)
  date_start_str = date_start.strftime('%Y-%m-%d')

  # add the date to the list
  dates.append(date_start_str)

#==================================================================================================================#
# CREATE THE PLOT
#==================================================================================================================#

# choose the plot size (width x height, in inches)
fig, ax = plt.subplots(figsize=(14, 7))

# plot title
plt.title(f'Metop/AVHRR - NDVI: Índice De Vegetação Por Diferença Normalizada - Lat.: {lat_point}° - Lon.: {lon_point}°',  fontsize=12, fontweight='bold')

# x axis
plt.xlabel("Datas", fontsize=12, fontweight='bold')
plt.xticks(rotation=90)

# y axis
plt.ylabel("NDVI", fontsize=12, fontweight='bold')

# create the line plot with the missing points
ndvi = np.array(ndvi)
dates = np.array(dates)
mask = np.isfinite(ndvi)
plt.plot(dates[mask], ndvi[mask], linestyle='--', color='gray', linewidth=1, label='Dado Faltante Entre Datas')

# create the line plot without the missing points
plt.plot(dates, ndvi, linestyle='-', color='blue', linewidth=2, marker='o', label='NDVI')

# set min and max of the y axis
ax.set_ylim([0, 0.9])

# add grids
plt.grid(axis='x', color='0.95')
plt.grid(axis='y', color='0.95')

# add a legend
plt.legend()

#==================================================================================================================#
# SAVE AND VISUALIZE THE PLOT
#==================================================================================================================#

# save the figure
plt.savefig('image_15.png', bbox_inches='tight', pad_inches=0, dpi=300)

# show the plot
plt.show()