from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import cv2
import os
from metadata_handler import load_metadata, save_metadata, update_processing_history

def add_margin_and_border(input_path, output_path, margin_size, border_thickness, border_color):
    # Load or create metadata
    metadata = load_metadata(input_path)
    
    # Load the image and extract alpha channel
    image = Image.open(input_path).convert("RGBA")
    alpha = np.array(image.split()[-1])
    
    # Find the bounding box of non-transparent pixels
    non_transparent = np.where(alpha > 0)
    if len(non_transparent[0]) == 0:  # Handle completely transparent images
        top, left, bottom, right = 0, 0, image.height, image.width
    else:
        top, bottom = non_transparent[0].min(), non_transparent[0].max()
        left, right = non_transparent[1].min(), non_transparent[1].max()

    # Calculate new dimensions with margin
    new_width = (right - left + 1) + (2 * margin_size)
    new_height = (bottom - top + 1) + (2 * margin_size)
    
    # Create new image with margin
    new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
    new_image.paste(image.crop((left, top, right + 1, bottom + 1)), 
                   (margin_size, margin_size))
    
    # Now add the border
    alpha = np.array(new_image.split()[-1])
    mask = (alpha > 0).astype(np.uint8) * 255

    # Dilate the mask to create the border
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border_thickness, border_thickness))
    dilated_mask = cv2.dilate(mask, kernel, iterations=1)

    # Smooth the outer edge of the dilated mask
    smoothed_mask = cv2.GaussianBlur(dilated_mask, (0, 0), sigmaX=border_thickness / 2)
    smoothed_mask = cv2.threshold(smoothed_mask, 128, 255, cv2.THRESH_BINARY)[1]

    # Subtract the original mask to get only the border
    border_mask = smoothed_mask - mask

    # Create a new image for the border
    border_image = Image.new("RGBA", new_image.size, (0, 0, 0, 0))
    border_pixels = border_image.load()

    # Apply the border color to the border mask
    for y in range(border_image.height):
        for x in range(border_image.width):
            if border_mask[y, x]:
                border_pixels[x, y] = border_color

    # Composite the original image and the border
    final_image = Image.alpha_composite(border_image, new_image)

    # Update metadata with new processing information
    metadata.update({
        "filename": os.path.basename(output_path),
        "width": final_image.width,
        "height": final_image.height,
        "file_size": os.path.getsize(output_path)
    })
    
    metadata = update_processing_history(metadata, "add_margin_and_border", {
        "margin_size": margin_size,
        "border_thickness": border_thickness,
        "border_color": border_color
    })
    
    # Save the final image and metadata
    final_image.save(output_path)
    save_metadata(output_path, metadata)

# Example usage
input_path = "examples/input/sample.png"
output_path = "examples/output/result.png"
margin_size = 200  # Size of transparent margin in pixels
border_thickness = 100  # Thickness of the border in pixels
border_color = (255, 255, 255, 255)  # White border with full opacity

add_margin_and_border(input_path, output_path, margin_size, border_thickness, border_color)