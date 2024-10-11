import os
from moviepy.editor import VideoFileClip, ColorClip, concatenate_videoclips, AudioClip

def extend_videos_with_black_screen(input_folder, extension_duration=0.25):
    """
    Extends videos in a given folder and its subfolders with a black screen at the end, including empty audio.
    Outputs to a sibling folder named "0.25 added" for each processed subfolder.
    
    Args:
        input_folder (str): Path to the input folder containing videos.
        extension_duration (float, optional): Duration of the black screen in seconds. Defaults to 0.25.
    """
    for root, dirs, files in os.walk(input_folder):
        # Check if there are any .mp4 files in the current folder
        if any(file.endswith('.mp4') for file in files):
            # Determine relative path to maintain sub-folder structure
            relative_path = os.path.relpath(root, input_folder)
            
            # Create the corresponding output folder under "0.25 added"
            output_folder = os.path.join(os.path.dirname(input_folder), "0.25 added", relative_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Process each .mp4 file in the current folder
            for filename in files:
                if filename.endswith('.mp4'):
                    input_path = os.path.join(root, filename)
                    output_path = os.path.join(output_folder, filename)
                    
                    # Load the original video
                    video = VideoFileClip(input_path)
                    
                    # Create a black screen clip
                    black_screen = ColorClip(size=video.size, color=(0, 0, 0), duration=extension_duration)
                    
                    # Create an empty audio clip
                    empty_audio = AudioClip(lambda t: [0], duration=extension_duration)
                    
                    # Set the empty audio to the black screen
                    black_screen = black_screen.set_audio(empty_audio)
                    
                    # Concatenate the original video with the black screen
                    extended_video = concatenate_videoclips([video, black_screen])
                    
                    # Write the extended video to the output path
                    extended_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
                    
                    # Close the clips
                    video.close()
                    black_screen.close()
                    extended_video.close()
            
            print(f"Processed folder: {root}")
    
    print("Processing complete.")

# Example usage
input_folder = r"E:\Python_Practice\Video_2s_Adder\input"
extend_videos_with_black_screen(input_folder)
