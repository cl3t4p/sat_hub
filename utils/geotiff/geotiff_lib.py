import rasterio
from rasterio.windows import from_bounds
from shapely import Polygon
from rasterio.io import MemoryFile
import os
from PIL import Image

# Set the environment variable to disable signing requests for public S3 buckets
os.environ["AWS_NO_SIGN_REQUEST"] = "YES"


def extract_boundingbox_into_tiff(geotiff_uri, output_file: str, bbox: Polygon,color_map = None):
    """
    Extracts a bounding box from a list of TIFF files or rasterio DatasetReader objects and saves the result to a new GeoTIFF file.
        tiff_files (list): List of (paths to the input TIFF files | list of s3 urls)
        output_file (str): Path to the output file where the extracted bounding box will be saved.
        bbox (Polygon): A shapely Polygon object representing the bounding box to extract.
    Returns:
        Affine: The transform of the output GeoTIFF file
    """
    color_map = None
    for geotiff_str in geotiff_uri:
        # Check if the input is a path to a file or a rasterio DatasetReader object
        with rasterio.open(geotiff_str, "r") as geotiff:
            # Get the colormap from the first file
            if color_map is None:
                color_map = geotiff.colormap(1)

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
    # Write the colormap
    with rasterio.open(output_file, "r+") as src:
        src.write_colormap(1, color_map)
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


def apply_colormap(input_file,color_map : dict,band = 1):
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