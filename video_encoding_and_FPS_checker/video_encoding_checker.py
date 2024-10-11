import os
import subprocess
import logging

def check_av1_encoding(video_path):
    """
    Checks if a video file has AV1 encoding using ffprobe.

    Args:
        video_path: Path to the video file.

    Returns:
        True if AV1 encoding is detected, False otherwise.
    """
    try:
        command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        output = subprocess.check_output(command, text=True).strip()
        return output == 'av1'
    except subprocess.CalledProcessError:
        logging.warning(f"Error checking encoding for {video_path}")
        return False

def scan_folder(input_folder, output_file):
    """
    Scans a folder for video files and reports those with AV1 encoding to a log file.

    Args:
        input_folder: Path to the folder containing video files.
        output_file: Path to the output log file.
    """
    logging.basicConfig(filename=output_file, level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.webm', '.avi')):  # Add more extensions if needed
                video_path = os.path.join(root, file)
                if check_av1_encoding(video_path):
                    logging.info(f"AV1 encoded video found: {video_path}")

if __name__ == "__main__":
    input_folder = r"E:\Dataset\All Video BG\Watermarked\Horizontal"
    output_file = "av1_videos.txt"  # You can customize the output file name

    scan_folder(input_folder, output_file)
    print(f"Scan complete. Results written to {output_file}") 