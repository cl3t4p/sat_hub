import botocore.client
from sat_hub_lib.geotiff.basetype_geotiff import BaseSat_GeoTiff
import boto3
import botocore
import json
from shapely.geometry import Polygon, box
from sat_hub_lib.utils import simplecache
from scipy import signal as signal
from enum import Enum
import os
import sat_hub_lib.utils.geotiff_lib as geotiff_lib
from sat_hub_lib.extension import IsMappable


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
    def get_color_map():
        color_map = {}
        for item in ESAWC_MAPCODE:
            color_map[item.code] = item.color
        return color_map

    @staticmethod
    def get_color(code):
        for item in ESAWC_MAPCODE:
            if item.code == code:
                return item.color
        return (0, 0, 0)


class S3_EsaWorldCover(BaseSat_GeoTiff,IsMappable):
    """
    #### Documentation for the ESA World Cover product
    Version 1 [WorldCover_PUM_V1.0.pdf](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v100/2020/docs/WorldCover_PUM_V1.0.pdf)
    Version 2 [WorldCover_PUM_V2.0.pdf](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PUM_V2.0.pdf)
    """

    bucket_name = "esa-worldcover"

    def __init__(self, config):
        super().__init__(config)
        self.cache_folder = config["cache_folder"]

        # Default resolution for the ESA World Cover
        self.resolution = 20

        # Check if the cache folder exists otherwise create it
        self.cache_folder = f"{self.cache_folder}/{self.__class__.__name__}"
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

        self.s3_client = boto3.client(
            "s3",
            region_name="eu-central-1",
            config=botocore.client.Config(signature_version=botocore.UNSIGNED),
        )
        self.version = config["version"]
        self.use_cache = not config["disable_cache"]
        self.s3cache = simplecache.S3Cache(
            self.cache_folder,
            S3_EsaWorldCover.bucket_name,
            "eu-central-1",
        )
        
    def get_default_value_map(self):
        return {ESAWC_MAPCODE.TREE_COVER.code: 1, ESAWC_MAPCODE.GRASSLAND.code: 0.8}

    def write_geotiff(self, output_file=None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/output.tif"
        self.log.info("Processing ESA World Cover")
        # Get the tiles that intersect with the bounding box
        tile_names = self._get_tile_names()
        prefix = self._get_versionprefix()
        geotiffs = []
        for tile in tile_names:
            key = f"{prefix}{tile}_Map.tif"

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
        self.geotiff_trasform, self.geotiff_meta = (
            geotiff_lib.extract_boundingbox_into_tiff(
                geotiffs, output_file, self.bounding_box
            )
        )
        geotiff_lib.apply_colormap(output_file, ESAWC_MAPCODE.get_color_map())
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
            key = f"{prefix}{tile}_Map.tif"

            if not self.use_cache:
                geotiffs.append(f"s3://{S3_EsaWorldCover.bucket_name}/{key}")
            else:
                local_filename = f"{self.cache_folder}/{key[14:]}"
                # If the file does not exist in the cache download it
                self.s3cache.get(key, local_filename)
                geotiffs.append(local_filename)

        # Trasform the geotiffs into a matrix
        matrix, self.geotiff_trasform, self.geotiff_meta = (
            geotiff_lib.extract_boundingbox_into_matrix(geotiffs, self.bounding_box)
        )
        self.log.info("Band matrix extracted")
        return matrix

    def _get_gridgeojson(self):
        if not self.use_cache:
            # No cache, all in memory
            obj = self.s3_client.get_object(
                Bucket=S3_EsaWorldCover.bucket_name, Key="esa_worldcover_grid.geojson"
            )
            return json.loads(obj["Body"].read().decode("utf-8"))
        else:
            geojson_filename = f"{self.cache_folder}/esa_worldcover_grid.geojson"
            self.s3cache.get("esa_worldcover_grid.geojson", geojson_filename)
            # Open the geojson file
            with open(geojson_filename, "r") as f:
                geo_data = json.load(f)

            return geo_data

    def _get_tile_names(self):
        geojson = self._get_gridgeojson()
        tiles = []
        for feature in geojson["features"]:
            polygon = Polygon(feature["geometry"]["coordinates"][0])
            cord_bounding_box =  box(
                self.NW_Long, self.SE_Lat, self.SE_Long, self.NW_Lat
            )
            if polygon.intersects(cord_bounding_box):
                tiles.append(feature["properties"]["ll_tile"])
        return tiles

    def _get_versionprefix(self):
        match self.version:
            case 1:
                return "v100/2020/map/ESA_WorldCover_10m_2020_v100_"
            case 2:
                return "v200/2021/map/ESA_WorldCover_10m_2021_v200_"
            case _:
                self.log.error("ESA World Cover version not supported please use 1 or 2")
                exit()
