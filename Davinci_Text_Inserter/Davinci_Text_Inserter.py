# Initialize DaVinci Resolve scripting
resolve = bmd.scriptapp('Resolve')
project = resolve.GetProjectManager().GetCurrentProject()
timeline = project.GetCurrentTimeline()

# Define the path to the folder containing your .txt files
folder_path = r'E:\Python_Practice\Text Separator\New Quotes List\Bhagavad Gita'

# Set the duration of each subtitle in seconds
subtitle_duration = 4  # 4 seconds

# Set the starting timecode
start_timecode = 0  # Start at the beginning of the timeline

# Initialize the current timecode to the start timecode
current_timecode = start_timecode

# Get the list of text files in the folder
text_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.txt')])

# Loop through each text file in the folder
for text_file in text_files:
    text_file_path = os.path.join(folder_path, text_file)
    
    # Read the text from the .txt file
    with open(text_file_path, 'r') as file:
        subtitles = file.readlines()

    # Loop through each line in the text file
    for subtitle in subtitles:
        subtitle = subtitle.strip()  # Remove any extra whitespace

        if not subtitle:  # Skip empty lines
            continue

        # Calculate the start and end timecodes for the subtitle
        start_time = current_timecode
        end_time = start_time + subtitle_duration

        # Create a new subtitle clip
        new_clip = timeline.CreateTextClip()
        new_clip.SetProperty('Text', subtitle)
        new_clip.SetProperty('Start', start_time)
        new_clip.SetProperty('End', end_time)

        # Add the clip to the timeline on the first video track
        video_track = timeline.GetTrack('video', 1)
        video_track.Append(new_clip)

        # Update the current timecode to the end of this subtitle
        current_timecode = end_time

# Save the project after adding all subtitles
project.Save()