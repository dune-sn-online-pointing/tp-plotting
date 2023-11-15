# look at the notebook and do the same here
import numpy as np
import matplotlib.pyplot as plt
import argparse

from include.TriggerPrimitive import TriggerPrimitive as TriggerPrimitive
from include.PlottingUtils import *

# parse from command line the args.files and the number of tps to plot
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--files", nargs="+", help="files to read")
parser.add_argument("-n", "--number-tps", type=int, help="number of tps to plot")
parser.add_argument("-s", "--superimpose", action="store_true", help="superimpose plots")
args = parser.parse_args()

# read the file(s) and create arrays of TPs, using the class in TriggerPrimitive.py
# the code will deduce if the file is coming from offline or online data

tps_lists = []
file_is_offline = [] # index i is True if the file i is offline data, matching tps_lists[i]
for tpFile_path in  args.files:
    
    this_tps_list = saveTPs(tpFile_path, args.number_tps)
    # order them basing on start_time
    this_tps_list.sort(key=lambda x: x.time_start)
    tps_lists.append(this_tps_list)
    
    # check if the file is offline or online
    if (this_tps_list[0].event_number == 0):
        file_is_offline.append(True)
    else:
        file_is_offline.append(False)

plotTimePeak(tps_lists, args.files, 
             superimpose=args.superimpose, 
             quantile=1, 
             y_min=None, y_max=None) 

plotTimeOverThreshold(tps_lists, args.files,
                        superimpose=args.superimpose,
                        quantile=1,
                        y_min=None, y_max=None)

plotADCIntegral(tps_lists, args.files,
                superimpose=args.superimpose,
                quantile=1,
                y_min=None, y_max=None)

plotADCPeak(tps_lists, args.files,
            superimpose=args.superimpose,
            quantile=1,
            y_min=None, y_max=None)

plotChannel(tps_lists, args.files,
            superimpose=args.superimpose,
            x_min=None, x_max=None,
            y_min=None, y_max=None)

plotDetId(tps_lists, args.files,
            superimpose=args.superimpose,
            quantile=1,
            y_min=None, y_max=None)
        
plt.show()