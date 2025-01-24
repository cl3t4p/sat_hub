from abc import abstractmethod
from shapely import Polygon
from sat_product.basesat import BaseSatType
import os
from shapely.geometry import box

class BaseSat_GeoTiff(BaseSatType):
    def __init__(self, config):
        super().__init__(config)
        self.cache_folder = config["SETTINGS"]["CACHE_FOLDER"]

        # Check if the cache folder exists otherwise create it
        self.cache_folder = f"{self.cache_folder}/{self.__class__.__name__}"
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

        #Bounding box
        self.cord_bounding_box = box(self.NW_Long, self.SE_Lat, self.SE_Long, self.NW_Lat)
    
    
    def write_geotiff(self):
        return super().write_geotiff()
    
    @abstractmethod
    def extract_bandmatrix(self):
        pass
    

