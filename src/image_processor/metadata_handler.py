import os
import json
from datetime import datetime
from PIL import Image

def get_image_info(image_path):
    """Get basic information about an image"""
    with Image.open(image_path) as img:
        # Check for transparency
        has_transparency = False
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            has_transparency = any(pixel[3] < 255 for pixel in img.convert('RGBA').getdata())

        return {
            "filename": os.path.basename(image_path),
            "format": img.format,
            "original_format": img.format,
            "width": img.width,
            "height": img.height,
            "has_transparency": has_transparency,
            "processing_history": [],
            "last_modified": datetime.now().isoformat()
        }

def load_metadata(image_path):
    """Load or create metadata for an image"""
    metadata_path = f"{os.path.splitext(image_path)[0]}.metadata.json"
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    return get_image_info(image_path)

def save_metadata(image_path, metadata):
    """Save metadata for an image"""
    metadata_path = f"{os.path.splitext(image_path)[0]}.metadata.json"
    metadata["last_modified"] = datetime.now().isoformat()
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def update_processing_history(metadata, operation, parameters=None):
    """Add a processing operation to the history"""
    metadata["processing_history"].append({
        "operation": operation,
        "parameters": parameters,
        "timestamp": datetime.now().isoformat()
    })
    return metadata 