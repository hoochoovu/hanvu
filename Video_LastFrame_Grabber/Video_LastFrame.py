import cv2
import os

# Define the input and output folders
input_folder = r"input"
output_folder = r"output"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate through all files in the input folder
for filename in os.listdir(input_folder):
    # Check if the file is a video
    if filename.endswith((".mp4", ".avi", ".mov")):  # Add more video extensions if needed
        # Construct the full path to the video file
        video_path = os.path.join(input_folder, filename)

        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Get the total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Set the frame position to the last frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)

        # Read the last frame
        ret, frame = cap.read()

        # Release the video capture object
        cap.release()

        # Construct the output filename
        output_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(output_folder, output_filename)

        # Save the frame as a PNG image
        if ret:
            cv2.imwrite(output_path, frame)
            print(f"Saved last frame of {filename} to {output_path}")
        else:
            print(f"Error reading last frame of {filename}")