import os

def delete_first_line(folder_path):
    """
    Iterates through .txt files in a folder and deletes the first line of each file.

    Args:
        folder_path (str): The path to the folder containing the .txt files.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as f:
                lines = f.readlines()

            # Delete the first line (index 0)
            modified_lines = lines[1:]

            # Save the modified content back to the file
            with open(file_path, "w") as f:
                f.writelines(modified_lines)

if __name__ == "__main__":
    folder_path = r"E:\Python_Practice\Video_DOWNLOADER_SCRAPER\Copy"
    delete_first_line(folder_path)
    print("First lines deleted successfully!")