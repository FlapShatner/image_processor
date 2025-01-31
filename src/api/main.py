from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import shutil
from image_processor import add_margin_and_border, convert_to_png, load_metadata
from image_processor.format_processor import ImageConversionError
from image_processor.border_processor import BorderProcessingError
from pathlib import Path

app = FastAPI(title="Image Border Processor API")

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def cleanup_temp_dir(temp_dir: str):
    """Cleanup temporary directory and its contents"""
    shutil.rmtree(temp_dir, ignore_errors=True)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Image Border Processor API"}

@app.post("/process-image/")
async def process_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    border_thickness: int = 100,
    border_color: str = "255,255,255,255",
):
    margin_size = border_thickness + 20
    # Create temporary directory outside the context manager
    temp_dir = tempfile.mkdtemp()
    try:
        # Save uploaded file
        input_path = Path(temp_dir) / "input_image"
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Convert color string to tuple
            border_color_tuple = tuple(map(int, border_color.split(",")))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid border color format. Expected format: 'R,G,B,A' with values between 0-255"
            )
        
        try:
            # Convert to PNG if needed
            if not str(input_path).lower().endswith('.png'):
                input_path = Path(convert_to_png(str(input_path)))
        except ImageConversionError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        try:
            # Process the image
            output_path = Path(temp_dir) / "output_image.png"
            add_margin_and_border(
                str(input_path),
                str(output_path),
                margin_size,
                border_thickness,
                border_color_tuple
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters: {str(e)}"
            )
        except BorderProcessingError as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        
        try:
            # Load metadata
            metadata = load_metadata(str(output_path))
            
            # Add cleanup to background tasks
            background_tasks.add_task(cleanup_temp_dir, temp_dir)
            
            # Return the response
            return FileResponse(
                path=str(output_path),
                media_type="image/png",
                headers={
                    "X-Image-Metadata": str(metadata)
                }
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error preparing response: {str(e)}"
            )
        
    except HTTPException:
        # Clean up and re-raise
        cleanup_temp_dir(temp_dir)
        raise
    except Exception as e:
        # Clean up and raise unexpected error
        cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 