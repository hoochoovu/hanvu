import os
import re

def sanitize_filename(filename):
    """Sanitize the filename by removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def extract_quotes(input_folder, output_folder):
    """
    Extracts quotes from text files in a folder and saves them into separate files within subfolders.
    
    Args:
        input_folder: Path to the folder containing the input text files.
        output_folder: Path to the folder where the output subfolders will be created.
    """
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_filepath = os.path.join(input_folder, filename)
            subfolder_name = os.path.splitext(filename)[0]
            subfolder_path = os.path.join(output_folder, subfolder_name)
            
            # Create subfolder if it doesn't exist
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)
            
            with open(input_filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                quote = ""
                for line in lines:
                    if line.strip():
                        quote += line.strip() + " "
                    else:
                        if quote.strip():
                            # Extract first 5 words from the quote
                            words = quote.split()[:5]
                            # Create output filename
                            output_filename = f"{subfolder_name}_{'_'.join(words)}.txt"
                            output_filename = sanitize_filename(output_filename)
                            output_path = os.path.join(subfolder_path, output_filename)
                            
                            try:
                                # Write the quote to the output file
                                with open(output_path, 'w', encoding='utf-8') as output_file:
                                    output_file.write(f"{quote.strip()}\n")
                            except FileExistsError:
                                print(f"File {output_filename} already exists. Skipping.")
                            except Exception as e:
                                print(f"An error occurred while writing to {output_path}: {e}")
                            
                            quote = ""  # Reset the quote for the next one
                
                # Process any remaining quote at the end of the file
                if quote.strip():
                    words = quote.split()[:5]
                    output_filename = f"{subfolder_name}_{'_'.join(words)}.txt"
                    output_filename = sanitize_filename(output_filename)
                    output_path = os.path.join(subfolder_path, output_filename)
                    
                    try:
                        with open(output_path, 'w', encoding='utf-8') as output_file:
                            output_file.write(f"{quote.strip()}\n")
                    except FileExistsError:
                        print(f"File {output_filename} already exists. Skipping.")
                    except Exception as e:
                        print(f"An error occurred while writing to {output_path}: {e}")

if __name__ == "__main__":
    input_folder = r"E:\Python_Practice\Text Separator\Input"
    output_folder = r"E:\Python_Practice\Text Separator\Output"
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    extract_quotes(input_folder, output_folder)