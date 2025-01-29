from PIL import Image
import os
from metadata_handler import load_metadata, save_metadata, update_processing_history

def is_image(file_path):
    """
    Check if the file is an image by attempting to open it with Pillow.
    """
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify that the file is a valid image
        return True
    except Exception:
        return False

def convert_to_png(file_path):
    """
    Convert the file to PNG if it is an image and not already in PNG format.
    If the file is not an image or cannot be converted, do nothing.
    """
    if not is_image(file_path):
        print(f"Skipping non-image file: {file_path}")
        return

    # Load or create metadata
    metadata = load_metadata(file_path)

    with Image.open(file_path) as img:
        if img.format == "PNG":
            print(f"File is already in PNG format: {file_path}")
            return

        # Create a new file path with a .png extension
        base_name, _ = os.path.splitext(file_path)
        output_path = f"{base_name}.png"

        try:
            # Convert and save as PNG
            img.save(output_path, "PNG")
            
            # Update metadata
            metadata.update({
                "filename": os.path.basename(output_path),
                "format": "PNG",
                "file_size": os.path.getsize(output_path)
            })
            
            metadata = update_processing_history(metadata, "convert_to_png", {
                "original_format": img.format,
                "new_format": "PNG"
            })
            
            save_metadata(output_path, metadata)
            print(f"Converted {file_path} to PNG: {output_path}")
            
        except Exception as e:
            print(f"Failed to convert {file_path} to PNG: {e}")

# Example usage
file_path = "example.jpg"  # Replace with your file path
convert_to_png(file_path)