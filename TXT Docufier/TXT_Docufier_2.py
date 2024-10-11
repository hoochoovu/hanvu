import os
import re
import docx

def natural_sort(list_of_strings):
  """Sorts a list of strings in a natural order, handling numeric parts correctly.

  Args:
      list_of_strings: The list of strings to be sorted.

  Returns:
      A new list containing the sorted strings.
  """
  convert = lambda text: int(text) if text.isdigit() else text
  alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
  return sorted(list_of_strings, key=alphanum_key)

def append_files_to_document(folder_path, output_format="docx"):
  """Appends all text files in a folder (including subfolders) to a document.

  Args:
      folder_path: The path to the folder containing the text files.
      output_format: The desired output format: "docx" or "txt". Defaults to "docx".
  """

  if output_format.lower() == "docx":
    doc = docx.Document()
  elif output_format.lower() == "txt":
    doc = open("combined_files.txt", "w", encoding="utf-8")
  else:
    raise ValueError("Invalid output format. Choose 'docx' or 'txt'.")

  # Get all text files recursively
  for root, _, files in os.walk(folder_path):
    for file in natural_sort(files):
      if file.endswith(".txt"):
        file_path = os.path.join(root, file)
        with open(file_path, "r", encoding="utf-8") as f:
          content = f.read()

          if output_format.lower() == "docx":
            doc.add_paragraph(content)
          else:
            doc.write(content + "\n")

  # Save the document
  if output_format.lower() == "docx":
    doc.save("combined_files.docx")
  else:
    doc.close()

if __name__ == "__main__":
  # Set the input folder path here
  folder_path = r"E:\ChatBot Therapy\Marcus Aurelius\Modern Stoic Book\The Main Book Sub Conscious Stoic\All Chapters"  
  # Set the desired output format here
  output_format = "txt"  # Choose either "docx" or "txt"
  append_files_to_document(folder_path, output_format)
  print(f"Files appended to 'combined_files.{output_format}'") 