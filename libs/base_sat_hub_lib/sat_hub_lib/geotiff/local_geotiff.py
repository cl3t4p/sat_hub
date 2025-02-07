import rasterio
from sat_hub_lib.geotiff.basetype_geotiff import BaseSat_GeoTiff
from sat_hub_lib.extension import IsMappable

class Local_GeoTiff(BaseSat_GeoTiff,IsMappable):
    def __init__(self, config):
        super().__init__(config)
        self.input_file = config["input_file"]
        self.resolution = None

    def get_default_value_map(self):
        return {1: 1}
    
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
        self.resolution = self.geotiff_resolution_fixed(geotiff)
        return self._default_rasterio_preprocess(geotiff)
    

    def geotiff_resolution_fixed(self,geotiff, factor=111111):
        """
        Calculate the fixed resolution of a GeoTIFF image in meters.

        Args:
            geotiff (rasterio.io.DatasetReader): The GeoTIFF image to calculate the resolution for.
            factor (float, optional): The conversion factor from degrees to meters. Defaults to 111111.

        Returns:
            tuple: A tuple containing the pixel width and height in meters, rounded to one decimal place.
        """
        res_deg = (abs(geotiff.transform.a), abs(geotiff.transform.e))
        pixel_width_m = res_deg[0] * factor
        pixel_height_m = res_deg[1] * factor
        return round(pixel_width_m, 1), round(pixel_height_m, 1)