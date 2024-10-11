import os
import random
import subprocess

def random_segment(input_file, duration, output_file, encoder, crf=None, bitrate=None, speed=None, gpu_id=0):
    # Get the duration of the input video
    cmd_duration = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', input_file
    ]
    total_duration = float(subprocess.check_output(cmd_duration).strip())
    
    # Ensure the random segment starts within the bounds
    start_time = random.uniform(0, max(0, total_duration - duration))

    # Construct the ffmpeg command
    encoding_options = []

    if encoder == "av1":
        encoding_options = [
            '-c:v', 'av1_nvenc',
            '-crf', str(crf),
            '-b:v', str(bitrate) if bitrate else '0'
        ]
    elif encoder == "h264":
        encoding_options = [
            '-c:v', 'h264_nvenc',
            '-preset', str(speed)
        ]
    else:
        raise ValueError("Unsupported encoder. Use 'av1' or 'h264'.")

    # FFMPEG command to extract segment
    cmd = [
        'ffmpeg', '-hwaccel', 'cuda', '-hwaccel_device', str(gpu_id), 
        '-ss', str(start_time), '-i', input_file, '-t', str(duration)
    ] + encoding_options + [output_file]
    
    # Run the command
    subprocess.run(cmd, check=True)

def process_videos(input_folder, output_folder, encoder='h264', iterations=1, duration=120, crf=30, bitrate=None, speed=4, gpu_id=0):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all .mp4 files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.mp4'):
            input_file = os.path.join(input_folder, file_name)
            base_name, _ = os.path.splitext(file_name)

            for i in range(iterations):
                output_file = os.path.join(output_folder, f"{base_name}_segment_{i+1}.mp4")
                random_segment(input_file, duration, output_file, encoder, crf, bitrate, speed, gpu_id)


if __name__ == "__main__":
    input_folder = r"I:\IntelDrive Dataset\Samurai-Monk-Roman 11 Min Videos\smoke"  # Specify the input folder path
    output_folder = "output"  # Specify the output folder path
    encoder = "av1"  # Change to 'h264' for H264 encoding
    iterations = 1  # Number of times to grab random segments per video
    crf = 18  # For AV1
    bitrate = "6M"  # For AV1
    speed = 3  # For H264
    gpu_id = 0  # GPU ID for Nvidia acceleration
    
    process_videos(input_folder, output_folder, encoder, iterations, duration=120, crf=crf, bitrate=bitrate, speed=speed, gpu_id=gpu_id)
