from PIL import Image
import os
from image_processor.metadata_handler import load_metadata, save_metadata, update_processing_history

class ImageConversionError(Exception):
    """Custom exception for image conversion errors"""
    pass

def is_image(file_path):
    """
    Check if the file is an image by attempting to open it with Pillow.
    """
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def convert_to_png(file_path):
    """
    Convert the file to PNG if it is an image and not already in PNG format.
    
    Args:
        file_path (str): Path to the image file
        
    Returns:
        str: Path to the converted PNG file
        
    Raises:
        ImageConversionError: If the file is not an image or conversion fails
    """
    if not is_image(file_path):
        raise ImageConversionError(f"Not a valid image file: {file_path}")

    try:
        with Image.open(file_path) as img:
            if img.format == "PNG":
                return file_path

            # Create a new file path with a .png extension
            base_name, _ = os.path.splitext(file_path)
            output_path = f"{base_name}.png"

            # Convert and save as PNG
            img.save(output_path, "PNG")
            
            # Update metadata
            metadata = load_metadata(file_path)
            metadata.update({
                "format": "PNG",
                "file_size": img.size
            })
            
            metadata = update_processing_history(metadata, "convert_to_png", {
                "original_format": img.format,
                "new_format": "PNG"
            })
            
            save_metadata(output_path, metadata)
            return output_path
            
    except Exception as e:
        raise ImageConversionError(f"Failed to convert {file_path} to PNG: {str(e)}")

# Example usage
# file_path = "example.jpg"  # Replace with your file path
# convert_to_png(file_path)