import os
import subprocess
import json
from datetime import datetime
import math

def get_file_info(file_path):
    """Gets the duration and stream info of a video file using ffprobe."""
    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        file_path
    ]
    try:
        output = subprocess.check_output(command).decode('utf-8')
        info = json.loads(output)
        duration = float(info['format']['duration'])
        video_stream = next((stream for stream in info['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next((stream for stream in info['streams'] if stream['codec_type'] == 'audio'), None)
        return duration, video_stream is not None, audio_stream is not None
    except subprocess.CalledProcessError as e:
        print(f"Error getting file info: {e}")
        return 0.0, False, False

def loop_video(input_file, output_file, target_duration, target_resolution, target_fps, crf, bitrate):
    """
    Loops a single video to create a new video with the specified duration using GPU-accelerated AV1 encoding.
    """
    input_duration, has_video, has_audio = get_file_info(input_file)
    if not has_video:
        print(f"Error: No video stream found in {input_file}")
        return

    loop_count = math.ceil(target_duration / input_duration)

    filter_complex = f"[0:v]scale={target_resolution[0]}:{target_resolution[1]}:force_original_aspect_ratio=decrease,pad={target_resolution[0]}:{target_resolution[1]}:(ow-iw)/2:(oh-ih)/2[scaled];"
    filter_complex += f"[scaled]loop={loop_count}:32767:0[looped];"
    filter_complex += f"[looped]trim=duration={target_duration}[outv]"

    ffmpeg_command = [
        'ffmpeg',
        '-hwaccel', 'cuda',
        '-i', input_file,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-c:v', 'av1_nvenc',
        '-crf', str(crf),
        '-b:v', bitrate,
        '-r', str(target_fps),
        '-gpu', '0',
    ]

    if has_audio:
        audio_filter = f"aloop={loop_count}:32767:0,atrim=duration={target_duration}"
        ffmpeg_command.extend([
            '-filter:a', audio_filter,
            '-c:a', 'aac',
            '-b:a', '192k'
        ])

    ffmpeg_command.append(output_file)

    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Looped video saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error looping video: {e}")

def process_videos(input_folder, output_folder, target_duration, target_resolution, target_fps, crf, bitrate):
    """
    Processes each video in the input folder, looping it to the target duration.

    Args:
        input_folder: The folder containing the video files to process.
        output_folder: The folder where the processed videos will be saved.
        target_duration: The desired duration for each output video in seconds.
        target_resolution: A tuple representing the desired resolution (width, height).
        target_fps: The desired frame rate for the output videos.
        crf: Constant Rate Factor for quality control.
        bitrate: Target bitrate for the output video.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.lower().endswith(('.mp4', '.mov', '.avi')):
            input_file = os.path.join(input_folder, file)
            output_file = os.path.join(output_folder, f"looped_{os.path.splitext(file)[0]}.mp4")
            
            loop_video(input_file, output_file, target_duration, target_resolution, target_fps, crf, bitrate)

def main():
    """Main function to process and loop videos."""
    video_input_folder = r"E:\Dataset\All Video BG\Samurai\smoke"
    output_folder = r"E:\Dataset\All Video BG\Samurai 1 Hour Videos\smoke"
    target_duration = 61*60  # Desired duration in seconds
    target_resolution = (1920, 1080)  # Desired resolution
    target_fps = 24
    
    # AV1 encoding parameters
    crf = 18  # Constant Rate Factor (adjust as needed, lower values = higher quality)
    bitrate = '6M'  # Target bitrate

    start_time = datetime.now()
    process_videos(video_input_folder, output_folder, target_duration, target_resolution, target_fps, crf, bitrate)
    end_time = datetime.now()
    total_time = end_time - start_time
    print(f"Processing completed in: {total_time}")

if __name__ == "__main__":
    main()