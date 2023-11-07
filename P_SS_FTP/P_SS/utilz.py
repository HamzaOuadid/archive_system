import hashlib
import tarfile
import os
import shutil


def diffrent_hashes(file1_path, file2_path, sql_file_name):
    archive = False

    # Extract files from the first tgz file
    with tarfile.open(file1_path, "r:gz") as tar1:
        tar1.extractall(path= 'temp/TAR1')
        extracted_dir1 = f"temp/TAR1/{tar1.getnames()[0]}"
        
    # Extract files from the second tgz file
    with tarfile.open(file2_path, "r:gz") as tar2:
        tar2.extractall(path= 'temp/TAR2')
        extracted_dir2 = f"temp/TAR2/{tar2.getnames()[0]}"


    # Calculate the hash of the SQL file in the first extracted directory
    with open(f"{extracted_dir1}/{sql_file_name}", "rb") as sql_file1:
        hash1 = hashlib.sha256(sql_file1.read()).hexdigest()

    # Calculate the hash of the SQL file in the second extracted directory
    with open(f"{extracted_dir2}/{sql_file_name}", "rb") as sql_file2:
        hash2 = hashlib.sha256(sql_file2.read()).hexdigest()

    # Clean up extracted files
    shutil.rmtree(extracted_dir1)
    shutil.rmtree(extracted_dir2)

    if hash1 == hash2:
        archive = False
    else:
        archive = True

    return archive



def replace_tgz(original_path, new_tgz_path, target_directory):
    # Remove the original tgz file
    try:
        shutil.rmtree(target_directory)
    except FileNotFoundError:
        pass
    
    # Copy the new tgz file to the target directory
    shutil.copy(new_tgz_path, target_directory)



def add_tgz(new_tgz_path, target_directory):
    # Copy the new tgz file to the target directory
    shutil.copy(new_tgz_path, target_directory)
    


def empty(directory_path):
    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        return
    
    # Get a list of all files and directories in the target directory
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)  # Remove files
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Remove directories and their contents


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"{file_path} has been deleted successfully")
    except OSError as e:
        print(f"Error: {e.filename} - {e.strerror}")
