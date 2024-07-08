import os
import time

folder_path = r'FOLDER PATH DIR'  # Specify the folder path where the text files are located

# Get the list of files in the folder
file_list = os.listdir(folder_path)

# Initialize an empty list to store the appended contents
appended_contents = []

# Initialize a loop counter
loop_count = 0

# Start the timer
start_time = time.time()

# Process each file in the folder
for file_name in file_list:
    file_path = os.path.join(folder_path, file_name)
    if os.path.isfile(file_path) and file_name.endswith('.txt'):
        with open(file_path, 'a+') as file:
            # Get the filename excluding the .txt extension
            filename = os.path.splitext(file_name)[0]
            # Append the filename to the contents
            file.write(f', {filename}\n')
            file.seek(0)  # Move the file pointer to the beginning
            # Read the contents of the file
            contents = file.read().strip()
            # Add the appended contents to the list
            appended_contents.append(contents)
    
    # Increment the loop counter
    loop_count += 1

# Stop the timer
end_time = time.time()

# Display the appended contents
for content in appended_contents:
    print(content)

# Display the loop count
print(f'Loop count: {loop_count}')

# Calculate and display the elapsed time
elapsed_time = end_time - start_time
print(f'Elapsed time: {elapsed_time} seconds')