import os

def process_files(folder_path):
    """
    Iterates through .txt files in a folder, removes the first 19 characters of each line,
    and saves the modified file.

    Args:
        folder_path (str): The path to the folder containing the .txt files.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as f:
                lines = f.readlines()

            # Remove the first 19 characters from each line
            modified_lines = [line[19:] for line in lines]

            # Save the modified content back to the file
            with open(file_path, "w") as f:
                f.writelines(modified_lines)

if __name__ == "__main__":
    folder_path = r"E:\Python_Practice\Video_DOWNLOADER_SCRAPER\Copy"
    process_files(folder_path)
    print("Files processed successfully!")