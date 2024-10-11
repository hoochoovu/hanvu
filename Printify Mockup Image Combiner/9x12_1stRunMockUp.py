import os
from PIL import Image

# Resize scale for foreground image
SCALE_FACTOR = .422

# Foreground overlay position
OFFSET_X = 863
OFFSET_Y = 812

# Function to process and overlay images
def overlay_images(bg_folder, fg_folder, output_folder, output_format="jpg"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    bg_images = [f for f in os.listdir(bg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    fg_images = [f for f in os.listdir(fg_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    for fg_file in fg_images:
        fg_image = Image.open(os.path.join(fg_folder, fg_file)).convert("RGBA")
        
        # Resize foreground image
        fg_width, fg_height = fg_image.size
        fg_image = fg_image.resize((int(fg_width * SCALE_FACTOR), int(fg_height * SCALE_FACTOR)), Image.LANCZOS)

        # Updated size after resizing
        fg_width, fg_height = fg_image.size
        
        # Create a subfolder inside the output folder for the foreground image
        fg_subfolder = os.path.join(output_folder, os.path.splitext(fg_file)[0])
        if not os.path.exists(fg_subfolder):
            os.makedirs(fg_subfolder)

        for bg_file in bg_images:
            bg_image = Image.open(os.path.join(bg_folder, bg_file)).convert("RGBA")
            bg_width, bg_height = bg_image.size

            # Check if the background image can fit the resized foreground with the offset
            if bg_width < fg_width + OFFSET_X or bg_height < fg_height + OFFSET_Y:
                print(f"Skipping {bg_file} with {fg_file}, background image too small for overlay.")
                continue

            # Create a copy of the background image to paste the foreground onto
            result_image = bg_image.copy()

            # Overlay the foreground image onto the background image
            result_image.paste(fg_image, (OFFSET_X, OFFSET_Y), fg_image)

            # Convert back to RGB and save the image
            result_image = result_image.convert("RGB")

            # Correct the output format for jpg
            if output_format.lower() == "jpg":
                output_format = "JPEG"
            
            # Save the image in the corresponding foreground subfolder
            output_file_name = f"[Mockup]{os.path.splitext(fg_file)[0]}_{bg_file}.{output_format.lower()}"
            output_path = os.path.join(fg_subfolder, output_file_name)
            result_image.save(output_path, format=output_format.upper())
            print(f"Saved: {output_path}")

# Main function
if __name__ == "__main__":
    bg_folder = r"E:\Python_Practice\Printify Mockup Image Combiner\Background Templates\firstrun"
    fg_folder = "fg"
    output_folder = "output"
    
    # Choose output format, jpg or png
    output_format = "jpg"  # Can be 'png' or 'jpg'

    overlay_images(bg_folder, fg_folder, output_folder, output_format)