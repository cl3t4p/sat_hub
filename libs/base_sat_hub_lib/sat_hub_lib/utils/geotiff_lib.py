import rasterio
from rasterio.windows import from_bounds
from shapely import Polygon
from rasterio.io import MemoryFile
import os
from PIL import Image
import numpy as np
from scipy.interpolate import interp1d

# Set the environment variable to disable signing requests for public S3 buckets
os.environ["AWS_NO_SIGN_REQUEST"] = "YES"


def extract_boundingbox_into_tiff(geotiff_uri, output_file: str, bbox: Polygon):
    """
    Extracts a bounding box from a list of TIFF files or rasterio DatasetReader objects and saves the result to a new GeoTIFF file.
        tiff_files (list): List of (paths to the input TIFF files | list of s3 urls)
        output_file (str): Path to the output file where the extracted bounding box will be saved.
        bbox (Polygon): A shapely Polygon object representing the bounding box to extract.
    Returns:
        Affine: The transform of the output GeoTIFF file
    """
    for geotiff_str in geotiff_uri:
        # Check if the input is a path to a file or a rasterio DatasetReader object
        with rasterio.open(geotiff_str, "r") as geotiff:
            # Calculate the window to read the subset
            window = from_bounds(*bbox.bounds, transform=geotiff.transform)
            # Read the subset
            subset = geotiff.read(window=window)
            transform = geotiff.window_transform(window)

            # Define metadata for the new file
            out_meta = geotiff.meta.copy()
            out_meta.update(
                {
                    "driver": "GTiff",
                    "height": subset.shape[1],
                    "width": subset.shape[2],
                    "transform": transform,
                }
            )

            # Save the subset to a new GeoTIFF
            with rasterio.open(output_file, "w", **out_meta) as dest:
                dest.write(subset)
    # Return the transform of the output GeoTIFF
    with rasterio.open(output_file, "r+") as src:
        return src.transform, src.meta


def extract_boundingbox_into_matrix(geotiffs, bbox: Polygon):
    """
    Extracts a bounding box from a list of TIFF files or rasterio DatasetReader objects and returns the result as a matrix.
        geotiffs (list): List of (paths to the input TIFF files | rasterio DatasetReader objects)
        bbox (Polygon): A shapely Polygon object representing the bounding box to extract.
    Returns:
        np.array: The matrix containing the extracted bounding box.
        Affine: The transform of the output GeoTIFF file
    """
    # Open a MemoryFile to store the output GeoTIFF as rasterio only works with files
    with MemoryFile() as memfile:
        for geotiff in geotiffs:

            # Check if to get it from the cache or download it
            if type(geotiff) == str:
                geotiff = rasterio.open(geotiff, "r")

            # Calculate the window to read the subset
            window = from_bounds(*bbox.bounds, transform=geotiff.transform)
            # Read the subset
            subset = geotiff.read(window=window)
            transform = geotiff.window_transform(window)

            # Define metadata for the new file
            out_meta = geotiff.meta.copy()
            out_meta.update(
                {
                    "driver": "GTiff",
                    "height": subset.shape[1],
                    "width": subset.shape[2],
                    "transform": transform,
                }
            )

            # Save the subset to a new GeoTIFF
            with memfile.open(**out_meta) as dest:
                dest.write(subset)

        output_file = memfile.open()
        return output_file.read(), output_file.transform, output_file.meta


def tiff_to_png(input_file, output_file):
    """
    Converts a TIFF file to a PNG file.
    Args:
        input_file (str): Path to the input TIFF file.
        output_file (str): Path to the output PNG file.
    Returns:
        None
    """
    image = Image.open(input_file)
    image.save(output_file, "PNG")


def apply_colormap(input_file, color_map: dict, band=1):
    """
    Applies a color map to a band in a GeoTIFF file.

    Args:
        input_file (str): Path to the input GeoTIFF file.
        color_map (dict): A dictionary mapping pixel values to RGB colors.
        band (int): The band to which the color map should be applied (default is 1).
    Returns:
        None
    """
    with rasterio.open(input_file, "r+") as src:
        src.write_colormap(band, color_map)



def generate_colormap(ramp, num_steps=256):
    """
    Generates a continuous colormap dictionary from given ramp values.

    Args:
        ramp (list): List of (value, hex_color) pairs.
        num_steps (int): Number of discrete steps for interpolation.
    
    Returns:
        dict: A colormap mapping discrete values to RGB tuples.
    """
    # Extract known values and corresponding colors
    values = np.array([v[0] for v in ramp])
    colors = np.array([[(v[1] >> 16) & 255, (v[1] >> 8) & 255, v[1] & 255] for v in ramp], dtype=np.float32)
    
    # Interpolating each RGB channel
    interp_r = interp1d(values, colors[:, 0], kind='linear', fill_value="extrapolate")
    interp_g = interp1d(values, colors[:, 1], kind='linear', fill_value="extrapolate")
    interp_b = interp1d(values, colors[:, 2], kind='linear', fill_value="extrapolate")
    
    # Generate evenly spaced steps
    step_values = np.linspace(values.min(), values.max(), num_steps)
    
    # Apply interpolation to get colors at each step
    interpolated_colors = {
        i: (int(interp_r(v)), int(interp_g(v)), int(interp_b(v)))
        for i, v in enumerate(step_values)
    }
    
    return interpolated_colors