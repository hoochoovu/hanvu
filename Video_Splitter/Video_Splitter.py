import os
import subprocess

# Define the input and output folders
input_folder = r"E:\Dataset\All Video BG\Watermarked\Vertical\Random\2 Minute\All Videos"
output_folder = r"output"

# Get a list of all the video files in the input folder
video_files = os.walk(input_folder)

# Define the chunk duration in seconds
chunk_duration = 120  # Minutes X Seconds

# Function to split video using ffmpeg with GPU acceleration
def split_video_with_ffmpeg(input_file, output_folder, chunk_duration):
    # Get the video duration using ffprobe
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
    video_duration = float(subprocess.check_output(cmd, shell=True).strip())

    num_chunks = int(video_duration // chunk_duration)

    for i in range(num_chunks):
        start_time = i * chunk_duration
        output_file = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(input_file))[0]}_Part{i + 1}.mp4")
        cmd = (
            f'ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i "{input_file}" '
            f'-ss {start_time} -t {chunk_duration} -c:v h264_nvenc -c:a copy "{output_file}"'
        )
        subprocess.run(cmd, shell=True)

# Process each video file
for video_file in video_files:
    input_file = os.path.join(input_folder, video_file)
    split_video_with_ffmpeg(input_file, output_folder, chunk_duration)

print("Video splitting complete!")
