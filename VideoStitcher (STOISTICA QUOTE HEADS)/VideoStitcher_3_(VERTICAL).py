import os
import subprocess
import random
import datetime

def get_file_duration(file_path):
    """Gets the duration of a video file using ffprobe."""
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    try:
        output = subprocess.check_output(command).decode('utf-8').strip()
        return float(output)
    except subprocess.CalledProcessError as e:
        print(f"Error getting file duration: {e}")
        return 0.0

def convert_video_to_mp4(input_file, output_file, codec):
    """Converts a video file to MP4 format using FFmpeg with GPU acceleration."""
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', codec,  # Choose GPU encoder
        '-c:a', 'aac',  # Convert audio to AAC
        '-strict', 'experimental',
        output_file
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting video to MP4: {e}")

def merge_videos(input_folder, output_folder, target_duration, target_resolution, target_fps=24, codec='h264_nvenc'):
    """
    Merges videos from a folder to create a new video with the specified duration.
    Retains the audio from the original videos.

    Args:
        input_folder: The folder containing the video files to merge.
        output_folder: The folder where the merged video will be saved.
        target_duration: The desired duration for the merged video in seconds.
        target_resolution: A tuple representing the desired resolution (width, height).
        target_fps: The desired frame rate for the merged video (default: 24).
        codec: The codec to use for video encoding ('h264_nvenc' or 'av1_nvenc').
    """
    video_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mov', '.avi')):
                video_files.append(os.path.join(root, file))

    merged_videos = []
    total_duration = 0
    while total_duration < target_duration:
        random_video = random.choice(video_files)
        
        # Use video duration to include silence
        video_duration = get_file_duration(random_video)

        merged_videos.append(random_video)
        total_duration += video_duration
        if total_duration > target_duration:
            # If adding the next video would exceed the target duration, break the loop
            break

    # Convert videos to MP4 if necessary
    for i, video_file in enumerate(merged_videos):
        if not video_file.lower().endswith(".mp4"):
            converted_video_path = os.path.splitext(video_file)[0] + ".mp4"
            convert_video_to_mp4(video_file, converted_video_path, codec)
            merged_videos[i] = converted_video_path

    # Create FFmpeg command to combine videos
    inputs = []
    for video in merged_videos:
        inputs.extend(['-i', video])

    # Create a filter complex for video scaling and concatenation
    filter_complex_parts = []
    for i, video in enumerate(merged_videos):
        filter_complex_parts.append(f"[{i}:v]scale={target_resolution[0]}:{target_resolution[1]}[v{i}];")
    video_outputs = ''.join([f"[v{i}]" for i in range(len(merged_videos))])
    filter_complex = ''.join(filter_complex_parts) + f"{video_outputs}concat=n={len(merged_videos)}:v=1[outv]"

    # Create a filter complex for audio concatenation
    audio_inputs = ''.join([f"[{i}:a]" for i in range(len(merged_videos))])
    audio_concat_filter = f"{audio_inputs}concat=n={len(merged_videos)}:v=0:a=1[outa]"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    merged_video_path = os.path.join(output_folder, f"merged_video_{timestamp}.mp4")

    ffmpeg_command = [
        'ffmpeg',
        *inputs,
        '-filter_complex', f"{filter_complex};{audio_concat_filter}",
        '-map', '[outv]',  # Map the video output
        '-map', '[outa]',  # Map the combined audio output
        '-c:v', codec,  # Use the specified codec for video
        '-c:a', 'aac',  # Use AAC codec for audio
        '-strict', 'experimental',
        '-r', str(target_fps),
        '-t', str(target_duration),  # Trim video to target duration
        merged_video_path
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Merged video saved to: {merged_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging videos: {e}")

def main():
    """Main function to stitch videos together."""
    video_input_folder = r"E:\Dataset\ALL STOIC QUOTE HEAD VIDEOS"
    output_folder = "output"
    target_duration = 120.0  # Desired duration in seconds
    target_resolution = (1080, 1920)  # Desired resolution
    number_of_iterations = 1  # Number of times to run the merge process
    codec = 'h264_nvenc'  # Choose between 'h264_nvenc' and 'av1_nvenc'

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(number_of_iterations):
        print(f"Starting iteration {i + 1} of {number_of_iterations}")
        start_time = datetime.datetime.now()
        merge_videos(video_input_folder, output_folder, target_duration, target_resolution, codec=codec)
        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        print(f"Iteration {i + 1} completed in: {total_time}")

if __name__ == "__main__":
    main()