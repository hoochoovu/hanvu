import os
import subprocess
import logging

def get_resolution(video_path):
    """
    Gets the resolution (width x height) of a video file using ffprobe.

    Args:
        video_path: Path to the video file.

    Returns:
        The resolution as a string (e.g., "1920x1080"), or None if the resolution cannot be determined.
    """
    try:
        command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0:s=, ', video_path]
        output = subprocess.check_output(command, text=True).strip()
        width, height = output.split(',')
        return f"{width}x{height}"
    except subprocess.CalledProcessError:
        logging.warning(f"Error getting resolution for {video_path}")
        return None

def scan_folder(input_folder):
    """
    Scans a folder for video files and groups them by resolution.

    Args:
        input_folder: Path to the folder containing video files.
    """
    resolution_groups = {}

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.webm', '.avi')):
                video_path = os.path.join(root, file)
                resolution = get_resolution(video_path)

                if resolution is not None:
                    if resolution not in resolution_groups:
                        resolution_groups[resolution] = []
                    resolution_groups[resolution].append(video_path)

    # Write results to separate files
    for resolution, video_list in resolution_groups.items():
        output_file = f"{resolution}.txt"
        with open(output_file, 'w') as f:
            for video_path in video_list:
                f.write(video_path + '\n')

if __name__ == "__main__":
    input_folder = r"E:\Dataset\All Video BG\Watermarked\Horizontal"
    scan_folder(input_folder)
    print("Scan complete. Resolution lists created.")