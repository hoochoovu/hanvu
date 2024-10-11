import os
import torch
from torchvision import transforms
from PIL import Image

# Define the 5 default ratios
default_ratios = {
    '2x3': (2, 3),
    '3x4': (3, 4),
    '4x5': (4, 5),
    '5x7': (5, 7),
}

def process_image(input_image, output_folder, ratio, output_format, use_transparency=False, dpi=None):
    output_format = output_format.lower()
    if output_format not in ['jpg', 'png']:
        raise ValueError("Output format must be either 'jpg' or 'png'.")

    # Get input image name without extension
    image_name = os.path.splitext(os.path.basename(input_image))[0]

    # Set file extension
    ext = 'png' if use_transparency and output_format == 'png' else output_format

    # Define output folder for this ratio
    ratio_folder = os.path.join(output_folder, f"{ratio[0]}x{ratio[1]}")
    os.makedirs(ratio_folder, exist_ok=True)

    # Output file path
    output_image = os.path.join(ratio_folder, f"{image_name}_{ratio[0]}x{ratio[1]}.{ext}")

    # Open and process the image
    with Image.open(input_image) as img:
        # Get original DPI or use provided DPI
        original_dpi = img.info.get('dpi', (300, 300))
        dpi_to_use = dpi if dpi else original_dpi

        # Ensure the dpi is a tuple
        if isinstance(dpi_to_use, int):
            dpi_to_use = (dpi_to_use, dpi_to_use)

        # Convert image to RGB if it's not already
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Calculate crop size based on ratio
        width, height = img.size
        crop_width = min(width, int(height * ratio[0] / ratio[1]))
        crop_height = min(height, int(width * ratio[1] / ratio[0]))

        # Calculate crop coordinates
        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height

        # Crop the image
        img_cropped = img.crop((left, top, right, bottom))

        # Convert PIL Image to PyTorch tensor
        to_tensor = transforms.ToTensor()
        img_tensor = to_tensor(img_cropped).unsqueeze(0)

        # Move tensor to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        img_tensor = img_tensor.to(device)

        # Apply any GPU-accelerated transformations here if needed
        # For example, you could add color adjustments, filters, etc.

        # Convert back to PIL Image
        img_processed = transforms.ToPILImage()(img_tensor.squeeze().cpu())

        # Save the processed image with the desired DPI
        if use_transparency and output_format == 'png':
            img_processed.save(output_image, format='PNG', dpi=dpi_to_use)
        else:
            img_processed.save(output_image, format='JPEG' if output_format == 'jpg' else 'PNG', dpi=dpi_to_use)

def process_images(input_folder, output_folder, ratios, output_format, custom_ratio=None, use_transparency=False, dpi=None):
    # Walk through the input folder and subfolders
    for root, _, files in os.walk(input_folder):
        # Recreate subfolder structure in output folder
        relative_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, relative_path)

        # Process each image file in the current directory
        for image_file in files:
            input_image_path = os.path.join(root, image_file)
            
            # Skip non-image files
            if not image_file.lower().endswith(('jpg', 'jpeg', 'png')):
                continue

            # Create a subfolder for this file
            file_name = os.path.splitext(image_file)[0]
            file_output_folder = os.path.join(output_subfolder, file_name)
            os.makedirs(file_output_folder, exist_ok=True)

            # Process the image for each ratio
            for ratio_name, ratio in ratios.items():
                process_image(input_image_path, file_output_folder, ratio, output_format, use_transparency, dpi)
            
            # If custom ratio provided, process with custom ratio
            if custom_ratio:
                process_image(input_image_path, file_output_folder, custom_ratio, output_format, use_transparency, dpi)

if __name__ == '__main__':
    # Example usage
    input_folder = 'input'
    output_folder = r'E:\ETSY ETSY ETSY\Design for Trends\Scary Halloween Faces\Witch\Digital Downloads (Rubia Witch)'
    output_format = 'jpg'  # 'jpg' or 'png'
    use_transparency = True  # For png images only
    custom_ratio = (1, 1)  # Custom ratio, if needed (optional)
    dpi = 300  # Set DPI, or None to preserve original DPI

    process_images(input_folder, output_folder, default_ratios, output_format, custom_ratio, use_transparency, dpi)
