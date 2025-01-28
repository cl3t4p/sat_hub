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
from scipy import signal as signal
from enum import Enum
import utils.geotiff.geotiff_lib as geotiff_lib

import time




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

    
    def write_geotiff(self,output_file=None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/output.tif"
        self.log.info("Processing ESA World Cover")
        # Get the tiles that intersect with the bounding box
        tile_names = self._get_tile_names()
        prefix = self._get_versionprefix()
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
        """
        Extracts a band matrix from GeoTIFF files.
        This method retrieves GeoTIFF files either from an S3 bucket or a local cache,
        transforms them into a matrix, and returns the resulting matrix. It also sets
        the GeoTIFF transformation and metadata attributes.
        Returns:
            numpy.ndarray: The extracted band matrix. Remember that this is a 3D array with shape (bands, rows, columns).
        Raises:
            Exception: If there is an error during the extraction process.
        """
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

        target_value = esamapcode.code
        
        # Get the matrix from the product
        matrix = self.product.extract_bandmatrix()[0]
        self.log.info("Starting percentage matrix calculation")
        
        
        # Create a circular kernel
        start_time = time.time()
        radius = self.meter_radius
        y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
        circular_kernel = (x**2 + y**2 <= radius**2).astype(float)
        
        self.log.info(f"Circular kernel creation time: {time.time() - start_time} seconds")
        
        start_time = time.time()
        target_matrix = (matrix == target_value).astype(float)
        self.log.info(f"Binary matrix creation time: {time.time() - start_time:.4f} seconds")

        # Convolve the target matrix with the kernel using FFT
        start_time = time.time()
        target_counts = signal.fftconvolve(target_matrix, circular_kernel, mode="same")
        self.log.info(f"Target counts FFT convolution time: {time.time() - start_time:.4f} seconds")

        # Convolve to count total valid cells using FFT
        start_time = time.time()
        total_cells = signal.fftconvolve(np.ones_like(matrix, dtype=float), circular_kernel, mode="same")
        self.log.info(f"Total cells FFT convolution time: {time.time() - start_time:.4f} seconds")




        # Calculate percentage of target_value around each pixel
        start_time = time.time()
        percentageMatrix_non_c_lib = (
            np.divide(
            target_counts,
            total_cells,
            out=np.zeros_like(target_counts),
            where=total_cells != 0,
            )
            * 100
        )
        self.log.info(f"Percentage matrix calculation time (non C++ library): {time.time() - start_time} seconds")


        """         
        start_time = time.time()
        target_matrix_list = target_matrix.tolist()
        circular_kernel_list = circular_kernel.tolist()
        percentageMatrix_c_lib = sat_img_lib.binary_convolve(target_matrix_list, circular_kernel_list)
        # Convert the list to a numpy array
        percentageMatrix_c_lib = np.array(percentageMatrix_c_lib)
        self.log.info(f"Percentage matrix calculation time (C library): {time.time() - start_time} seconds")

        # Check if the results are equal
        if np.array_equal(percentageMatrix_non_c_lib, percentageMatrix_c_lib):
            self.log.info("The results from both methods are equal.")
        else:
            self.log.warning("The results from both methods are NOT equal.")
        self.log.info("Percentage matrix calculated
         """
        return percentageMatrix_non_c_lib
    