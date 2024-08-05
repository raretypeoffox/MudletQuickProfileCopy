import os
import shutil
import glob

# Define customizable variables
username = 'WindowsUsername'  # Change this to the actual username
profile_name = 'MainMudletProfileName'  # Change this to your main profile name (ie where we will copy from)
profile_files_to_copy = ['AltList.lua', 'InventoryList.lua']  # List of additional files to copy (leave as default for Vagonuth package)

# Define source directories and files
base_directory = fr'C:\Users\{username}\.config\mudlet\profiles'    # by default, where Mudlet keeps profiles on Windows (edit if needed)
source_directory = os.path.join(base_directory, profile_name, 'current')
profile_file_path = 'profiles.txt'  # Path to the file containing profile names
base_target_directory = base_directory  # Base directory for target profiles

# Function to read profile names from a file
def read_profile_names(file_path):
    with open(file_path, 'r') as file:
        profiles = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    return profiles

# Function to find the most recently modified XML file
def find_most_recent_file(directory, extension='*.xml'):
    files = glob.glob(os.path.join(directory, extension))
    if not files:
        raise FileNotFoundError("No files found with the specified extension.")
    
    most_recent_file = max(files, key=os.path.getmtime)
    return most_recent_file

# Function to keep only the most recent XML file in the 'current' directory
def keep_most_recent_xml(directory):
    xml_files = glob.glob(os.path.join(directory, '*.xml'))
    if not xml_files:
        return
    
    most_recent_file = max(xml_files, key=os.path.getmtime)
    
    for file in xml_files:
        if file != most_recent_file:
            os.remove(file)
            print(f'Deleted old XML file: {file}')
    
    print(f'Most recent XML file retained: {most_recent_file}')

# Function to copy the entire profile folder
def copy_profile_folder(source_folder, target_folder):
    if not os.path.exists(target_folder):
        shutil.copytree(source_folder, target_folder)
        print(f'Copied entire profile folder from {source_folder} to {target_folder}')
        keep_most_recent_xml(os.path.join(target_folder, 'current'))
    else:
        print(f'Target folder already exists: {target_folder}')

# Function to copy files to each target directory
def copy_files_to_targets(files, profile_names, base_directory):
    for profile in profile_names:
        target_directory = os.path.join(base_directory, profile)
        current_directory = os.path.join(target_directory, 'current')

        if not os.path.exists(target_directory):
            source_profile_folder = os.path.join(base_directory, profile_name)
            copy_profile_folder(source_profile_folder, target_directory)
            write_to_login(target_directory, profile)
        else:
            if not os.path.exists(current_directory):
                os.makedirs(current_directory)
            
            if os.path.isfile(files[0]):  # Copy the most recent XML file
                shutil.copy(files[0], current_directory)
                print(f'Copied {files[0]} to {current_directory}')
            else:
                print(f'File not found: {files[0]}')

            for file in files[1:]:  # Copy the .lua files
                if os.path.isfile(file):  # Check if the file exists
                    shutil.copy(file, target_directory)
                    print(f'Copied {file} to {target_directory}')
                else:
                    print(f'File not found: {file}')

# Function to write a new login file when creating a new profile                    
def write_to_login(target_directory, char_name):
    byte_array = []
    for char in char_name:
        byte_array.append(b'\x00')
        byte_array.append(char.encode('utf-8'))

    byte_array = [b'\x00', b'\x00', b'\x00', b'\n'] + byte_array

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    file_path = os.path.join(target_directory, "login")
    
    with open(file_path, 'wb') as file:
        for byte in byte_array:
            file.write(byte)

# Main execution
try:
    profile_names = read_profile_names(profile_file_path)
    
    recent_file = find_most_recent_file(source_directory)
    
    # List of files to copy: the first is the recent XML file, followed by the .lua files
    files_to_copy = [recent_file] + [os.path.join(base_directory, profile_name, file) for file in profile_files_to_copy]
    
    copy_files_to_targets(files_to_copy, profile_names, base_target_directory)
    
    print('File copying completed successfully.')
except Exception as e:
    print(f'An error occurred: {e}')
