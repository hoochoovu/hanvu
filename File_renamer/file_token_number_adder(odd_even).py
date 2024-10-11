import os
import re
from natsort import natsorted

def add_tokens_to_filenames(folder_path, start_number):
    """
    Reads files from a folder, adds tokens to filenames based on a sequence, 
    and renames the files.

    Args:
        folder_path: Path to the folder containing the files.
        start_number: The starting number for the token sequence (1 or 2).
    """

    if start_number not in [1, 2]:
        raise ValueError("Starting number must be either 1 or 2.")

    current_number = start_number
    for filename in natsorted(os.listdir(folder_path)):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            new_filename = f"[{current_number}] {filename}"
            new_filepath = os.path.join(folder_path, new_filename)
            os.rename(filepath, new_filepath)
            current_number += 2

if __name__ == "__main__":
    folder_path = r"E:\Dataset\All Photo Creations for Video Generation\Artwork\Leonid Afremov Style\Vertical"
    while True:
        start_number_input = 1
        try:
            start_number = int(start_number_input)
            if start_number in [1, 2]:
                break
            else:
                print("Invalid input. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    add_tokens_to_filenames(folder_path, start_number)
    print("Files renamed successfully!")