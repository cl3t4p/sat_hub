import numpy as np
import rasterio
from scipy import signal
from sat_hub_lib.baseproducts import BaseSatType, BaseProduct


class GProx(BaseProduct):

    def __init__(self, product: BaseSatType, config, value_to_map: int):
        super().__init__(config)
        self.meter_radius = config["meter_radius"]
        self.product = product
        self.matrix = None
        self.value_to_map = value_to_map

    def write_geotiff(self, output_file: str = None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/gprox.tif"

        matrix = self.extract_bandmatrix()
        self.log.info("Writing matrix to GeoTIFF at " + output_file)
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
        Calculate the percentage of a target value around each pixel in a matrix using a circular kernel.
        This method performs the following steps:
        1. Extracts the matrix from the product.
        2. Creates a circular kernel based on the specified meter radius.
        3. Generates a binary matrix where the target value is marked.
        4. Convolves the binary matrix with the circular kernel using FFT to count target values.
        5. Convolves a matrix of ones with the circular kernel using FFT to count total valid cells.
        6. Calculates the percentage of the target value around each pixel.
        Returns:
            np.ndarray: A matrix representing the percentage of the target value around each pixel.
        """

        target_value = self.value_to_map

        # Get the matrix from the self.product
        matrix = self.product.extract_bandmatrix()[0]
        self.log.info("Starting percentage matrix calculation")

        # Create a circular kernel with increasing values outward (normalized to [0,1])
        radius = self.meter_radius / self.product.resolution
        y, x = np.ogrid[-radius: radius + 1, -radius: radius + 1]
        distance_from_center = np.sqrt(x**2 + y**2)
        
        # Compute kernel values, ensuring they stay within [0,1] using formula: (r - d) / r
        circular_kernel = np.clip((radius - distance_from_center) / radius, 0, 1)

        target_matrix = (matrix == target_value).astype(float)

        # Convolve the target matrix with the kernel using FFT
        target_counts = signal.fftconvolve(target_matrix, circular_kernel, mode="same")

        # Convolve to count total valid cells using FFT
        total_cells = signal.fftconvolve(
            np.ones_like(matrix, dtype=float), circular_kernel, mode="same"
        )

        # Calculate percentage of target_value around each pixel
        percentageMatrix = (
            np.divide(
                target_counts,
                total_cells,
                out=np.zeros_like(target_counts),
                where=total_cells != 0,
            )
            * 100
        )
        self.log.info(f"Percentage matrix calculated with shape {percentageMatrix.shape}")
        return percentageMatrix