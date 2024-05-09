import os
import datetime
import pandas as pd
import csv
import re
from abifpy import Trace


def list_folders_with_mtime(directory):
    folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
    folder_info = []
    for folder in folders:
        folder_path = os.path.join(directory, folder)
        mtime = os.path.getmtime(folder_path)
        mtime_formatted = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        folder_info.append((folder, mtime_formatted))
    return folder_info


def filter_dict_by_suffix(dictionary, suffix_to_exclude):
    filtered_dict = {key: value for key, value in dictionary.items() if not key.endswith(suffix_to_exclude)}
    return filtered_dict


def remove_entries(dictionary, strings):
    keys_to_remove = []
    for key in dictionary.keys():
        if key in strings:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del dictionary[key]


def get_folder_paths(list_of_folders_in_Quintara_data):
    full_folder_paths = []
    path = r'O:\Quintara_data'
    for folder in list_of_folders_in_Quintara_data:
        full_folder_paths.append(os.path.join(path, folder))
    return full_folder_paths


# def constants
directory_path = r'O:\Quintara_data'
exclusionary_suffix = 'bestpick'  # remove bestpick folders
folders_to_remove = ['2012', '2023', '2024', 'DenaM_Gilead', 'MC']  # folders to not analyze

# create tuple with folders and mtime
folders_with_mtime = list_folders_with_mtime(directory_path)

# create dict
folders_with_mtime_dict = dict(folders_with_mtime)

# remove unwanted folders from dict
folders_with_mtime_dict = filter_dict_by_suffix(folders_with_mtime_dict, exclusionary_suffix)
remove_entries(folders_with_mtime_dict, folders_to_remove)

keys = list(folders_with_mtime_dict.keys())
values = list(folders_with_mtime_dict.values())

# write dict to csv
df_folders = pd.DataFrame([keys, values])
df_folders = df_folders.transpose()
df_folders.columns = ['Folder', 'mTime']
df_folders.to_csv('plate_folders.csv')
df_folders['Plate'] = df_folders['Folder'].str[:-3]
df_folders['Sequencer'] = df_folders['Folder'].str[-2:]

df_folders.to_csv('plate_folders.csv')

# Identify plates that were rerun
rerun_plates = df_folders[df_folders.duplicated(subset=['Plate'], keep=False)]

# Get the index values of the duplicated entries
duplicated_indexes = rerun_plates.index.tolist()

# Get first runs by mtime
second_runs = duplicated_indexes[::2]
print(second_runs)

# Remove 2nd runs from analysis
df_first_run_plates = df_folders.drop(second_runs)
first_run_plates = df_first_run_plates['Folder'].tolist()
df_first_run_plates.to_csv('first_runs.csv')

# Get order subfolders for each plate folder
first_run_folder_paths = get_folder_paths(first_run_plates)

subfolders_dict = {}

pattern = re.compile(r'^\d{6}')

for folder_path in first_run_folder_paths:
    items = os.listdir(folder_path)
    subfolders = [item for item in items if os.path.isdir(os.path.join(folder_path, item)) and pattern.match(item)]
    subfolders_dict[folder_path] = subfolders

subfolder_file_path = 'subfolders.csv'

with open(subfolder_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Folder Path', 'Subfolders'])
    for folder_path, subfolders in subfolders_dict.items():
        for subfolder in subfolders:
            writer.writerow([folder_path, subfolder])

# get ab1 files from each subfolder
ab1_files_dict = {}

df_subfolders = pd.read_csv('subfolders.csv')
subfolder_partial_paths = df_subfolders['Folder Path'].tolist()
subfolder_names = df_subfolders['Subfolders'].tolist()
subfolder_full_paths = []

for subfolder_path, subfolder in zip(subfolder_partial_paths, subfolder_names):
    subfolder_full_paths.append(os.path.join(subfolder_path, subfolder))

for subfolder_path in subfolder_full_paths:
    files = os.listdir(subfolder_path)
    ab1_files = [file for file in files if file.endswith('.ab1')]
    ab1_files_dict[subfolder_path] = ab1_files

ab1_file_path = 'ab1_files.csv'
with open(ab1_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['SubFolder Path', 'AB1 File'])
    for subfolder_path, ab1_files in ab1_files_dict.items():
        for ab1_file in ab1_files:
            writer.writerow([subfolder_path, ab1_file])

# get average qual values for each ab1 file
df_ab1 = pd.read_csv('ab1_files.csv')
ab1_partial_paths = df_ab1['SubFolder Path'].tolist()
ab1_names = df_ab1['AB1 File'].tolist()
ab1_full_paths = []
avg_qual_vals = []
lors = []

for ab1_partial_path, ab1_name in zip(ab1_partial_paths, ab1_names):
    ab1_full_paths.append(os.path.join(ab1_partial_path, ab1_name))

for sequence in ab1_full_paths:
    trace = Trace(sequence)
    qual_vals = trace.qual_val

    # get lor
    for i, num in enumerate(qual_vals):
        if num >= 45:
            lor = i

    if lor is None:
        lor = 0

    if lor > 100:
        qual_vals_trim = qual_vals[:lor + 1]
        qual_val = sum(qual_vals_trim) / len(qual_vals_trim)
        avg_qual_vals.append(qual_val)
        lors.append(lor)

    else:
        qual_val = sum(qual_vals) / len(qual_vals)
        avg_qual_vals.append(qual_val)
        lors.append(lor)

df_ab1['AVG Qual Values'] = avg_qual_vals
df_ab1['AVG LOR'] = lors

df_ab1.to_csv('df_ab1.csv')
