import os
import requests
import time

def download_videos_from_urls(export_folder, output_folder="videos"):
    """
    Downloads videos from a list of collected URLs stored in files within the export folder.
    Saves the downloaded videos to the specified output folder.
    The filename of each downloaded video includes the name of the text file it was read from.
    """
    os.makedirs(output_folder, exist_ok=True)  # Create output folder if it doesn't exist
    
    for filename in os.listdir(export_folder):
        if filename.endswith(".txt"):
            export_filepath = os.path.join(export_folder, filename)
            text_file_name = os.path.splitext(filename)[0]  # Get name without extension
            
            with open(export_filepath, "r", encoding="utf-8") as f:
                for video_url in f:
                    video_url = video_url.strip()
                    if not video_url:
                        continue
                    try:
                        # Download the video
                        response = requests.get(video_url)
                        response.raise_for_status()
                        
                        # Construct the filename
                        original_video_filename = os.path.basename(video_url)
                        extension = os.path.splitext(original_video_filename)[1]
                        if not extension:
                            extension = ".mp4"  # Default to .mp4 if no extension found
                        
                        new_video_filename = f"[{text_file_name}]{original_video_filename}"
                        if extension.lower() == ".mp4":
                            new_video_filename = new_video_filename.replace(extension, f"_file{extension}")
                        
                        # Save the video
                        video_filepath = os.path.join(output_folder, new_video_filename)
                        with open(video_filepath, "wb") as video_file:
                            video_file.write(response.content)
                        print(f"Downloaded: {new_video_filename}")
                        
                        # Wait if necessary to avoid server rate limits
                        time.sleep(5)
                    except Exception as e:
                        print(f"Error downloading video from {video_url}: {e}")

# Example usage
export_folder = r"E:\Python_Practice\Video_DOWNLOADER_SCRAPER\video_urls\Need Scraping"  # Folder containing collected URLs
output_folder = "videos"  # Folder to store downloaded videos
download_videos_from_urls(export_folder, output_folder)