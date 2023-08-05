# required modules
import hdf5plugin                               # for reading compressed data, a decompression library is needed
import glob                                     # unix style pathname pattern expansion
import os                                       # miscellaneous operating system interfaces
from satpy import Scene                         # scene object to hold satellite data

# initialise Scene
path_to_testdata = '../samples/mtg/RC0073/'
scn = Scene(filenames=glob.glob(os.path.join(path_to_testdata, '*BODY*.nc')), reader='fci_l1c_nc')

# load the datasets/composites of interest. note: the data inside the FCI files is stored upside down. The upper_right_corner='NE' argument flips it automatically in upright position.
scn.load(['ir_105'], upper_right_corner='NE')
scn.show('ir_105')