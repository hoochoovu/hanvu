import os
import subprocess
import gc
import psutil
import time

# Define the input and output folders
input_folder = r"E:\Davinci\STOIC Background Videos\V3\Videos"
output_folder = r"output"

# Get a list of all the video files in the input folder
video_files = os.listdir(input_folder)

# Define the chunk duration in seconds
chunk_duration = 605  # Minutes X Seconds

# Function to split video using ffmpeg with GPU acceleration and GPU selection
def split_video_with_ffmpeg(input_file, output_folder, chunk_duration, gpu_id=0):
    # Set the CUDA_VISIBLE_DEVICES environment variable
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    # Get the video duration using ffprobe
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
    video_duration = float(subprocess.check_output(cmd, shell=True).strip())

    num_chunks = int(video_duration // chunk_duration)

    for i in range(num_chunks):
        start_time = i * chunk_duration
        output_file = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(input_file))[0]}_Part{i + 1}.mp4")
        
        # Command to split the video using ffmpeg
        cmd = (
            f'ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i "{input_file}" '
            f'-ss {start_time} -t {chunk_duration} -c:v h264_nvenc -c:a copy "{output_file}"'
        )

        start_time_iteration = time.time()  # For logging time taken per iteration

        # Run the ffmpeg command and ensure subprocess cleanup
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error splitting video chunk {i + 1}: {e}")
            continue

        end_time_iteration = time.time()
        print(f"Chunk {i + 1} processed in {end_time_iteration - start_time_iteration} seconds.")

        # Explicitly clear memory and reset garbage collection
        gc.collect()
        free_resources()

# Function to release system resources
def free_resources():
    # Release CPU memory or close file handles if needed
    process = psutil.Process(os.getpid())
    
    # Print memory usage for debugging purposes
    print(f"Memory usage before release: {process.memory_info().rss / (1024 * 1024):.2f} MB")
    
    # Suggest to the OS to release memory resources (works for some OS, not all)
    process.memory_info()
    
    # Log GPU memory release or context reset (if needed)
    # This is where you would include any GPU-specific resource management if required.
    
    print(f"Memory usage after release: {process.memory_info().rss / (1024 * 1024):.2f} MB")

# Process each video file and use a specific GPU (e.g., GPU 0 or 1)
gpu_id = 0  # Change this to select a different GPU (0, 1, etc.)

for video_file in video_files:
    input_file = os.path.join(input_folder, video_file)
    split_video_with_ffmpeg(input_file, output_folder, chunk_duration, gpu_id)

print("Video splitting complete!")
