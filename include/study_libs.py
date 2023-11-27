import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('/afs/cern.ch/work/d/dapullia/public/dune/online-pointing-utils/python/tps_text_to_image')
import create_images_from_tps_libs as tp2img 

'''
hist_n_tps
hist_total_charge
hist_max_charge
hist_length_main_track
hist_charge_density
'''
idx = {
    'time_start': 0,
    'time_over_threshold': 1,
    'time_peak': 2,
    'channel': 3,
    'adc_integral': 4,
    'adc_peak': 5,
    'mc_truth': 6,
    'event_number': 7,
    'plane': 8,
}


class Group: # Only good for HD geometry 1x2x6
    def __init__(self, tps):
        self.tps = tps
        self.n_tps = tps.shape[0]
        self.apa = np.unique(tps[:, idx['channel']] // 2560)
        self.is_clean, self.supernova_fraction, self.total_charge = self.extract_info()
        self.contains_supernova = self.supernova_fraction != 0
        self.event_number = np.unique(tps[:, idx['event_number']])
        self.track_time_lenght = (np.max(tps[:, idx['time_start']]+tps[:, idx['time_over_threshold']]) - np.min(tps[:, idx['time_start']]))*0.08
        self.track_channel_lenght = (np.max(tps[:, idx['channel']]) - np.min(tps[:, idx['channel']]))*0.5
        self.track_total_lenght = np.sqrt(self.track_time_lenght**2 + self.track_channel_lenght**2)
    def __len__(self):
        return self.n_tps
    def __str__(self):
        return str(self.tps)
    def __repr__(self):
        return str(self.tps)
    def get_pos(self):
        return self.x, self.y, self.z
    def get_apa(self):
        return self.apa
    def is_clean(self):
        return self.is_clean
    def supernova_fraction(self):
        return self.supernova_fraction
    def extract_info(self):
        supernova_counter = 0
        total_charge = 0
        for tp in self.tps:
            total_charge += tp[idx['adc_integral']]
            if tp[idx['mc_truth']] == 1:
                supernova_counter += 1
        supernova_fraction = supernova_counter / self.n_tps
        is_clean = supernova_fraction == 0 or supernova_fraction == 1
        return is_clean, supernova_fraction, total_charge
def save_groups(groups, name, save_txt=False, save_npy=False, out_dir_groups='data/'):
    if save_npy:
        np.save(out_dir_groups + name, groups)
    if save_txt:
        with open(out_dir_groups + name+ ".txt", "w") as f:
            for i, group in enumerate(groups):
                f.write("\nGroup %d\n\n" % i)
                for tp in group:
                    f.write("%s %s %s %s %s %s %s %s %s \n" % (tp['time_start'], tp['time_over_threshold'], tp['time_peak'], tp['channel'], tp['adc_integral'], tp['adc_peak'], tp['mc_truth'], tp['event_number'], tp['plane']))




def hist_n_tps(groups, main_neutrino_group_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    lens =[len(group) for group in groups]
    lens_supernova = [len(group) for group in groups if group.contains_supernova]
    lens_clean_supernova = [len(group) for group in groups if group.contains_supernova and group.is_clean]
    lens_mostly_supernova = [len(group) for group in groups if group.supernova_fraction >= 0.5]
    len_main_neutrino_group_per_event = [len(group) for group in main_neutrino_group_per_event]
    
    # find max value of the histogram
    max_value = max(lens)
    max_value_with_margin = int(max_value * 1.1)
    
    plt.figure(figsize=(11, 7))
    plt.hist(lens, bins=max_value_with_margin+1, range=(0, max_value_with_margin+1), label="All groups", align='left')
    plt.hist(lens_supernova, bins=max_value_with_margin+1, range=(0, max_value_with_margin+1), label="Contains supernova groups", color='red', align='left')
    plt.hist(lens_mostly_supernova, bins=max_value_with_margin+1, range=(0, max_value_with_margin+1), label="Mostly supernova groups", color='orange', align='left')
    plt.hist(lens_clean_supernova, bins=max_value_with_margin+1, range=(0, max_value_with_margin+1), label="Clean supernova groups", color='green', align='left')
    # add patch for the longest group per event
    plt.hist(len_main_neutrino_group_per_event, bins=max_value_with_margin+1, range=(0, max_value_with_margin+1), label="Main track per event", color='purple', hatch='xx', alpha=0.1, align='left')

    plt.xlabel("Number of TPs per group")
    plt.ylabel("Number of groups")
    plt.title(f"Number of TPs per group (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    # set axis log
    plt.yscale('log')
    plt.xticks(np.arange(0, max_value_with_margin+1,max_value_with_margin//10))
    plt.legend()
    plt.savefig(out_dir+f"hist_groups_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()



def hist_total_charge(groups, main_neutrino_group_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    total_charge = [group.total_charge for group in groups]
    total_charge_supernova = [group.total_charge for group in groups if group.contains_supernova]
    total_charge_clean_supernova = [group.total_charge for group in groups if group.contains_supernova and group.is_clean]
    total_charge_mostly_supernova = [group.total_charge for group in groups if group.supernova_fraction >= 0.5]
    total_charge_main_neutrino_group_per_event = [group.total_charge for group in main_neutrino_group_per_event]

    max_charge_value = max(total_charge)
    max_charge_value_with_margin = int(max_charge_value * 1.1)

    plt.hist(total_charge, bins=50, range=(0, max_charge_value_with_margin), label="All groups")
    plt.hist(total_charge_supernova, bins=50, range=(0, max_charge_value_with_margin), label="Contains supernova groups", color='red')
    plt.hist(total_charge_mostly_supernova, bins=50, range=(0, max_charge_value_with_margin), label="Mostly supernova groups", color='orange')
    plt.hist(total_charge_clean_supernova, bins=50, range=(0, max_charge_value_with_margin), label="Clean supernova groups", color='green')
    plt.hist(total_charge_main_neutrino_group_per_event, bins=50, range=(0, max_charge_value_with_margin), label="Main track per event", color='purple', hatch='xx', alpha=0.1)
    plt.xlabel("Total charge per group")
    plt.ylabel("Number of groups")
    plt.title(f"Total charge per group (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    # set axis log
    plt.yscale('log')
    plt.xticks(np.arange(0, max_charge_value_with_margin, max_charge_value_with_margin // 10))
    plt.legend()
    plt.savefig(out_dir + f"hist_groups_total_charge_tl_{ticks_limit}_cl_{channel_limit}.png", bbox_inches='tight', pad_inches=0.2)
    plt.clf()


def hist_max_charge(groups, main_neutrino_group_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    max_charge = [np.max(group.tps[:,idx['adc_integral']]) for group in groups]
    max_charge_supernova = [np.max(group.tps[:,idx['adc_integral']]) for group in groups if group.contains_supernova]
    max_charge_clean_supernova = [np.max(group.tps[:,idx['adc_integral']]) for group in groups if group.contains_supernova and group.is_clean]
    max_charge_mostly_supernova = [np.max(group.tps[:,idx['adc_integral']]) for group in groups if group.supernova_fraction >= 0.5]
    max_charge_main_neutrino_group_per_event = [np.max(group.tps[:,idx['adc_integral']]) for group in main_neutrino_group_per_event]

    max_charge_value = max(max_charge)
    max_charge_value_with_margin = int(max_charge_value * 1.1)

    plt.hist(max_charge, bins=50, range=(0, max_charge_value_with_margin), label="All groups")
    plt.hist(max_charge_supernova, bins=50, range=(0, max_charge_value_with_margin), label="Contains supernova groups", color='red')
    plt.hist(max_charge_mostly_supernova, bins=50, range=(0, max_charge_value_with_margin), label="Mostly supernova groups", color='orange')
    plt.hist(max_charge_clean_supernova, bins=50, range=(0, max_charge_value_with_margin), label="Clean supernova groups", color='green')
    plt.hist(max_charge_main_neutrino_group_per_event, bins=50, range=(0, max_charge_value_with_margin), label="Main track per event", color='purple', hatch='xx', alpha=0.1)
    plt.xlabel("Max charge per group")
    plt.ylabel("Number of groups")
    plt.title(f"Max charge per group (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    # set axis log
    plt.yscale('log')
    plt.xticks(np.arange(0, max_charge_value_with_margin, max_charge_value_with_margin // 10))
    plt.legend()
    plt.savefig(out_dir+f"hist_groups_max_charge_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()

def hist_n_tps_main_track(main_neutrino_group_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    lens =[len(group) for group in main_neutrino_group_per_event]
    lens_clean_supernova = [len(group) for group in main_neutrino_group_per_event if group.is_clean]
    lens_mostly_supernova = [len(group) for group in main_neutrino_group_per_event if group.supernova_fraction >= 0.5]
    lens_lower_threshold = [len(group) for group in main_neutrino_group_per_event if group.supernova_fraction >= 0.25]
    lens_higher_threshold = [len(group) for group in main_neutrino_group_per_event if group.supernova_fraction >= 0.75]

    # find max value of the histogram
    max_value = max(lens)
    max_value_with_margin = int(max_value * 1.1)

    plt.hist(lens, bins=120, range=(0, max_value_with_margin), label="Longest group per event", align='left')
    plt.hist(lens_lower_threshold, bins=120, range=(0, max_value_with_margin), label="supernova_fraction >= 0.25", color='red', align='left')
    plt.hist(lens_mostly_supernova, bins=120, range=(0, max_value_with_margin), label="supernova_fraction >= 0.5", color='orange', align='left')
    plt.hist(lens_higher_threshold, bins=120, range=(0, max_value_with_margin), label="supernova_fraction >= 0.75", color='yellow', align='left')
    plt.hist(lens_clean_supernova, bins=120, range=(0, max_value_with_margin), label="Clean supernova groups", color='green', align='left')
    plt.xlabel("Number of TPs per group")
    plt.ylabel("Number of groups")
    plt.title(f"Number of TPs per group (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    # set axis log
    plt.xticks(np.arange(0, max_value_with_margin, max_value_with_margin // 10))
    plt.legend()
    plt.savefig(out_dir+f"hist_groups_main_track_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()

def hist_total_lenght(groups, main_neutrino_group_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    total_lenght = [group.track_total_lenght for group in groups]
    total_lenght_supernova = [group.track_total_lenght for group in groups if group.contains_supernova]
    total_lenght_clean_supernova = [group.track_total_lenght for group in groups if group.contains_supernova and group.is_clean]
    total_lenght_mostly_supernova = [group.track_total_lenght for group in groups if group.supernova_fraction >= 0.5]
    total_lenght_main_neutrino_group_per_event = [group.track_total_lenght for group in main_neutrino_group_per_event]

    max_length = max(total_lenght)
    max_length_with_margin = int(max_length * 1.1)

    plt.hist(total_lenght, bins=50, range=(0, max_length_with_margin), label="All groups")
    plt.hist(total_lenght_supernova, bins=50, range=(0, max_length_with_margin), label="Contains supernova groups", color='red')
    plt.hist(total_lenght_mostly_supernova, bins=50, range=(0, max_length_with_margin), label="Mostly supernova groups", color='orange')
    plt.hist(total_lenght_clean_supernova, bins=50, range=(0, max_length_with_margin), label="Clean supernova groups", color='green')
    plt.hist(total_lenght_main_neutrino_group_per_event, bins=50, range=(0, max_length_with_margin), label="Main track per event", color='purple', hatch='xx', alpha=0.1)
    plt.xlabel("Total length per group")
    plt.ylabel("Number of groups")
    plt.title(f"Total length per group (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    # set axis log
    plt.yscale('log')
    plt.xticks(np.arange(0, max_length_with_margin, max_length_with_margin // 10))
    plt.legend()
    plt.savefig(out_dir+f"hist_groups_total_length_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()




def save_main_tracks_img(main_neutrino_group_per_event, channel_map, out_dir_img='plots/'):

    if not os.path.exists(out_dir_img):
        os.makedirs(out_dir_img)
    for group in main_neutrino_group_per_event:
        tp2img.save_img(group.tps,channel_map, out_dir_img, outname="event_"+str(group.tps[0][idx['event_number']]))




def hist_n_apas_per_event(n_apas_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    plt.hist(n_apas_per_event, bins=6, range=(0, 6), label="Number of APAs per event", align='left')
    plt.xlabel("Number of APAs per event")
    plt.xlabel("Number of APAs per event")
    plt.ylabel("Number of events")
    plt.title(f"Number of APAs per event (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    # set axis log
    plt.xticks(np.arange(0, 6, 1))
    plt.legend()
    plt.savefig(out_dir+f"hist_n_apas_per_event_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()



def hist_n_sn_groups_per_event(n_sn_groups_per_event, ticks_limit, channel_limit, n_tps_sn, n_tps_bkg, out_dir='plots/'):
    plt.hist(n_sn_groups_per_event, bins=40, range=(0,40), label="Number of SN groups per event", align='left')
    plt.xlabel("Number of SN groups per event")
    plt.ylabel("Number of events")
    plt.title(f"Number of SN groups per event (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    # create a text box with number of TPs per event
    textstr = f"Total TPs: {n_tps_sn+n_tps_bkg}\nSN TPs: {n_tps_sn}\nBkg TPs: {n_tps_bkg}"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.8, 0.85, textstr, transform=plt.gca().transAxes, fontsize=14, verticalalignment='top', bbox=props)

    # set axis log
    plt.xticks(np.arange(0, 40, 5))
    plt.legend()
    plt.savefig(out_dir+f"hist_n_sn_groups_per_event_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()

def hist_2D_ntps_total_charge(groups, main_neutrino_group_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    total_charge = []
    n_tps = []
    for group in groups:
        total_charge.append(group.total_charge)
        n_tps.append(len(group))
    # evaluate correlation
    corr = np.corrcoef(total_charge, n_tps)
    
    max_total_charge = max(total_charge)
    max_total_charge_with_margin = int(max_total_charge * 1.1)
    max_n_tps = max(n_tps)
    max_n_tps_with_margin = int(max_n_tps * 1.1)

    plt.hist2d(n_tps, total_charge, bins=(max_n_tps_with_margin, 100), range=((0, max_n_tps_with_margin+1), (0, max_total_charge_with_margin+1)), label="All groups")
    # create a text box with correlation
    textstr = f"Correlation: {corr[0][1]:.3f}"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.65, 0.9, textstr, transform=plt.gca().transAxes, fontsize=9, verticalalignment='top', bbox=props)
    
    plt.xlabel("Number of TPs per group")
    plt.ylabel("Total charge per group")
    plt.title(f"nTPs vs total charge (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    plt.colorbar()
    plt.savefig(out_dir+f"hist_2D_ntps_total_charge_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()

def hist_2D_ntps_max_charge(groups, main_neutrino_group_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    max_charge = []
    n_tps = []
    for group in groups:
        max_charge.append(np.max(group.tps[:,idx['adc_integral']]))
        n_tps.append(len(group))
    # evaluate correlation
    corr = np.corrcoef(max_charge, n_tps)
    max_charge_value = max(max_charge)
    max_charge_value_with_margin = int(max_charge_value * 1.1)
    max_n_tps = max(n_tps)
    max_n_tps_with_margin = int(max_n_tps * 1.1)

    plt.hist2d(n_tps, max_charge, bins=(max_n_tps_with_margin, 100), range=((0, max_n_tps_with_margin+1), (0, max_charge_value_with_margin+1)), label="All groups")
    # create a text box with correlation
    textstr = f"Correlation: {corr[0][1]:.3f}"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.65, 0.9, textstr, transform=plt.gca().transAxes, fontsize=9, verticalalignment='top', bbox=props)
    
    plt.xlabel("Number of TPs per group")
    plt.ylabel("Max charge per group")
    plt.title(f"nTPs vs max charge (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    plt.colorbar()
    plt.savefig(out_dir+f"hist_2D_ntps_max_charge_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()

def hist_2D_total_lenght_total_charge(groups, main_neutrino_group_per_event, ticks_limit, channel_limit, out_dir='plots/'):
    total_charge = []
    total_lenght = []
    for group in groups:
        total_charge.append(group.total_charge)
        total_lenght.append(group.track_total_lenght)
    # evaluate correlation
    corr = np.corrcoef(total_charge, total_lenght)
    
    max_total_charge = max(total_charge)
    max_total_charge_with_margin = int(max_total_charge * 1.1)
    max_total_lenght = max(total_lenght)
    max_total_lenght_with_margin = int(max_total_lenght * 1.1)

    plt.hist2d(total_lenght, total_charge, bins=50, range=((0, max_total_lenght_with_margin+1), (0, max_total_charge_with_margin+1)), label="All groups")

    # create a text box with correlation
    textstr = f"Correlation: {corr[0][1]:.3f}"
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.65, 0.9, textstr, transform=plt.gca().transAxes, fontsize=9, verticalalignment='top', bbox=props)

    plt.xlabel("Total lenght per group")
    plt.ylabel("Total charge per group")
    plt.title(f"Total lenght vs total charge (ticks limit: {ticks_limit}, channel limit: {channel_limit})")
    plt.colorbar()
    plt.savefig(out_dir+f"hist_2D_total_lenght_total_charge_tl_{ticks_limit}_cl_{channel_limit}.png",bbox_inches='tight', pad_inches=0.2)
    plt.clf()


