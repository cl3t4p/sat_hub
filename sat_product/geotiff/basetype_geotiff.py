from sat_product.basesat import BaseSatType
import os

class BaseSat_GeoTiff(BaseSatType):
    
    def __init__(self, config):
        super().__init__(config)
        self.cache_folder = config["SETTINGS"]["CACHE_FOLDER"]
        
        # Check if the cache folder exists otherwise create it
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

        
    
    
    def process(self):
        return super().process()
    

    

    