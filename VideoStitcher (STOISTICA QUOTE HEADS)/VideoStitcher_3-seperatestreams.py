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

def select_videos(input_folder, target_duration):
    """Selects videos from the input folder to match the target duration."""
    video_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mov', '.avi')):
                video_files.append(os.path.join(root, file))

    selected_videos = []
    total_duration = 0
    while total_duration < target_duration:
        random_video = random.choice(video_files)
        
        # Check if the audio duration matches the video duration
        video_duration = get_file_duration(random_video)
        audio_duration = get_file_duration(random_video)  # Assuming audio is in the same file
        if abs(video_duration - audio_duration) > 0.1:  # Allow a small tolerance for rounding errors
            print(f"Skipping {random_video} - audio duration mismatch.")
            continue

        selected_videos.append(random_video)
        total_duration += video_duration
        if total_duration > target_duration:
            # If adding the next video would exceed the target duration, break the loop
            break

    return selected_videos

def process_video_files(video_files, target_resolution, codec):
    """Converts and scales video files."""
    processed_videos = []
    for video_file in video_files:
        if not video_file.lower().endswith(".mp4"):
            converted_video_path = os.path.splitext(video_file)[0] + ".mp4"
            convert_video_to_mp4(video_file, converted_video_path, codec)
            processed_videos.append(converted_video_path)
        else:
            processed_videos.append(video_file)
    return processed_videos

def append_videos(video_files, target_resolution, target_fps, codec, output_path):
    """Appends video files into a single video."""
    inputs = []
    filter_complex_parts = []
    for i, video in enumerate(video_files):
        inputs.extend(['-i', video])
        filter_complex_parts.append(f"[{i}:v]scale={target_resolution[0]}:{target_resolution[1]}[v{i}];")
    video_outputs = ''.join([f"[v{i}]" for i in range(len(video_files))])
    filter_complex = ''.join(filter_complex_parts) + f"{video_outputs}concat=n={len(video_files)}:v=1[outv]"

    ffmpeg_command = [
        'ffmpeg',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[outv]',  # Map the video output
        '-c:v', codec,  # Use the specified codec for video
        '-r', str(target_fps),
        '-y',  # Overwrite output file if it exists
        output_path
    ]
    print(f"Running FFmpeg command for video: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error appending videos: {e}")

def append_audios(video_files, output_path):
    """Appends audio streams of video files into a single audio stream."""
    inputs = []
    audio_inputs = ''.join([f"[{i}:a]" for i in range(len(video_files))])
    audio_concat_filter = f"{audio_inputs}concat=n={len(video_files)}:v=0:a=1[outa]"

    for video in video_files:
        inputs.extend(['-i', video])

    ffmpeg_command = [
        'ffmpeg',
        *inputs,
        '-filter_complex', audio_concat_filter,
        '-map', '[outa]',  # Map the combined audio output
        '-c:a', 'aac',  # Use AAC codec for audio
        '-strict', 'experimental',
        '-y',  # Overwrite output file if it exists
        output_path
    ]
    print(f"Running FFmpeg command for audio: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error appending audios: {e}")

def merge_audio_video(video_file, audio_file, output_path, codec, target_duration, target_fps):
    """Merges audio and video into a single file."""
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_file,
        '-i', audio_file,
        '-c:v', codec,
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-r', str(target_fps),
        '-t', str(target_duration),  # Trim video to target duration
        '-y',  # Overwrite output file if it exists
        output_path
    ]
    print(f"Running FFmpeg command for merging: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Merged video saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging audio and video: {e}")

def merge_videos(input_folder, output_folder, target_duration, target_resolution, target_fps=24, codec='h264_nvenc'):
    """Main function to handle the merging process."""
    video_files = select_videos(input_folder, target_duration)

    processed_videos = process_video_files(video_files, target_resolution, codec)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_output_path = os.path.join(output_folder, f"processed_video_{timestamp}.mp4")
    audio_output_path = os.path.join(output_folder, f"processed_audio_{timestamp}.aac")
    merged_output_path = os.path.join(output_folder, f"merged_video_{timestamp}.mp4")

    append_videos(processed_videos, target_resolution, target_fps, codec, video_output_path)
    append_audios(processed_videos, audio_output_path)
    merge_audio_video(video_output_path, audio_output_path, merged_output_path, codec, target_duration, target_fps)

def main():
    """Main function to stitch videos together."""
    video_input_folder = r"E:\Python_Practice\VideoStitcher\input"
    output_folder = "output"
    target_duration = 59.0  # Desired duration in seconds
    target_resolution = (1920, 1080)  # Desired resolution
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
