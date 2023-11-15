import numpy as np
from dataclasses import dataclass
import datetime
from dataclasses import dataclass
import datetime


#-------------------------------------------
# Constants
#-------------------------------------------

# these are taken from https://github.com/DUNE-DAQ/trgdataformats/blob/develop/include/trgdataformats/Types.hpp
# TODO change data types to proper C++-defined ones (uint32_t, etc)

INVALID_TIMESTAMP = datetime.datetime.max   # uint64_t
INVALID_CHANNEL = 0xFFFFFFFF                # uint32_t
INVALID_VERSION = 0XFFF                     # uint16_t
INVALID_DETIT = 0XFFF                       # uint16_t

#-------------------------------------------
# TriggerPrimitive struct
#-------------------------------------------

# format consistent with the header TriggerPrimitive.hpp: 
# https://github.com/DUNE-DAQ/trgdataformats/blob/develop/include/trgdataformats/TriggerPrimitive.hpp, 
# as of 2023-11-08
class TriggerPrimitive:
    def __init__(self,
                 time_start=INVALID_TIMESTAMP,
                 time_peak=INVALID_TIMESTAMP,
                 time_over_threshold=INVALID_TIMESTAMP,
                 channel=INVALID_CHANNEL,
                 adc_integral=0,
                 adc_peak=0,
                 detid=INVALID_DETIT,
                 type=0,
                 algorithm=0,
                 version=1,
                 flags=0,
                 particle_type=0,
                 event_number=0,
                 view=-1,
                 energy=0,
                 n_electrons=0,
                 track_id=0,
                 true_x=0,
                 true_y=0,
                 true_z=0):
        
        # DAQ TP variables
        self.time_start = time_start
        self.time_peak = time_peak
        self.time_over_threshold = time_over_threshold
        self.channel = channel
        self.adc_integral = adc_integral
        self.adc_peak = adc_peak
        self.detid = detid
        self.type = type
        self.algorithm = algorithm
        self.version = version
        self.flags = flags

        # Offline MC truth variables
        self.particle_type = particle_type  # create an enum for this; it's the particle type. For now, 1 is Marley, 2 is background
        self.event_number = event_number  # init, it starts from 1
        self.view = view  # create an enum for this; 0 is U, 1 is V, 2 is Z
        self.energy = energy  # in MeV, not printed as of Nov 10th
        self.n_electrons = n_electrons  # not printed as of Nov 10th
        self.track_id = track_id  # not printed as of Nov 10th
        self.true_x = true_x  # not printed as of Nov 10th
        self.true_y = true_y  # not printed as of Nov 10th
        self.true_z = true_z  # not printed as of Nov 10th
