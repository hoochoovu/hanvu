import os
from moviepy.editor import VideoFileClip, ColorClip, concatenate_videoclips, AudioClip

def extend_videos_with_black_screen(input_folder, output_folder, extension_duration=2):
    """
    Extends videos in a given folder with a black screen at the end, including empty audio.

    Args:
        input_folder (str): Path to the input folder containing videos.
        output_folder (str): Path to the output folder for extended videos.
        extension_duration (int, optional): Duration of the black screen in seconds. Defaults to 2.
    """

    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Traverse through the input folder and its subfolders
    for root, dirs, files in os.walk(input_folder):
        # Determine the relative path from the input folder
        relative_path = os.path.relpath(root, input_folder)
        # Create the corresponding subfolder in the output folder
        output_subfolder = os.path.join(output_folder, relative_path)
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)

        for filename in files:
            if filename.endswith('.mp4'):
                input_path = os.path.join(root, filename)
                output_path = os.path.join(output_subfolder, filename)

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

    print("Processing complete.")

# Example usage
input_folder = r'E:\Dataset\All STOISTICA Audio\Video Clips\Vertical\Original'
output_folder = r'E:\Dataset\All STOISTICA Audio\Video Clips\Vertical\2s Added'
extend_videos_with_black_screen(input_folder, output_folder, extension_duration=2)
