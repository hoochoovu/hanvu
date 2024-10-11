import os
import torch
from torchvision import transforms
from PIL import Image

# Define vertical and horizontal ratios
vertical_ratios = {
    '2x3': (2, 3),
    '3x4': (3, 4),
    '4x5': (4, 5),
    '5x7': (5, 7),
}

horizontal_ratios = {
    '3x2': (3, 2),
    '4x3': (4, 3),
    '5x4': (5, 4),
    '7x5': (7, 5),
}

def process_image(input_image, output_folder, ratio, output_format, use_transparency=False, dpi=None):
    output_format = output_format.lower()
    if output_format not in ['jpg', 'png']:
        raise ValueError("Output format must be either 'jpg' or 'png'.")

    # Get input image name without extension
    image_name = os.path.splitext(os.path.basename(input_image))[0]

    # Set file extension
    ext = 'png' if use_transparency and output_format == 'png' else output_format

    # Output file path (now all ratios are in the same folder)
    output_image = os.path.join(output_folder, f"{image_name}_{ratio[0]}x{ratio[1]}.{ext}")

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

        if width > height:  # Horizontal image
            crop_width = min(width, int(height * ratio[0] / ratio[1]))
            crop_height = height
        else:  # Vertical image
            crop_width = width
            crop_height = min(height, int(width * ratio[1] / ratio[0]))

        # If the crop size is smaller than the original image, crop the image
        if crop_width <= width and crop_height <= height:
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

            # Convert back to PIL Image
            img_processed = transforms.ToPILImage()(img_tensor.squeeze().cpu())

            # Save the processed image with the desired DPI
            img_processed.save(output_image, format='JPEG' if output_format == 'jpg' else 'PNG', dpi=dpi_to_use)
        else:
            print(f"Skipping {image_name} for ratio {ratio[0]}x{ratio[1]} due to size constraints.")

def process_images(input_folder, output_folder, output_format, use_transparency=False, dpi=None):
    # Walk through the input folder and subfolders
    for root, _, files in os.walk(input_folder):
        for image_file in files:
            input_image_path = os.path.join(root, image_file)
            
            # Skip non-image files
            if not image_file.lower().endswith(('jpg', 'jpeg', 'png', 'avif', 'webp')):
                continue

            # Create a subfolder for this file's output
            file_name = os.path.splitext(image_file)[0]
            file_output_folder = os.path.join(output_folder, file_name)
            os.makedirs(file_output_folder, exist_ok=True)

            # Open the image to check its orientation
            with Image.open(input_image_path) as img:
                width, height = img.size
                if width > height:  # Horizontal image
                    ratios = horizontal_ratios
                else:  # Vertical image
                    ratios = vertical_ratios

            # Process the image for each ratio, and store them in the same folder
            for ratio_name, ratio in ratios.items():
                process_image(input_image_path, file_output_folder, ratio, output_format, use_transparency, dpi)

if __name__ == '__main__':
    # Example usage
    input_folder = 'input'
    output_folder = 'output'
    output_format = 'jpg'  # 'jpg' or 'png'
    use_transparency = True  # For png images only
    dpi = 300  # Set DPI, or None to preserve original DPI

    process_images(input_folder, output_folder, output_format, use_transparency, dpi)
