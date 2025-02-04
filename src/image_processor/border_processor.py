from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import cv2
import os
from image_processor.metadata_handler import load_metadata, save_metadata, update_processing_history

class BorderProcessingError(Exception):
    """Custom exception for border processing errors"""
    pass


def add_margin_and_border(input_path, output_path, margin_size, border_thickness, border_color):
    """
    Add margin and border to an image.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image
        margin_size (int): Size of transparent margin in pixels
        border_thickness (int): Thickness of the border in pixels
        border_color (tuple): RGBA color tuple for the border
        
    Raises:
        BorderProcessingError: If there's an error during processing
        ValueError: If input parameters are invalid
    """
    try:
        # Validate input parameters
        if not os.path.exists(input_path):
            raise BorderProcessingError(f"Input file not found: {input_path}")
        
        if margin_size < 0:
            raise ValueError("Margin size must be non-negative")
        
        if border_thickness < 0:
            raise ValueError("Border thickness must be non-negative")
            
        if not isinstance(border_color, tuple) or len(border_color) != 4:
            raise ValueError("Border color must be an RGBA tuple")
            
        if not all(isinstance(v, int) and 0 <= v <= 255 for v in border_color):
            raise ValueError("Border color values must be integers between 0 and 255")

        # Load or create metadata
        try:
            metadata = load_metadata(input_path)
        except Exception as e:
            raise BorderProcessingError(f"Failed to load metadata: {str(e)}")
        
        try:
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

            # Check if image is rectangular (no transparency)
            is_rectangular = np.all(alpha[top:bottom+1, left:right+1] > 0)
            # is_rectangular = True

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

            # Create kernel for border - use rectangle for rectangular images, ellipse for others
            if is_rectangular:
                # Use half the border thickness for rectangular images
                adjusted_thickness = border_thickness // 3
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, 
                                                (adjusted_thickness, adjusted_thickness))
            else:
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, 
                                                (border_thickness, border_thickness))
            
            # Dilate the mask to create the border
            dilated_mask = cv2.dilate(mask, kernel, iterations=1)

            # Only smooth the border for non-rectangular images
            if is_rectangular:
                smoothed_mask = dilated_mask
            else:
                # Smooth the outer edge of the dilated mask
                smoothed_mask = cv2.GaussianBlur(dilated_mask, (0, 0), 
                                               sigmaX=border_thickness / 2)
                smoothed_mask = cv2.threshold(smoothed_mask, 128, 255, 
                                            cv2.THRESH_BINARY)[1]

            # Create a new image for the border
            border_image = Image.new("RGBA", new_image.size, (0, 0, 0, 0))
            border_pixels = border_image.load()

            # Apply the border color to the border mask
            for y in range(border_image.height):
                for x in range(border_image.width):
                    if smoothed_mask[y, x]:
                        border_pixels[x, y] = border_color

            # Composite the original image and the border
            final_image = Image.alpha_composite(border_image, new_image)

            # Save the final image first
            final_image.save(output_path)

            # Then update metadata with new processing information
            metadata.update({
                "width": final_image.width,
                "height": final_image.height,
            })
            
            metadata = update_processing_history(metadata, "add_margin_and_border", {
                "margin_size": margin_size,
                "border_thickness": adjusted_thickness if is_rectangular else border_thickness,
                "border_color": border_color
            })

            # Save metadata after the image is saved
            save_metadata(output_path, metadata)
            
            return final_image  # Optionally return the processed image
            
        except Exception as e:
            raise BorderProcessingError(f"Error saving output: {str(e)}")
            
    except (BorderProcessingError, ValueError) as e:
        raise
    except Exception as e:
        raise BorderProcessingError(f"Unexpected error: {str(e)}")

# Example usage
input_path = "examples/input/sample.png"
output_path = "examples/output/result.png"
margin_size = 200  # Size of transparent margin in pixels
border_thickness = 100  # Thickness of the border in pixels
border_color = (255, 255, 255, 255)  # White border with full opacity

add_margin_and_border(input_path, output_path, margin_size, border_thickness, border_color)