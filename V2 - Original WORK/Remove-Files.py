import os
import shutil

# Get the path of the folder where the script is located
current_dir = os.path.dirname(os.path.abspath(__file__))


# Folders to exclude
exclude_dirs = ['video-input', 'video-output']

# Loop through the items in the current directory
for item in os.listdir(current_dir):
    item_path = os.path.join(current_dir, item)
    
    # Check if it's a directory and not excluded
    if os.path.isdir(item_path) and item not in exclude_dirs:
        # Delete all files and subfolders inside this directory
        for root, dirs, files in os.walk(item_path):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                shutil.rmtree(dir_path)
                print(f"Deleted folder: {dir_path}")

print("Cleanup complete.")