import botocore.client
from sat_product.geotiff.basetype_geotiff import BaseSat_GeoTiff
import boto3
import botocore
import json
from shapely.geometry import Polygon, Point
import os
import sat_hub_lib

class S3_EsaWorldCover(BaseSat_GeoTiff):
    
    bucket_name = "esa-worldcover"
    
    def __init__(self, config):
        super().__init__(config)
        self.s3_client = boto3.client('s3', region_name='eu-central-1',config=botocore.client.Config(signature_version=botocore.UNSIGNED))
        self.version = config["version"]
    
    
    def process(self):
        tiles = self.download_files()
        
        # Extract the box from the geotiff
        bounding_box = (self.NW_Long, self.SE_Lat, self.SE_Long, self.NW_Lat)
        input_paths = [f"{self.cache_folder}/{tile}" for tile in tiles]
        output_path = f"{self.cache_folder}/combined_output.tif"
        sat_hub_lib.combine_geotiffs_with_box(input_paths, bounding_box, output_path)
    
    
    
    def download_files(self) -> list:
        geojson_filename = f"{self.cache_folder}/esa_worldcover_grid.geojson"

        # Check if the geojson file exists otherwise download it
        if not os.path.exists(geojson_filename):
            # Download the geojson file
            self.s3_client.download_file(S3_EsaWorldCover.bucket_name, 'esa_worldcover_grid.geojson', geojson_filename)
            


        with open(geojson_filename, "r") as f:
            geo_data = json.load(f)
        
        tiles_names = self.get_tiles(geo_data)
        tiles_files = self.download_geotiff_files(tiles_names)

        return tiles_files
        
    
    def get_tiles(self,geojson):
        tiles = []

        for feature in geojson['features']:
            polygon = Polygon(feature['geometry']['coordinates'][0])
            if polygon.intersects(self.cord_bounding_box):
                tiles.append(feature['properties']['ll_tile'])
        return tiles
    
    def download_geotiff_files(self, tiles_names: list):
        tiles_files = []
        match self.version:
            case 1:
                prefix = 'v100/2020/map/ESA_WorldCover_10m_2020_v100_'
            case 2:
                prefix = 'v200/2021/map/ESA_WorldCover_10m_2021_v200_'
            case _:
                print("Invalid version for ESA WorldCover")
                exit()

        # If cache does not hit download the files
        for tile in tiles_names:
            print(f"Caching {tile}")

            key = f'{prefix}{tile}_Map.tif'
            local_filename = f"{self.cache_folder}/{key[14:]}"

            if not os.path.exists(local_filename):
                print("Cache miss")
                print(f"Downloading {key} to {local_filename}")
                self.s3_client.download_file(S3_EsaWorldCover.bucket_name, key, local_filename)
                print(f"Downloaded {key}")
            else:
                print(f"Cached hit {key}")
            tiles_files.append(local_filename)
        return tiles_files