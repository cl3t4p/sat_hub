import logging
import botocore.client
import rasterio
from sat_product.geotiff.basetype_geotiff import BaseSat_GeoTiff
import boto3
import botocore
import json
from shapely.geometry import Polygon
from utils.geotiff import simplecache
import numpy as np
from scipy import ndimage as ndimg
from enum import Enum
import utils.geotiff.geotiff_lib as geotiff_lib




class S3_EsaWorldCover(BaseSat_GeoTiff):
    """
    #### Documentation for the ESA World Cover product
    Version 1 [WorldCover_PUM_V1.0.pdf](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v100/2020/docs/WorldCover_PUM_V1.0.pdf)
    Version 2 [WorldCover_PUM_V2.0.pdf](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PUM_V2.0.pdf)
    """
    
    bucket_name = "esa-worldcover"
    
    def __init__(self, config):
        super().__init__(config)
        self.s3_client = boto3.client('s3', region_name='eu-central-1',config=botocore.client.Config(signature_version=botocore.UNSIGNED))
        self.version = config["version"]
        self.use_cache = not config["disable_cache"]
        self.s3cache = simplecache.S3Cache(config["SETTINGS"]["CACHE_FOLDER"], S3_EsaWorldCover.bucket_name, 'eu-central-1')
        self.geotiff_trasform = None

    
    def process(self):
        self.log.info("Processing ESA World Cover")
        # Get the tiles that intersect with the bounding box
        tile_names = self._get_tile_names()
        prefix = self._get_versionprefix()
        output_file = f"{self.get_outfolder()}/output.tif"
        

        geotiffs = []
        for tile in tile_names:
            key = f'{prefix}{tile}_Map.tif'
            
            self.log.info(f"Getting {key}")
            if not self.use_cache:
                geotiffs.append(f"s3://{S3_EsaWorldCover.bucket_name}/{key}")
            else:
                self.log.info(f"Using cache")
                local_filename = f"{self.cache_folder}/{key[14:]}"
                # If the file does not exist in the cache download it

                self.s3cache.get(key, local_filename)
                geotiffs.append(local_filename)
        
        self.log.info("Extracting bounding box")
        self.geotiff_trasform,self.geotiff_meta = geotiff_lib.extract_boundingbox_into_tiff(geotiffs, output_file, self.bounding_box)
        self.log.info("Bounding box extracted to " + output_file)
            
        
    def extract_bandmatrix(self):
        self.log.info("Extracting band matrix")
        tile_names = self._get_tile_names()
        prefix = self._get_versionprefix()
        
        geotiffs = []
        for tile in tile_names:
            key = f'{prefix}{tile}_Map.tif'
            
            if not self.use_cache:
                geotiffs.append(f"s3://{S3_EsaWorldCover.bucket_name}/{key}")
            else:
                local_filename = f"{self.cache_folder}/{key[14:]}"
                # If the file does not exist in the cache download it
                self.s3cache.get(key, local_filename)
                geotiffs.append(local_filename)
        
        # Trasform the geotiffs into a matrix
        
        matrix,self.geotiff_trasform,self.geotiff_meta =  geotiff_lib.extract_boundingbox_into_matrix(geotiffs, self.bounding_box)
        self.log.info("Band matrix extracted")
        return matrix
        
        
        

    def _get_gridgeojson(self):
        if not self.use_cache:
            # No cache, all in memory
            obj = self.s3_client.get_object(Bucket=S3_EsaWorldCover.bucket_name, Key='esa_worldcover_grid.geojson')
            return json.loads(obj['Body'].read().decode('utf-8'))
        else:
            geojson_filename = f"{self.cache_folder}/esa_worldcover_grid.geojson"
            self.s3cache.get('esa_worldcover_grid.geojson', geojson_filename)
            # Open the geojson file
            with open(geojson_filename, "r") as f:
                geo_data = json.load(f)
            
            return geo_data

    
    def _get_tile_names(self):
        geojson = self._get_gridgeojson()
        tiles = []
        for feature in geojson['features']:
            polygon = Polygon(feature['geometry']['coordinates'][0])
            if polygon.intersects(self.cord_bounding_box):
                tiles.append(feature['properties']['ll_tile'])
        return tiles
    
    
    

    def _get_versionprefix(self):
        match self.version:
            case 1:
                return 'v100/2020/map/ESA_WorldCover_10m_2020_v100_'
            case 2:
                return 'v200/2021/map/ESA_WorldCover_10m_2021_v200_'
            case _:
                print("Invalid version for ESA WorldCover")
                exit()
                

