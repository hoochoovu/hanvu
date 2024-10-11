import os
import re

def rename_files(folder_path):
    """
    Renames .txt files in a folder based on the first line (title) and first number (chapter),
    removing invalid characters from the filename.

    Args:
        folder_path (str): Path to the folder containing the text files.
    """

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)

            # Read the first line (title) with UTF-8 encoding
            with open(filepath, 'r', encoding='utf-8') as f:
                title = f.readline().strip()

            # Find the first number in the file
            chapter = None
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    match = re.search(r'\d+', line)
                    if match:
                        chapter = match.group()
                        break

            # Handle cases where no number is found
            if chapter is None:
                print(f"No chapter number found in '{filename}', skipping...")
                continue

            # Create the new filename and remove invalid characters
            new_filename = f"{chapter} - {title}.txt"
            invalid_chars = ':;?"|'
            for char in invalid_chars:
                new_filename = new_filename.replace(char, '')

            new_filepath = os.path.join(folder_path, new_filename)

            # Rename the file
            os.rename(filepath, new_filepath)
            print(f"Renamed '{filename}' to '{new_filename}'")

# Example usage:
folder_path = r"E:\ChatBot Therapy\Marcus Aurelius\Modern Stoic Book\The Main Book Sub Conscious Stoic\8" 
rename_files(folder_path)