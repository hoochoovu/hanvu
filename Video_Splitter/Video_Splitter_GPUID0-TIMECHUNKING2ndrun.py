import os
import subprocess

# Define the input and output folders
input_folder = r"E:\Dataset\All Video BG\Watermarked\Vertical\All Artwork"
output_folder = r"output3"

# Define the chunk duration in seconds (10 minutes = 600 seconds)
chunk_duration = 5.1  # Set to 604 for 10 minutes in seconds

# Function to split video dynamically
def split_video_dynamic_trimming(input_file, output_folder, chunk_duration, gpu_id=0):
    # Set the CUDA_VISIBLE_DEVICES environment variable to select the GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    # Get the video duration using ffprobe
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
    try:
        video_duration = float(subprocess.check_output(cmd, shell=True).strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting duration for {input_file}: {e}")
        return

    num_chunks = int(video_duration // chunk_duration)
    
    # Process each chunk dynamically
    for i in range(num_chunks + 1):  # Add +1 to ensure the last chunk is captured if it's less than chunk_duration
        start_time = i * chunk_duration
        
        # Handle the last chunk to avoid overflow
        if start_time >= video_duration:
            break
        
        # For the last chunk, adjust the duration to avoid overshooting
        if start_time + chunk_duration > video_duration:
            duration = video_duration - start_time
        else:
            duration = chunk_duration

        # Generate the output file name
        output_file = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(input_file))[0]}_Part{i + 1}.mp4")

        # FFmpeg command with start time (-ss) and duration (-t)
        cmd = (
            f'ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i "{input_file}" '
            f'-ss {start_time} -t {duration} -c:v h264_nvenc -c:a copy "{output_file}"'
        )

        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing chunk {i + 1} of {input_file}: {e}")
            continue

    print(f"Video '{os.path.basename(input_file)}' has been split into {num_chunks + 1} chunks.")

# Process each video file
gpu_id = 0  # Change this to select a different GPU (0, 1, etc.)

# Use os.walk to get video files
for dirpath, dirnames, filenames in os.walk(input_folder):
    # Iterate through files in the current directory
    for video_file in filenames:
        # Ensure we're only processing video files (e.g., .mp4)
        if video_file.endswith(".mp4"):
            input_file = os.path.join(dirpath, video_file)

            # Call the split function
            split_video_dynamic_trimming(input_file, output_folder, chunk_duration, gpu_id)

print("Video splitting complete!")
