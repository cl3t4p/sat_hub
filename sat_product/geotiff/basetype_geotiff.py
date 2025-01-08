from sat_product.basesat import BaseSatType

class BaseSat_GeoTiff(BaseSatType):
    
    def __init__(self, config):
        super().__init__(config)
        self.cache_folder = config["SETTINGS"]["CACHE_FOLDER"]
        
    
    
    def process(self):
        return super().process()
    

    
    
    