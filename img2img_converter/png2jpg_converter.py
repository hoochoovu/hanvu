from PIL import Image
import os

def convert_images(input_folder, output_folder, allowed_extensions=("jpg", "jpeg", "png")):
    """
    Converts images in a folder to JPG or PNG while preserving resolution and DPI.

    Args:
        input_folder: Path to the folder containing images.
        output_folder: Path to the folder where converted images will be saved.
        allowed_extensions: Tuple of allowed input image extensions (case-insensitive).
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        name, ext = os.path.splitext(filename)
        ext = ext.lower()[1:]  # Get extension without the dot and make it lowercase

        if ext in allowed_extensions:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"{name}.jpg")

            try:
                img = Image.open(input_path)
                dpi = img.info.get("dpi") 

                # Preserve DPI if available, otherwise use default (72)
                img = Image.open(input_path).convert("RGB")  # Convert to RGB mode
                img.save(output_path, "JPEG", dpi=dpi or (300, 300), quality=95)

                print(f"Converted '{filename}' to '{os.path.basename(output_path)}'")

            except Exception as e:
                print(f"Error converting '{filename}': {e}")

# Example usage:
input_folder = r"E:\ETSY ETSY ETSY\Design for Trends\Scary Halloween Faces\Originals Pictures\Upscaled 8k 300DPI"
output_folder = "output"

convert_images(input_folder, output_folder) 