import os


def list_folders(directory):
    folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
    return folders


directory_path = r'O:\Quintara_data'
plate_folders = list_folders(directory_path)
print('Folders in', directory_path, 'are', plate_folders)

