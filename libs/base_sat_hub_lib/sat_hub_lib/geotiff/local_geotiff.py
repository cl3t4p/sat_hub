from pyproj import Transformer
import rasterio
from sat_hub_lib.geotiff.basetype_geotiff import BaseSat_GeoTiff

class Local_GeoTiff(BaseSat_GeoTiff):
    def __init__(self, config):
        super().__init__(config)
        self.input_file = config["input_file"]
        self.resolution = None

    def write_geotiff(self, output_file: str = None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/output.tif"

        self.output_file = output_file
        with rasterio.open(self.input_file) as src:
            data, meta = self.__default_rasterio_preprocess(src)
            _range = data.shape[0]

            with rasterio.open(output_file, "w", **meta) as dst:
                for i in range(1, _range + 1):
                    dst.write(data[i - 1], i)


    
    def extract_bandmatrix(self):
        with rasterio.open(self.input_file) as src:
            data, meta = self.__default_rasterio_preprocess(src)
            return data
    

    def __default_rasterio_preprocess(self, geotiff):
        self.resolution = 20
        return self._default_rasterio_preprocess(geotiff)