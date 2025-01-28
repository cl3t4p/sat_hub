from setuptools import setup, Extension

# Define the C++ extension module
module = Extension(
    "sat_img_lib",              # Module name
    sources=["src/lib.cpp"],    # C++ source file
    language="c++"                     # Specify C++ language
)

# Setup function
setup(
    name="sat_img_lib",
    version="1.0",
    description="Simple library for image processing",
    ext_modules=[module],
)
