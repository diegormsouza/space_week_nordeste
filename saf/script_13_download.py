#-------------------------------------------------------------------------------------------------------------------
# Training - Processing EUMETSAT Data and Products - Script 13: Downloading files using the requests library
# Author: Diego Souza (INPE/CGCT/DISSM)
#-------------------------------------------------------------------------------------------------------------------

# required modules
import requests                                  # HTTP library for Python
from requests.auth import HTTPBasicAuth          # basic authentication
import os                                        # miscellaneous operating system interfaces
import zipfile                                   # tools to create, read, write, append, and list a ZIP file
from datetime import datetime, timedelta         # basic date and time types
from dateutil.relativedelta import relativedelta # unix style pathname pattern expansion

# local directory
local_dir = "samples_script_13"; os.makedirs(local_dir, exist_ok=True)

# start date (yyyymmdd)
date_start = '20230501'

# end date (yyyymmdd)
date_end = '20230721'

# interval (month)
interval = 1

# convert to datetime
date_start = datetime(int(date_start[0:4]), int(date_start[4:6]), int(date_start[6:8]))
date_end = datetime(int(date_end[0:4]), int(date_end[4:6]), int(date_end[6:8]))

# create our references for the loop
date_loop = date_start

# loop between dates
while (date_loop <= date_end):

  # days to download
  days = ['01', '11', '21']

  for day in days:
  # for each day in the list

    # download parameters
    year = date_loop.strftime('%Y')
    month = date_loop.strftime('%m')
    url = 'https://datalsasaf.lsasvcs.ipma.pt/'
    product = '/PRODUCTS/EPS/ENDVI10/ENVI/'
    date = f'{year}/{month}/{day}/'
    file_name = f'METOP_AVHRR_{year}{month}{day}_S10_AMs_V200.zip'

    # user and password
    user = 'diegosouza'
    password = 'myLSASAF2023#'

    try:
      # download file
      print(f'Downloading the file: {file_name} ...')
      my_request = requests.get(url + product + date + file_name, auth = HTTPBasicAuth(user, password))
      open(local_dir + '//' + file_name, 'wb').write(my_request.content)

      # unzip file
      with zipfile.ZipFile(local_dir + '//' + file_name, 'r') as zip_ref:
        zip_ref.extractall(local_dir)

      print("Download finished.")
    except:
      print("File not found!")

  # increment the reference date
  date_loop = date_loop + relativedelta(months=interval)