from abc import ABC, abstractmethod
import numpy as np
import rasterio
from scipy import signal
from sat_hub_lib.baseproducts import BaseSatType, BaseProduct

class IsMappable(ABC):

    @abstractmethod
    def get_default_value_map(self):
        raise NotImplementedError
    

class GProx(BaseProduct):

    def __init__(self, product: BaseSatType, config):
        super().__init__(config)
        self.meter_radius = config["meter_radius"]
        self.value_map = config.get("value_map", None)
        self.product = product
        self.matrix = None
        
        if self.value_map is None:
            if self.product.get_default_value_map is not None:
                self.value_map = self.product.get_default_value_map()
            else:
                raise ValueError(f"Value map {self.product.__class__.__name__} is not provided and the product does not have a default value map.")

    def write_geotiff(self, output_file: str = None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/gprox.tif"

        matrix = self.extract_bandmatrix()
        with rasterio.open(output_file, "w", **self.product.geotiff_meta) as dst:
            dst.write(matrix.astype(rasterio.uint8), 1)
            dst.meta.update(
                {
                    "driver": "GTiff",
                    "height": matrix.shape[0],
                    "width": matrix.shape[1],
                    "transform": self.product.geotiff_trasform,
                    "count": 1,
                    "dtype": rasterio.uint8,
                }
            )
        # Create a green gradient colormap
        color_map = {i: (0, i, 0, 255) for i in range(256)}

        # Write the colormap
        with rasterio.open(output_file, "r+") as src:
            src.write_colormap(1, color_map)
        self.log.info("Matrix written to GeoTIFF at " + output_file)

    def extract_bandmatrix(self):
        """
        Calculate the percentage of a target value around each pixel in a matrix using a circular (or rather, physically circular)
        kernel that accounts for anisotropic pixel resolution.
        Steps:
        1. Extracts the matrix from the product.
        2. Creates a circular kernel based on the specified meter radius.
            - If the product resolution is an integer, a uniform resolution is assumed.
            - If it is a tuple (res_x, res_y), the physical distance for each kernel cell is computed as 
            sqrt((x*res_x)**2 + (y*res_y)**2).
        3. Generates a binary matrix where the target value is marked.
        4. Convolves the binary matrix with the circular kernel using FFT to count target values.
        5. Convolves a matrix of ones with the circular kernel using FFT to count total valid cells.
        6. Calculates the percentage of the target value around each pixel.
        Returns:
            np.ndarray: A matrix representing the percentage of the target value around each pixel.
        """

        
        

        # Get the matrix from the product
        matrix = self.product.extract_bandmatrix()[0]
        self.log.info("Starting percentage matrix calculation")


        # Create the kernel based on resolution type.
        if isinstance(self.product.resolution, int):

            # Create a circular kernel with increasing values outward (normalized to [0,1])
            radius = self.meter_radius / self.product.resolution
            y, x = np.ogrid[-radius: radius + 1, -radius: radius + 1]
            distance_from_center = np.sqrt(x**2 + y**2)
            
            # Compute kernel values, ensuring they stay within [0,1] using formula: (r - d) / r
            circular_kernel = np.clip((radius - distance_from_center) / radius, 0, 1)

        elif isinstance(self.product.resolution, tuple):
            # Unpack the resolution for width and height (e.g., (res_x, res_y) in meters per pixel or degrees converted via a factor)
            res_x, res_y = self.product.resolution
            # Calculate how many pixels in each direction correspond to the meter radius.
            radius_x = self.meter_radius / res_x
            radius_y = self.meter_radius / res_y
            # Create grid indices for y and x:
            y, x = np.ogrid[-radius_y: radius_y + 1, -radius_x: radius_x + 1]
            # Compute the physical distance for each cell:
            # Note: x and y here are in pixel offsets; multiply by the corresponding resolution.
            distance = np.sqrt((x * res_x)**2 + (y * res_y)**2)
            # Create the kernel: cells within the meter_radius get a value that linearly decays from 1 (at center) to 0 at the edge.
            circular_kernel = np.clip((self.meter_radius - distance) / self.meter_radius, 0, 1)
        else:
            raise ValueError("Unsupported resolution type")


        
        # Get the target value map
        target_value = self.value_map
        
        if isinstance(target_value, dict):
            # Create a matrix with the target values mapped to integers.
            target_matrix = np.zeros_like(matrix, dtype=float)
            for value, target in target_value.items():
                target_matrix[matrix == value] = target
        elif isinstance(target_value, int):
            # Create a binary matrix: 1 where the matrix equals target_value, 0 otherwise.
            target_value = self.value_to_map
            target_matrix = (matrix == target_value).astype(float)
            



        # Convolve the target matrix with the kernel using FFT to count target occurrences.
        target_counts = signal.fftconvolve(target_matrix, circular_kernel, mode="same")

        # Convolve a ones matrix with the kernel to count total valid cells per pixel neighborhood.
        total_cells = signal.fftconvolve(np.ones_like(matrix, dtype=float), circular_kernel, mode="same")

        # Calculate percentage (with safe division).
        percentageMatrix = (np.divide(
                                target_counts,
                                total_cells,
                                out=np.zeros_like(target_counts),
                                where=total_cells != 0
                            ) * 100)
        self.log.info(f"Percentage matrix calculated with shape {percentageMatrix.shape}")
        return percentageMatrix