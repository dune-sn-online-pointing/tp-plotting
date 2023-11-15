import numpy as np
import matplotlib.pyplot as plt
from .TriggerPrimitive import TriggerPrimitive

# Function to save tps in a list
def saveTPs (filename, max_tps):
    
    data = np.genfromtxt(filename, delimiter=' ', max_rows=max_tps)
    data = data.transpose()
    
    # there could also be a text variable that is set to "DAQ" or "LArSoft
    if len(data) == 11:
        daq = True
        print ("File ", filename, " comes from DAQ")
    elif len(data) == 20:
        daq = False
        print ("File ", filename, " comes from LArSoft")
    else:
        print ("-----------------------------------------------------------------------")
        print ("ERROR: TPs in this file have a number of variables not matching nor DAQ nor LArSoft:", len(data))
        print ("-----------------------------------------------------------------------")
        return
    
    # if daq is true, save only the first 10 variables in the TP objects
    # appo vectors just for clarity, could be avoided
    time_start = data[0]
    time_over_threshold = data[1]
    time_peak = data[2] 
    channel = data[3]
    adc_integral = data[4]
    adc_peak = data[5]
    detid = data[6]
    type = data[7]
    algorithm = data[8]
    version = data[9]
    flags = data[10]
    
    # offset to have the first TP at t=0, we need this?
    # time_shift = time_start[0] 
    # time_start -= time_shift
    # time_start *= 16e-9 # convert to seconds, do we want it?
        
    # if it comes from the daq, directly create the TP list
    if (daq):
        # create a list to store the TPs
        tp_list = []
        # loop over the number of TPs and append tps to the list
        for i in range(len(time_start)):
            tp_list.append(TriggerPrimitive(time_start[i], time_peak[i], time_over_threshold[i], channel[i], adc_integral[i], 
                                            adc_peak[i], detid[i], type[i], algorithm[i], version[i], flags[i]))
    else:
        # appo vectors 
        particle_type = data[11]
        event_number = data[12]
        view = data[13]
        energy = data[14]
        n_electrons = data[15]
        track_id = data[16]
        true_x = data[17]
        true_y = data[18]
        true_z = data[19]
        # here using the constructor with also the offline variables
        tp_list = []
        for i in range(len(time_start)):
            tp_list.append(TriggerPrimitive(time_start[i], time_peak[i], time_over_threshold[i], channel[i], adc_integral[i], 
                                            adc_peak[i], detid[i], type[i], algorithm[i], version[i], flags[i], particle_type[i], 
                                            event_number[i], view[i], energy[i], n_electrons[i], track_id[i], true_x[i], true_y[i], 
                                            true_z[i]))
        # delete the appo vectors
        del time_start, time_over_threshold, time_peak, channel, adc_integral, adc_peak, detid, type, algorithm, version, flags
        del particle_type, event_number, view, energy, n_electrons, track_id, true_x, true_y, true_z
    
    return tp_list

#################################################################################]
# FUNCTIONS TO PLOT THE TPS

# Common options
alpha = 0.4 # transparency of the histograms, lower is more opaque
grid_in_superimpose = False
grid_in_not_superimpose = False


def plotTimePeak(tps_lists, file_names, superimpose=False, quantile=1, y_min=0, y_max=None):
    fig = plt.subplot(111)  # for when superimpose is true
    legend_properties = {'weight': 'bold'}
    
    # compute x_max using quantile, considering all the files
    time_peak_all_files = []
    for tps_file in tps_lists:
        time_peak_all_files += [tp.time_peak - tp.time_start for tp in tps_file]
    x_max = np.quantile(time_peak_all_files, quantile)
    
    del time_peak_all_files # free memory

    for i, tps_file in enumerate(tps_lists):
        time_peak = [tp.time_peak - tp.time_start for tp in tps_file]
        label = f"Time Peak, file {file_names[i].split('/')[-1]}"
        
        if not superimpose:
            fig = plt.subplot(111)
            plt.grid(grid_in_not_superimpose) 
        fig.set_xlabel("Time Peak [ticks]")

        if y_min is not None:
            fig.set_ylim(bottom=y_min)
        if y_max is not None:
            fig.set_ylim(top=y_max)
 
        # bin size is optimized to have a number of bins depending on x_max, thus based on the quantile
        fig.hist(time_peak, bins=np.arange(-0.5, x_max + 0.5), label=label, alpha=alpha, edgecolor='black')

        if not superimpose:
            fig.set_title(f"Time Peak, file {file_names[i].split('/')[-1]}", fontweight='bold')
            plt.show()

    if superimpose:
        fig.legend(prop=legend_properties)
        plt.grid(grid_in_superimpose)
        plt.show()
        
    del time_peak # free memory

    return


