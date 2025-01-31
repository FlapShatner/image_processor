# Image Border Processor

A Python tool for adding smooth borders to images with alpha channel support,
available both as a library and REST API.

## Features

- Convert images to PNG format
- Add customizable borders with transparency support
- Maintain image metadata
- REST API endpoint for image processing
- Support for multiple image formats

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Usage

### As a Library

```python
from image_processor import add_margin_and_border

input_path = "examples/input/sample.png"
output_path = "examples/output/result.png"
margin_size = 200  # Size of transparent margin in pixels
border_thickness = 100  # Thickness of the border in pixels
border_color = (255, 255, 255, 255)  # White border with full opacity (RGBA)

add_margin_and_border(input_path, output_path, margin_size, border_thickness, border_color)
```

### As an API

#### Start the server:

```bash
python src/run_server.py
```

The API will be available at `http://localhost:8000` with the following
   endpoints:

- `GET /`: Welcome message
- `POST /process-image/`: Process an image with the following parameters:
  - `file`: Image file (multipart/form-data)
  - `margin_size`: Size of transparent margin in pixels (default: 200)
  - `border_thickness`: Thickness of the border in pixels (default: 100)
  - `border_color`: Border color in RGBA format (default: "255,255,255,255")

Example curl request:

```bash
curl -X POST "http://localhost:8000/process-image/?margin_size=100&border_thickness=50&border_color=255,0,0,255" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"
```

API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

- `src/`
  - `api/`: FastAPI server and endpoints
  - `image_processor/`: Core image processing library
- `examples/`
  - `input/`: Sample input images
  - `output/`: Processed output images
- `tests/`: Unit tests

## Development

1. Create a virtual environment:

```bash
python -m venv borders
source borders/bin/activate  # On Windows: borders\Scripts\activate
```

2. Install development dependencies:

```bash
pip install -e .
```

3. Run tests:

```bash
python -m unittest discover tests
```

## License

MIT
