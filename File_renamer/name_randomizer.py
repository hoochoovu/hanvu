import os
import random

# Set the directory that will be renaming the files.
directory = r"E:\Dataset\All Photo Creations for Video Generation\Artwork\Ink and Wash\Miyamoto Musashi\Ready\Vertical\Portrait"

# Get a list of all the files in the directory.
files = os.listdir(directory)

# Get a list of all the .jpg files in the directory.
jpg_files = [file for file in files if file.endswith(".jpg")]

# Shuffle the list of .jpg files.
random.shuffle(jpg_files)

# Rename the .jpg files with the given name BackgroundBG0001, choosing at random and adding 1 to the name each time.
i = 1
for jpg_file in jpg_files:
    new_name = "Miyamoto Musashi - Ink and Wash - {:04d}.jpg".format(i)
    os.rename(os.path.join(directory, jpg_file), os.path.join(directory, new_name))
    i += 1