class ESAWC_MAPCODE(Enum):

    TREE_COVER = 10, (0, 100, 0)
    SHRUBLAND = 20, (255, 187, 34)
    GRASSLAND = 30, (255, 255, 76)
    CROPLAND = 40, (240, 150, 255)
    BUILTUP = 50, (250, 0, 0)
    BARE = 60, (180, 180, 180)
    SNOW_ICE = 70, (240, 240, 240)
    PERMANENT_WATER = 80, (0, 100, 200)
    HERBACEOUS_WETLAND = 90, (0, 150, 160)
    MANGROVE = 95, (0, 207, 117)
    MOSS_AND_LICHEN = 100, (250, 230, 160)
    UNCLASSIFIED = 0, (0, 0, 0)

    def __init__(self, code, color):
        self.code = code
        self.color = color

    @staticmethod
    def get_color(code):
        for item in ESAWC_MAPCODE:
            if item.code == code:
                return item.color
        return (0, 0, 0)

class S3_GProx():
    
    def __init__(self, s3_product : S3_EsaWorldCover,config):
        self.log = logging.getLogger(type(self).__name__)
        self.meter_radius = config["meter_radius"]
        self.product = s3_product
        
    def write_matrix_to_geotiff(self,matrix, product, output_file):
        """
        Writes a matrix to a GeoTIFF file.
        Args:
            matrix (np.array): The matrix to write to the GeoTIFF.
            product (BaseSat_GeoTiff): The product object used to extract the matrix.
            output_file (str): Path to the output GeoTIFF file.
        Returns:
            None
        """
        self.log.info("Writing matrix to GeoTIFF at " + output_file)
        with rasterio.open(output_file, "w", **product.geotiff_meta) as dst:
            dst.write(matrix.astype(rasterio.uint8), 1)
            dst.meta.update(
                {
                    "driver": "GTiff",
                    "height": matrix.shape[0],
                    "width": matrix.shape[1],
                    "transform": product.geotiff_trasform,
                    "count": 1,
                    "dtype": rasterio.uint8,
                }
            )
        # Create a green gradient colormap
        color_map = {i: (0, int(255 * (i / 100)), 0) for i in range(101)}

        # Write the colormap
        with rasterio.open(output_file, "r+") as src:
            src.write_colormap(1, color_map)
        self.log.info("Matrix written to GeoTIFF at " + output_file)
            
        
        
    def get_percentage_convolution_matrix(
        self,esamapcode=ESAWC_MAPCODE.TREE_COVER
    )->np.array:
        """
        Extracts a percentage matrix indicating the proportion of a specified target value 
        within a circular neighborhood around each pixel in the input matrix.
        Args:
            product: An object that contains the matrix data and provides the method `extract_matrix()`.
            radius (int): The radius of the circular neighborhood to consider around each pixel.
            esamapcode (ESAWC_MAPCODE, optional): The target value to look for in the matrix. 
                Defaults to ESAWC_MAPCODE.TREE_COVER.
        Returns:
            np.array: A matrix of the same shape as the input matrix, where each element 
            represents the percentage of the target value within the specified radius around 
            the corresponding pixel.
        """
        self.log.info("Calculating percentage matrix")
        target_value = esamapcode.code
        
        # Get the matrix from the product
        matrix = self.product.extract_bandmatrix()[0]
        
        # Create a circular kernel
        radius = self.meter_radius
        y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
        
        circular_kernel = (x**2 + y**2 <= radius**2).astype(float)

        # Create a binary matrix where 1 indicates the target value
        target_matrix = (matrix == target_value).astype(float)

        # Convolve the target matrix with the kernel to count target_value occurrences
        target_counts = ndimg.convolve(target_matrix, circular_kernel, mode="constant", cval=0)

        # Convolve to count total valid cells
        total_cells = ndimg.convolve(np.ones_like(matrix, dtype=float), circular_kernel, mode="constant", cval=0)

        # Calculate percentage of target_value around each pixel
        percentageMatrix = (
            np.divide(
                target_counts,
                total_cells,
                out=np.zeros_like(target_counts),
                where=total_cells != 0,
            )
            * 100
        )
        self.log.info("Percentage matrix calculated")
        return percentageMatrix