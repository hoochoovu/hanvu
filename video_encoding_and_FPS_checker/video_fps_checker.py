import os
import subprocess
import logging

def get_frame_rate(video_path):
    """
    Gets the frame rate of a video file using ffprobe.

    Args:
        video_path: Path to the video file.

    Returns:
        The frame rate as a float (e.g., 24.0, 29.97, 30.0), or None if the frame rate cannot be determined.
    """
    try:
        command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        output = subprocess.check_output(command, text=True).strip()
        if '/' in output:
            num, den = output.split('/')
            return float(num) / float(den)
        else:
            return float(output)  # Handle cases where frame rate is a direct number
    except subprocess.CalledProcessError:
        logging.warning(f"Error getting frame rate for {video_path}")
        return None

def scan_folder(input_folder):
    """
    Scans a folder for video files and groups them by frame rate.

    Args:
        input_folder: Path to the folder containing video files.
    """
    frame_rate_groups = {}

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.webm', '.avi')):
                video_path = os.path.join(root, file)
                frame_rate = get_frame_rate(video_path)

                if frame_rate is not None:
                    frame_rate_str = f"{frame_rate:.2f}fps"  # Format as "XX.XXfps"
                    if frame_rate_str not in frame_rate_groups:
                        frame_rate_groups[frame_rate_str] = []
                    frame_rate_groups[frame_rate_str].append(video_path)

    # Write results to separate files
    for frame_rate, video_list in frame_rate_groups.items():
        output_file = f"{frame_rate}.txt"
        with open(output_file, 'w') as f:
            for video_path in video_list:
                f.write(video_path + '\n')

if __name__ == "__main__":
    input_folder = r"E:\Dataset\All Video BG\Watermarked\Horizontal"
    scan_folder(input_folder)
    print("Scan complete. Frame rate lists created.")