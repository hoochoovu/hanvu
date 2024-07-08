import os
import re

def extract_quotes(input_folder, output_folder):
  """Extracts quotes and authors from a text file and saves them into separate files.

  Args:
    input_folder: Path to the folder containing the input text file.
    output_folder: Path to the folder where the output files will be saved.
  """

  for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
      filepath = os.path.join(input_folder, filename)
      with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

        # Split the content into quotes
        quotes = re.split(r'(?<=“)\s*-\s*(?=[A-Z])', content)

        # Extract and save each quote
        for quote in quotes:
          quote = quote.strip()

          # Extract the first 5 words of the quote
          first_five_words = ' '.join(quote.split()[:5])

          # Create the output filename
          output_filename = f"Thich Nhat Hanh-{first_five_words}.txt"  # Always use "Thich Nhat Hanh"
          output_path = os.path.join(output_folder, output_filename)

          # Write the quote to the output file
          with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(quote)

if __name__ == "__main__":
  input_folder = r"FOLDER TO TEXTS"
  output_folder = r"OUTPUT FOLDER"

  # Create the output folder if it doesn't exist
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

  extract_quotes(input_folder, output_folder)