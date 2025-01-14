from sat_product.basesat import BaseSatType
import os
from shapely.geometry import Polygon, Point, box
class BaseSat_GeoTiff(BaseSatType):
    
    def __init__(self, config):
        super().__init__(config)
        self.cache_folder = config["SETTINGS"]["CACHE_FOLDER"]
        
        # Check if the cache folder exists otherwise create it
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

        #Bounding box
        self.cord_bounding_box = box(self.NW_Long, self.SE_Lat, self.SE_Long, self.NW_Lat)
    
    
    def process(self):
        return super().process()
    
