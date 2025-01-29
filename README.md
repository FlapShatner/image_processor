# Image Border Processor

A Python tool for adding smooth borders to images with alpha channel support.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from image_processor import add_smooth_border

input_path = "examples/input/sample.png"
output_path = "examples/output/result.png"
border_thickness = 10  # Thickness of the border in pixels
border_color = (255, 0, 0, 255)  # Red border with full opacity (RGBA)

add_smooth_border(input_path, output_path, border_thickness, border_color)
```

And here's a basic test file:

```python
:tests/test_border_processor.py
import unittest
from image_processor import add_smooth_border
import os
class TestBorderProcessor(unittest.TestCase):
def test_add_smooth_border(self):
input_path = "examples/input/sample.png"
output_path = "examples/output/result.png"
# Ensure the input file exists
self.assertTrue(os.path.exists(input_path))
# Test with red border
add_smooth_border(input_path, output_path, 10, (255, 0, 0, 255))
# Check if output file was created
self.assertTrue(os.path.exists(output_path))
if name == 'main':
unittest.main()
```

This structure provides several benefits:

1. Modular organization with separated source code and tests
2. Easy package installation with `setup.py`
3. Clear dependency management with `requirements.txt`
4. Example directory for sample images
5. Proper Python package structure with `__init__.py` files

To use this project:

1. Create the directory structure as shown above
2. Install the requirements:

```bash
pip install -r requirements.txt
```

3. Place your input images in the `examples/input` directory
4. Run the code using the example in the README
5. Find the processed images in the `examples/output` directory

The project can be installed in development mode using:

```bash
pip install -e .
```
