import rasterio
from rasterio.windows import from_bounds
from shapely import Polygon
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


COLOR_MAP = {
    10: (0, 100, 0),
    20: (255, 187, 34),
    30: (255, 255, 76),
    40: (240, 150, 255),
    50: (255, 0, 0),
    60: (180, 180, 180),
    70: (240, 240, 240),
    80: (0, 100, 200),
    90: (0, 150, 200),
    95: (0, 207, 117),
    100: (250, 230, 160),
}

def extract_boundingbox(tiff_files,output_file,bbox : Polygon):
    src_crs = 'WGS84'# CRS of the input bounding box

    for tiff_file in tiff_files:
        with rasterio.open(tiff_file) as src:
            # Calculate the window to read the subset
            window = from_bounds(*bbox.bounds, transform=src.transform)
            
            # Read the subset
            subset = src.read(window=window)
            transform = src.window_transform(window)
            
            # Define metadata for the new file
            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": subset.shape[1],
                "width": subset.shape[2],
                "transform": transform,
            })

            
            # Save the subset to a new GeoTIFF
            with rasterio.open(output_file, "w", **out_meta) as dest:
                dest.write(subset)
        print(f"Processed: {tiff_file}")


# Trasform to png using the COLOR_MAP
def trasform_geotiff_to_png(input_tiff,output_png):
    values, colors = zip(*COLOR_MAP.items())
    cmap = ListedColormap([tuple(c / 255.0 for c in color) for color in colors])

    with rasterio.open(input_tiff) as src:
        # Read the first band (assuming a single-band GeoTIFF)
        data = src.read(1)
        
        # Replace no-data values with NaN for transparency (if necessary)
        nodata = src.nodata
        if nodata is not None:
            data = np.where(data == nodata, np.nan, data)

    # Plot the data with the colormap and save as PNG
    plt.figure(figsize=(10, 10))
    plt.imshow(data, cmap=cmap, vmin=min(values), vmax=max(values))
    plt.colorbar(label="Land Cover Classes")
    plt.axis('off')  # Turn off axis for cleaner output
    plt.savefig(output_png, bbox_inches='tight', pad_inches=0, dpi=300)
    plt.close()

    print(f"PNG saved to {output_png}")
