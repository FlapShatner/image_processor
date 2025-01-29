from setuptools import setup, find_packages

setup(
    name="image-border-processor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
    ],
    python_requires=">=3.7",
) 