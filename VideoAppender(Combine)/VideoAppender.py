import os
import moviepy.editor as mpe

def append_mp4_files(input_folder, output_folder, output_filename):
    """Appends all .mp4 files in a given folder into a single output file.

    Args:
        input_folder (str): Path to the folder containing the .mp4 files.
        output_folder (str): Path to the folder where the output file will be saved.
        output_filename (str): Name of the output file.
    """

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get a list of all .mp4 files in the input folder
    mp4_files = [f for f in os.listdir(input_folder) if f.endswith(".mp4")]

    # Sort the files by name (optional for consistent order)
    mp4_files.sort()

    # Initialize an empty list to store video clips
    video_clips = []

    # Loop through the .mp4 files and load them into a list
    for filename in mp4_files:
        file_path = os.path.join(input_folder, filename)
        video_clip = mpe.VideoFileClip(file_path)
        video_clips.append(video_clip)

    # Concatenate the video clips into a single video
    final_clip = mpe.concatenate_videoclips(video_clips)

    # Save the final video to the output folder
    output_path = os.path.join(output_folder, output_filename)
    final_clip.write_videofile(output_path)

# Example usage:
input_folder = r"E:\Python_Practice\VideoAppender(Combine)\Input"  # Replace with the actual path
output_folder = r"E:\Python_Practice\VideoAppender(Combine)\Output"  # Replace with the actual path
output_filename = "combined_video.mp4"  # Name of your output video file

append_mp4_files(input_folder, output_folder, output_filename)