def  plotTimeOverThreshold(tps_lists, file_names, superimpose=False, quantile=1, y_min=0, y_max=None):
    fig = plt.subplot(111)  # for when superimpose is true
    legend_properties = {'weight': 'bold'}
    
    # compute x_max using quantile, considering all the files
    time_over_threshold_all_files = []
    for tps_file in tps_lists:
        time_over_threshold_all_files += [tp.time_over_threshold for tp in tps_file]
    x_max = np.quantile(time_over_threshold_all_files, quantile)
    
    del time_over_threshold_all_files # free memory

    for i, tps_file in enumerate(tps_lists):
        time_over_threshold = [tp.time_over_threshold for tp in tps_file]
        label = f"Time over Threshold, file {file_names[i].split('/')[-1]}"
        
        if not superimpose:
            fig = plt.subplot(111)
            plt.grid(grid_in_not_superimpose) 
        fig.set_xlabel("Time over Threshold [ticks]")

        if y_min is not None:
            fig.set_ylim(bottom=y_min)
        if y_max is not None:
            fig.set_ylim(top=y_max)
 
        # bin size is optimized to have a number of bins depending on x_max, thus based on the quantile
        fig.hist(time_over_threshold, bins=np.arange(-0.5, x_max + 0.5), label=label, alpha=alpha, edgecolor='black')

        if not superimpose:
            fig.set_title(f"Time over Threshold, file {file_names[i].split('/')[-1]}", fontweight='bold')
            plt.show()

    if superimpose:
        fig.legend(prop=legend_properties)
        plt.grid(grid_in_superimpose)
        plt.show()
        
    # free memory
    del time_over_threshold

    return


def plotChannel(tps_lists, file_names, superimpose=False, x_min=0, x_max=None, y_min=0, y_max=None):
    fig = plt.subplot(111)  # for when superimpose is true
    legend_properties = {'weight': 'bold'}
    
    channel_all_files = []
    for tps_file in tps_lists:
        channel_all_files += [tp.channel for tp in tps_file] 

    for i, tps_file in enumerate(tps_lists):
        channel = [tp.channel for tp in tps_file]
        label = f"Channel, file {file_names[i].split('/')[-1]}"
        
        if not superimpose:
            fig = plt.subplot(111)
            plt.grid(grid_in_not_superimpose) 
        fig.set_xlabel("Channel")

        if y_min is not None:
            fig.set_ylim
        if y_max is not None:
            fig.set_ylim(top=y_max)
        
        if x_max is None:
            fig.set_xlim(right=np.max(channel_all_files))
        else:    
            fig.set_xlim(right=x_max)
            
            
        # bin size is optimized to have a number of bins depending on x_max, thus based on the quantile
        fig.hist(channel, bins=100, label=label, alpha=alpha)
        
        if not superimpose:
            fig.set_title(f"Channel, file {file_names[i].split('/')[-1]}", fontweight='bold')
            plt.show()
            
    if superimpose:
        fig.legend(prop=legend_properties)
        plt.grid(grid_in_superimpose)
        plt.show()
    
    del channel_all_files # free memory
    del channel # free memory

    return            

