import os
import time
import requests

def download_urls(folder_path, main_output_folder):
    """
    Reads .txt files in a folder, downloads URLs with a 15-second delay,
    and saves the downloaded content to individual folders named after the files,
    within a main output folder.
    Skips URLs that have already been downloaded. Saves files as .mp4.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            output_folder = os.path.splitext(filename)[0]
            # Create the full path for the output folder within the main output folder
            full_output_folder = os.path.join(main_output_folder, output_folder)
            os.makedirs(full_output_folder, exist_ok=True)

            with open(filepath, 'r') as file:
                for url in file:
                    url = url.strip()
                    if url:
                        output_filename = os.path.basename(url)
                        output_filename = os.path.splitext(output_filename)[0] + ".mp4"
                        output_filepath = os.path.join(full_output_folder, output_filename)

                        if os.path.exists(output_filepath):
                            print(f"Skipping {url} - already downloaded.")
                            continue

                        try:
                            response = requests.get(url, stream=True)
                            response.raise_for_status()

                            with open(output_filepath, 'wb') as output_file:
                                for chunk in response.iter_content(chunk_size=1024 * 1024):
                                    output_file.write(chunk)

                            print(f"Downloaded {url} to {full_output_folder}")
                            time.sleep(15)
                        except requests.exceptions.RequestException as e:
                            print(f"Error downloading {url}: {e}")

if __name__ == "__main__":
    folder_path = r"FOLDER PATH"  # Folder with .txt files
    main_output_folder = r"OUTPUT PATH"  # Replace with your desired main output folder
    download_urls(folder_path, main_output_folder)