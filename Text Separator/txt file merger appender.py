import os

def merge_txt_files(folder_path, output_file="ALLMERGED.txt"):
  """
  Merges all .txt files in a given folder into a single file, removing duplicates.

  Args:
    folder_path: The path to the folder containing the .txt files.
    output_file: The name of the output file (default: "merged.txt").
  """

  # Initialize an empty set to store unique lines
  unique_lines = set()

  # Iterate through all files in the folder
  for filename in os.listdir(folder_path):
    # Check if the file is a .txt file
    if filename.endswith(".txt"):
      file_path = os.path.join(folder_path, filename)

      # Open the file and read its content
      with open(file_path, "r") as f:
        for line in f:
          # Add the line to the set, ensuring uniqueness
          unique_lines.add(line.strip())

  # Write the unique lines to the output file
  with open(output_file, "w") as f:
    for line in unique_lines:
      f.write(line + "\n")

# Example usage
folder_path = r"E:\Dataset\PEXELS\Z Links to Scrape" # Replace with your actual folder path
output_file = "merged.txt"  # You can change this if you want a different output filename
merge_txt_files(folder_path, output_file)

print(f"Merged all .txt files in {folder_path} to {output_file}")