from sat_product.geotiff.basetype_geotiff import BaseSat_GeoTiff
import boto3

class S3_EsaWorldCover(BaseSat_GeoTiff):
    
    
    
    def __init__(self, config):
        super().__init__(config)
        
    
    
    def process(self):
        return super().process()
    
    
    def get_geotiff_links(self) -> list:
        s3 = boto3.client('s3')
        s3.download_file('esa-worldcover', 'esa_worldcover_grid.geojson', f"{self.cache_folder}/esa_worldcover_grid.geojson")