# look at above and create plotADCIntegral
def plotADCIntegral(tps_lists, file_names, superimpose=False, quantile=1, y_min=0, y_max=None):
    fig = plt.subplot(111)  # for when superimpose is true
    legend_properties = {'weight': 'bold'}
    
    # compute x_max using quantile, considering all the files
    adc_integral_all_files = []
    for tps_file in tps_lists:
        adc_integral_all_files += [tp.adc_integral for tp in tps_file]
    
    x_max = np.quantile(adc_integral_all_files, quantile)
    
    del adc_integral_all_files # free memory

    for i, tps_file in enumerate(tps_lists):
        adc_integral = [tp.adc_integral for tp in tps_file]
        label = f"ADC Integral, file {file_names[i].split('/')[-1]}"
        
        if not superimpose:
            fig = plt.subplot(111)
            plt.grid(grid_in_not_superimpose) 
        fig.set_xlabel("ADC Integral")

        if y_min is not None:
            fig.set_ylim(bottom=y_min)
        if y_max is not None:
            fig.set_ylim(top=y_max)
 
        # bin size is optimized to have a number of bins depending on x_max, thus based on the quantile
        # np.arange(-0.5, x_max + 0.5, (x_max+1)/300)
        fig.hist(adc_integral, bins=50, range=(-0.5,x_max+0.5), label=label, alpha=alpha, edgecolor='black')
        
        if not superimpose:
            fig.set_title(f"ADC Integral, file {file_names[i].split('/')[-1]}", fontweight='bold')
            plt.show()
            
    if superimpose:
        fig.legend(prop=legend_properties)
        plt.grid(grid_in_superimpose)
        plt.show()
        
    
    del adc_integral # free memory
    
    return

# look at previous functions and write plotADCPeak
def plotADCPeak(tps_lists, file_names, superimpose=False, quantile=1, y_min=0, y_max=None):
    fig = plt.subplot(111)  # for when superimpose is true
    legend_properties = {'weight': 'bold'}
    
    # compute x_max using quantile, considering all the files
    adc_peak_all_files = []
    for tps_file in tps_lists:
        adc_peak_all_files += [tp.adc_peak for tp in tps_file]
    x_max = np.quantile(adc_peak_all_files, quantile)
    
    del adc_peak_all_files # free memory

    for i, tps_file in enumerate(tps_lists):
        adc_peak = [tp.adc_peak for tp in tps_file]
        label = f"ADC Peak, file {file_names[i].split('/')[-1]}"
        
        if not superimpose:
            fig = plt.subplot(111)
            plt.grid(grid_in_not_superimpose) 
        fig.set_xlabel("ADC Peak")

        if y_min is not None:
            fig.set_ylim(bottom=y_min)
        if y_max is not None:
            fig.set_ylim(top=y_max)
 
        # bin size is optimized to have a number of bins depending on x_max, thus based on the quantile
        fig.hist(adc_peak, bins=50, range=(-0.5, x_max + 0.5), label=label, alpha=alpha, edgecolor='black')
        
        if not superimpose:
            fig.set_title(f"ADC Peak, file {file_names[i].split('/')[-1]}", fontweight='bold')
            plt.show()
            
    if superimpose:
        fig.legend(prop=legend_properties)
        plt.grid(grid_in_superimpose)
        plt.show()
        
    return

# look at previous functions and write plotDetId
def plotDetId(tps_lists, file_names, superimpose=False, quantile=1, y_min=0, y_max=None):
    fig = plt.subplot(111)  # for when superimpose is true
    legend_properties = {'weight': 'bold'}
    
    # compute x_max using quantile, considering all the files
    detid_all_files = []
    for tps_file in tps_lists:
        detid_all_files += [tp.detid for tp in tps_file]
    x_max = np.quantile(detid_all_files, quantile)
    
    del detid_all_files # free memory

    for i, tps_file in enumerate(tps_lists):
        detid = [tp.detid for tp in tps_file]
        label = f"DetId, file {file_names[i].split('/')[-1]}"
        
        if not superimpose:
            fig = plt.subplot(111)
            plt.grid(grid_in_not_superimpose) 
        fig.set_xlabel("DetId")
        # set ticks on x axis to be integers from 0 to x_max
        fig.set_xticks(np.arange(0, x_max + 1, 1))

        if y_min is not None:
            fig.set_ylim(bottom=y_min)
        if y_max is not None:
            fig.set_ylim(top=y_max)
 
        # bin size is optimized to have a number of bins depending on x_max, thus based on the quantile
        fig.hist(detid, bins=np.arange(-0.5, x_max + 0.5), label=label, alpha=alpha, edgecolor='black')
        
        if not superimpose:
            fig.set_title(f"DetId, file {file_names[i].split('/')[-1]}", fontweight='bold')
            plt.show()
            
    if superimpose:
        fig.legend(prop=legend_properties)
        plt.grid(grid_in_superimpose)
        plt.show()
        
    return
        