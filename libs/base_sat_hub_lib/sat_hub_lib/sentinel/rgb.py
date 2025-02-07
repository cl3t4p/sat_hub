from io import BytesIO
import numpy as np
import rasterio
from .basetype_sent import SentinelBaseType
from sentinelhub import SentinelHubRequest, DataCollection, MosaickingOrder


class RGB(SentinelBaseType):

    def __init__(self, args: dict):
        super().__init__(args)
        self.brightness = args.get("brightness")

    def write_geotiff(self, output_file: str = None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/output.tif"
        response = self._get_response()

        data_in_memory = BytesIO(response[0].content)
        with rasterio.open(data_in_memory) as src:
            full_data, meta = self._default_rasterio_preprocess(src)
            _range = full_data.shape[0]

            with rasterio.open(output_file, "w", **meta) as dst:
                for i in range(1, _range + 1):
                    band_matrix = full_data[i - 1]

                    band_matrix = self.__brighten_band(band_matrix)

                    dst.write(band_matrix, i)

    def extract_bandmatrix(self):
        response = self._get_response()
        data_in_memory = BytesIO(response[0].content)
        with rasterio.open(data_in_memory) as src:
            band_matrix, meta = self._default_rasterio_preprocess(src)
            # Apply factor factor=3.5 / 255 to band_matrix to brighten the image
            for i in range(0, band_matrix.shape[0]):
                band_matrix[i] = self.__brighten_band(band_matrix[i])
            return band_matrix

    def __brighten_band(self, band):
        """
        Brightens the given band by a fixed factor.

        Parameters:
        band (numpy.ndarray): The input band to be brightened.

        Returns:
        numpy.ndarray: The brightened band with values clipped between 0 and 255 and cast to uint8.
        """
        factor = self.brightness / 255
        return np.clip(band * factor * 255, 0, 255).astype(np.uint8)

    def _get_input_type(self):
        return [
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=("2020-06-01", "2020-06-30"),
                mosaicking_order=MosaickingOrder.LEAST_CC,  # MosaickingOrder.LEAST_CC is used to get the least cloudy image
            )
        ]

    def _get_evalscript(self):
        return """    
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04"]
                }],
                output: {
                    bands: 3
                }
            };
        }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
        """
