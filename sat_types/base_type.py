from abc import ABC, abstractmethod
from sentinelhub import SentinelHubRequest, MimeType, CRS, BBox, Geometry, SHConfig
from pyproj import Geod
import datetime


class BaseType(ABC):
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

    def __init__(self, args: dict):
        # Auth configuration
        self.config = SHConfig()
        self.config.sh_client_id = args["client_id"]
        self.config.sh_client_secret = args["client_secret"]

        # Geographical parameters
        self.timeIntervalStart = args["start_date"]
        self.timeIntervalEnd = args["end_date"]
        self.NW_Long = args["point1"][1]
        self.NW_Lat = args["point1"][0]
        self.SE_Long = args["point2"][1]
        self.SE_Lat = args["point2"][0]
        self.maxCloudCoverage = args["cloud_coverage"]
        pixel_value = args["pixel_value"]

        # Output folder
        self.outputFolder = self.get_outfolder(args["output"])

        # Resolution calculation
        # The dimensions in meters of the area of interest are calculated.
        # The dimensions in pixels of the area of interest are calculated.
        # The resolution is calculated (dimensions in meters / dimensions in pixels).
        verticalSideMeter = BaseType.wgs84.inv(
            self.NW_Long, self.NW_Lat, self.NW_Long, self.SE_Lat
        )[2]
        horizontalSideMeter = BaseType.wgs84.inv(
            self.NW_Long, self.NW_Lat, self.SE_Long, self.NW_Lat
        )[2]
        longSide = max(verticalSideMeter, horizontalSideMeter)
        shortSide = min(verticalSideMeter, horizontalSideMeter)
        
        
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


    def get_request(self) -> SentinelHubRequest:
        bbox = BBox(
            bbox=[self.NW_Long, self.SE_Lat, self.SE_Long, self.NW_Lat], crs=CRS.WGS84
        )
        geometry = Geometry(
            geometry={"coordinates": [self.get_geo_cords()], "type": "Polygon"},
            crs=CRS.WGS84,
        )
        request = SentinelHubRequest(
            evalscript=self.get_evalscript(),
            data_folder=self.outputFolder,
            input_data=self.get_input_data(),
            responses=[
                SentinelHubRequest.output_response("default", MimeType.TIFF),
                SentinelHubRequest.output_response("default", MimeType.JPG),
            ],
            bbox=bbox,
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

    def get_outfolder(self, outfolder):
        """
        Generates an output folder path based on the provided template or class name.

        Args:
            outfolder (str): The template for the output folder path. If it contains
                             the placeholder "*date_time*", it will be replaced with
                             the current date and time in the format "YYYY-MM-DD_HH-MM-SS".
                             If None, the output folder path will be generated using
                             the class name and the current date and time.

        Returns:
            str: The generated output folder path.
        """
        time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if outfolder is not None:
            return outfolder.replace("*date_time*", time)
        else:
            className = self.__class__.__name__
            return f"{className}_{time}"

    @abstractmethod
    def get_input_data(self) -> list:
        pass

    @abstractmethod
    def get_evalscript(self) -> str:
        pass

    @abstractmethod
    def process(self):
        pass
