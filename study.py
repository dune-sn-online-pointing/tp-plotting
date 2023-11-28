import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import os
from dataclasses import dataclass
sys.path.append('/afs/cern.ch/work/d/dapullia/public/dune/online-pointing-utils/python/tps_text_to_image')
import create_images_from_tps_libs as tp2img 
import include.study_libs as study
import argparse
import ROOT

np.set_printoptions(threshold=sys.maxsize, linewidth=1000, precision=3,)
'''
Open questions:
- how easy is to distinguish the main track of a sn event from a bkg event?
- how much noise you have in each sn group?
- number of blips per sn event.
- number of bkg within a 3 meters radius.
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
plane_names = {
    0: "U",
    1: "V",
    2: "X",
}

def read_root_file (filename):
    file = ROOT.TFile.Open(filename, "READ")

    # get tree name
    nrows = []
    event = []
    matrix = []

    for i in file.GetListOfKeys():
        # get the TTree
        tree = file.Get(i.GetName())
        print(f"Tree name: {tree.GetName()}")
        tree.Print()

        for entry in tree:
            # nrows = entry.NRows
            # event = entry.Event
            # matrix = entry.Matrix
            nrows.append(entry.NRows)
            event.append(entry.Event)
            # Matrix is <class cppyy.gbl.std.vector<vector<int> > at 0x16365890>
            # extract the matrix from the vector<vector<int>> object to numpy array
            m = np.empty((nrows[-1], 9), dtype=int)
            for j in range(nrows[-1]):
                for k in range(9):
                    m[j][k] = entry.Matrix[j][k]
            matrix.append(m)

    return nrows, event, matrix

def read_root_file_to_groups(filename):
    file = ROOT.TFile.Open(filename, "READ")
    groups = []
    for i in file.GetListOfKeys():
        # get the TTree
        tree = file.Get(i.GetName())
        print(f"Tree name: {tree.GetName()}")
        tree.Print()

        for entry in tree:
            # nrows = entry.NRows
            # event = entry.Event
            # matrix = entry.Matrix
            nrows = entry.NRows
            event = entry.Event
            # Matrix is <class cppyy.gbl.std.vector<vector<int> > at 0x16365890>
            # extract the matrix from the vector<vector<int>> object to numpy array
            m = np.empty((nrows, 9), dtype=int)
            for j in range(nrows):
                for k in range(9):
                    m[j][k] = entry.Matrix[j][k]
            groups.append(study.Group(m))
    return groups


argparser = argparse.ArgumentParser()
argparser.add_argument('--plane', type=int, default=2)
argparser.add_argument('--output_folder', type=str, default="/afs/cern.ch/work/d/dapullia/public/dune/dataset_study/")
argparser.add_argument('--input_file', type=str, default="/afs/cern.ch/work/d/dapullia/public/dune/dataset_study/X/groups_tick_limits_25_channel_limits_5_min_tps_to_group_1.root")
args = argparser.parse_args()
plane = args.plane
output_folder = args.output_folder
input_file = args.input_file

channel_map = tp2img.create_channel_map_array(drift_direction=0)

folder_name = input_file.split("/")[-1].split(".")[0]


out_dir = output_folder + f"{plane_names[plane]}/{folder_name}/"
# out_dir_groups = out_dir+"groups/"
out_dir_img = out_dir+"img/"
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
if not os.path.exists(out_dir_img):
    os.makedirs(out_dir_img)


# nrows, event, matrix = read_root_file(filename)
# print(nrows[:10])
# print(event[:10])
# print(matrix[:10])

groups = read_root_file_to_groups(input_file)
n_events = len(np.unique([group.tps[0][idx['event_number']] for group in groups]))

main_neutrino_group_per_event = []
apas = []
n_sn_groups_per_event = []
n_tps_sn = 0
n_tps_bkg = 0

for i in range(1, n_events+1):
    groups_ev = [group for group in groups if group.tps[0][idx['event_number']] == i and group.contains_supernova]
    # consider the product of the number of TPs per group and the supernova fraction as the score of the group
    main_neutrino_group_per_event.append(max(groups_ev, key=lambda group: group.n_tps*group.supernova_fraction))
    apas.append([])
    n_sn_groups_per_event.append(len(groups_ev))
    for group in groups_ev:
        [apas[i-1].append(j) for j in group.get_apa()]
        tps_array = group.tps
        n_tps_sn += len(tps_array[tps_array[:, idx['mc_truth']] == 1])
        n_tps_bkg += len(tps_array) - len(tps_array[tps_array[:, idx['mc_truth']] == 1])


n_apas_per_event = [len(np.unique(apas[i-1])) for i in range(1, n_events+1)]


print("Number of groups: ", len(groups))
print("Number of clean groups: ", len([group for group in groups if group.is_clean]))
print("Number of supernova groups (both clean and dirty): ", len([group for group in groups if group.contains_supernova]))
print("Number of dirty groups that contain a supernova: ", len([group for group in groups if not group.is_clean and group.contains_supernova]))

with open(out_dir+"summary.txt", "w") as f:
    f.write("Number of groups: %d\n" % len(groups))
    f.write("Number of clean groups: %d\n" % len([group for group in groups if group.is_clean]))
    f.write("Number of supernova groups (both clean and dirty): %d\n" % len([group for group in groups if group.contains_supernova]))
    f.write("Number of dirty groups that contain a supernova: %d\n" % len([group for group in groups if not group.is_clean and group.contains_supernova]))


study.hist_n_tps(groups=groups, main_neutrino_group_per_event=main_neutrino_group_per_event, out_dir=out_dir, outname="hist_n_tps.png")

study.hist_n_tps_main_track(main_neutrino_group_per_event=main_neutrino_group_per_event, out_dir=out_dir, outname="hist_n_tps_main_track.png")

study.hist_total_charge(groups=groups, main_neutrino_group_per_event=main_neutrino_group_per_event, out_dir=out_dir, outname="hist_total_charge.png")

study.hist_max_charge(groups=groups, main_neutrino_group_per_event=main_neutrino_group_per_event, out_dir=out_dir, outname="hist_max_charge.png")
 
study.hist_total_lenght(groups=groups, main_neutrino_group_per_event=main_neutrino_group_per_event, out_dir=out_dir, outname="hist_total_length.png")

study.hist_n_apas_per_event(n_apas_per_event=n_apas_per_event, out_dir=out_dir, outname="hist_n_apas_per_event.png")

study.hist_n_sn_groups_per_event(n_sn_groups_per_event=n_sn_groups_per_event, n_tps_sn=n_tps_sn, n_tps_bkg=n_tps_bkg, out_dir=out_dir, outname="hist_n_sn_groups_per_event.png")

study.hist_2D_ntps_max_charge(groups=groups, main_neutrino_group_per_event=main_neutrino_group_per_event, out_dir=out_dir, outname="hist_2D_ntps_max_charge.png")

study.hist_2D_ntps_total_charge(groups=groups, main_neutrino_group_per_event=main_neutrino_group_per_event, out_dir=out_dir, outname="hist_2D_ntps_total_charge.png")

study.hist_2D_total_lenght_total_charge(groups=groups, main_neutrino_group_per_event=main_neutrino_group_per_event, out_dir=out_dir, outname="hist_2D_total_length_total_charge.png")

