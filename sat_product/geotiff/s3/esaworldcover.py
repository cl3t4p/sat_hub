import botocore.client
from sat_product.geotiff.basetype_geotiff import BaseSat_GeoTiff
import boto3
import botocore
import json
import hashlib
import os

class S3_EsaWorldCover(BaseSat_GeoTiff):
    
    
    
    def __init__(self, config):
        super().__init__(config)
        self.s3_client = boto3.client('s3', region_name='eu-central-1',config=botocore.client.Config(signature_version=botocore.UNSIGNED))
        
    
    
    def process(self):
        self.get_geotiff_links()
    
    
    def get_geotiff_links(self) -> list:
        geojson_filename = f"{self.cache_folder}/esa_worldcover_grid.geojson"

        # Check if the geojson file exists otherwise download it
        if not os.path.exists(geojson_filename):
            # Download the geojson file
            self.s3_client.download_file('esa-worldcover', 'esa_worldcover_grid.geojson', geojson_filename)
            with open(geojson_filename, "r") as f:
                geo_data = json.load(f)
        else:
            with open(geojson_filename, "r") as f:
                geo_data = json.load(f)
            
            # Check the e_tag of the file md5 hash
            e_tag = self.s3_client.head_object(Bucket='esa-worldcover', Key='esa_worldcover_grid.geojson').get('ETag')[1:-1]
            
            # Convert geo_data to JSON string and then to bytes
            geo_data_bytes = json.dumps(geo_data).encode('utf-8')
            hashgeo = hashlib.md5(geo_data_bytes).hexdigest()
            
            if e_tag != hashgeo:
                print("File has been updated")
                # Download the geojson file
                self.s3_client.download_file('esa-worldcover', 'esa_worldcover_grid.geojson', geojson_filename)
        
