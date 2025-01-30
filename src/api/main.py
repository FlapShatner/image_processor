from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
from image_processor import add_margin_and_border, convert_to_png, load_metadata
from image_processor.format_processor import ImageConversionError
from pathlib import Path

app = FastAPI(title="Image Border Processor API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Image Border Processor API"}

@app.post("/process-image/")
async def process_image(
    file: UploadFile = File(...),
    margin_size: int = 200,
    border_thickness: int = 100,
    border_color: str = "255,255,255,255"
):
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
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
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing image: {str(e)}"
                )
            
            try:
                # Load metadata
                metadata = load_metadata(str(output_path))
                
                # Return the processed image and metadata
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
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 