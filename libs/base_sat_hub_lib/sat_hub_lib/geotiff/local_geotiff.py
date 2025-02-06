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
    

    def geotiff_resolution_fixed(self,geotiff_path, factor=111111):
        """
        Reads the pixel resolution (in degrees) from a GeoTIFF and converts both
        east-west and north-south directions to meters using the same conversion factor.
        
        This ignores the cosine(latitude) adjustment for longitude and is only appropriate
        if you expect an isotropic resolution (e.g. if the file is already designed for 18 m cells).
        
        Parameters:
            geotiff_path (str): Path to the GeoTIFF file.
            factor (float): Conversion factor for one degree to meters (default 111111).
        
        Returns:
            tuple: (pixel_width_m, pixel_height_m)
        """
        with rasterio.open(geotiff_path) as src:
            res_deg = (abs(src.transform.a), abs(src.transform.e))
            pixel_width_m = res_deg[0] * factor
            pixel_height_m = res_deg[1] * factor
            return round(pixel_width_m, 1), round(pixel_height_m, 1)