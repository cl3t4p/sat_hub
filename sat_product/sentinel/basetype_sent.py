from abc import ABC, abstractmethod
from sat_product.basesat import BaseSatType
from sentinelhub import SentinelHubRequest, MimeType, CRS, BBox, Geometry, SHConfig
from pyproj import Geod
import os
import tarfile
import shutil


class SentinelBaseType(BaseSatType):
    """
    BaseType is an abstract base class that provides a template for satellite data processing.
    Attributes:
        wgs84 (Geod): A Geod object for WGS84 ellipsoid.
    Methods:
        __init__(self, args: dict):
            Initializes the BaseType object with configuration and geographical parameters.
        get_request(self):
            Creates and returns a SentinelHubRequest object based on the initialized parameters.
        get_geo_cords(self):
            Returns the geographical coordinates of the bounding box as a list of points.
        get_outfolder(self, outfolder):
            Generates and returns the output folder path, replacing "*unix_time*" with the current timestamp.
        get_input_data(self) -> list:
            Abstract method to be implemented by subclasses to provide input data for the request.
        get_evalscript(self) -> str:
            Abstract method to be implemented by subclasses to provide the evaluation script for the request.
        process(self):
            Abstract method to be implemented by subclasses to process the data.
    """

    wgs84 = Geod(ellps="WGS84")

    def __init__(self, config: dict):
        # Initialize the base class with the configuration parameters
        super().__init__(config)
        
        # Auth configuration
        self.config = SHConfig()
        self.config.sh_client_id = config["client_id"]
        self.config.sh_client_secret = config["client_secret"]

        # Time interval
        self.timeIntervalStart = config["start_date"]
        self.timeIntervalEnd = config["end_date"]

        # Geographical parameters
        self.maxCloudCoverage = config["cloud_coverage"]
        pixel_value = config["pixel_value"]


        # Resolution calculation
        # The dimensions in meters of the area of interest are calculated.
        # The dimensions in pixels of the area of interest are calculated.
        # The resolution is calculated (dimensions in meters / dimensions in pixels).
        verticalSideMeter = SentinelBaseType.wgs84.inv(
            self.NW_Long, self.NW_Lat, self.NW_Long, self.SE_Lat
        )[2]
        horizontalSideMeter = SentinelBaseType.wgs84.inv(
            self.NW_Long, self.NW_Lat, self.SE_Long, self.NW_Lat
        )[2]
        self.longSide = max(verticalSideMeter, horizontalSideMeter)
        self.shortSide = min(verticalSideMeter, horizontalSideMeter)
        
        
        # The resolution is calculated based on the long side of the area of interest.
        # pixel_value is the value of the long side of the area of interest in pixels default 750.
        
        # The long side of the area is assigned a value of 750 pixels, and the short side adjusts to maintain proportions.
        # By changing the value of 750, the resolution of the image can be modified.
        # In the case of gprox and small areas, it is recommended to use a lower value to avoid long waiting times.
        #self.verticalSidePixel = verticalSideMeter * (pixel_value / longSide)
        #self.horizontalSidePixel = horizontalSideMeter * (pixel_value / longSide)
        
        #self.resolution = longSide / pixel_value
        
        self.resolution = 20

        # Calculate the number of pixels for the vertical and horizontal sides
        self.verticalSidePixel = verticalSideMeter / self.resolution
        self.horizontalSidePixel = horizontalSideMeter / self.resolution
        self.bbox = BBox(
            bbox=[self.NW_Long, self.SE_Lat, self.SE_Long, self.NW_Lat], crs=CRS.WGS84
        )


    def get_request(self) -> SentinelHubRequest:
        geometry = Geometry(
            geometry={"coordinates": [self.get_geo_cords()], "type": "Polygon"},
            crs=CRS.WGS84,
        )
        request = SentinelHubRequest(
            evalscript=self.get_evalscript(),
            data_folder=self.output_folder,
            input_data=self.get_input_type(),
            responses=self.get_response_type(),
            bbox=self.bbox,
            geometry=geometry,
            size=[self.horizontalSidePixel, self.verticalSidePixel],
            config=self.config,
        )
        return request

    def get_geo_cords(self):
        return [
            [self.NW_Long, self.SE_Lat],
            [self.NW_Long, self.NW_Lat],
            [self.SE_Long, self.NW_Lat],
            [self.SE_Long, self.SE_Lat],
            [self.NW_Long, self.SE_Lat],
        ]
        
    def get_response_type(self) -> list:
        return [
            SentinelHubRequest.output_response('default', MimeType.TIFF),
            SentinelHubRequest.output_response('default', MimeType.JPG),
        ]

    @abstractmethod
    def get_input_type(self) -> list:
        pass

    @abstractmethod
    def get_evalscript(self) -> str:
        pass

    @abstractmethod
    def process(self):
        pass

    @staticmethod
    def extractImagesFromTar(outputFolderPath : str):
        print("Extracting images...")
        
        for subdir in os.listdir(outputFolderPath):
            subdir_path = os.path.join(outputFolderPath, subdir)
            if os.path.isdir(subdir_path):
                if "response.tar" in os.listdir(subdir_path):
                    tarPath = os.path.join(subdir_path, "response.tar")
                    targetFolder = os.path.join(outputFolderPath, "extracted_contents")
                    if not os.path.exists(targetFolder):
                        os.makedirs(targetFolder)
                    with tarfile.open(tarPath, 'r') as tar:
                        tar.extractall(targetFolder)
                    # Rimuovere la tar
                    os.remove(tarPath)
                    
                    # Move the extracted contents to the target folder
                    for item in os.listdir(subdir_path):
                        s = os.path.join(subdir_path, item)
                        d = os.path.join(outputFolderPath, item)
                        shutil.move(s, d)
                    
                    # Remove the now empty extracted_contents folder
                    os.rmdir(subdir_path)

        print("Extraction completed")