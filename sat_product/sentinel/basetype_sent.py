from abc import abstractmethod
from io import BytesIO

import rasterio
from sat_product.basesat import BaseSatType
from sentinelhub import SentinelHubRequest, MimeType, CRS, Geometry, SHConfig
import sentinelhub


class SentinelBaseType(BaseSatType):
    
    max_resolution_allowed = 2500

    def __init__(self, config: dict):
        # Initialize the base class with the configuration parameters
        super().__init__(config)
        
        # Auth configuration for Sentinel Hub
        self.config = SHConfig()
        self.config.sh_client_id = config["client_id"]
        self.config.sh_client_secret = config["client_secret"]

        # Time interval
        self.timeIntervalStart = config["start_date"]
        self.timeIntervalEnd = config["end_date"]
        
        # Geographical parameters
        self.cloud_coverage = config["cloud_coverage"]
        
        
        self.sat_hub_bounding_box = sentinelhub.BBox(bbox=self.bounding_box.bounds, crs=CRS.WGS84)
                
        # Resolution stuff as Sentinel Hub poses a limit on the width and height of the bounding box (2500)
        if "resolution" in config and config["resolution"] is not None:
            self.resolution = config["resolution"]
            self.sat_hub_bounding_box_size = sentinelhub.bbox_to_dimensions(self.sat_hub_bounding_box, self.resolution)
            if self.sat_hub_bounding_box_size[0] > self.max_resolution_allowed or self.sat_hub_bounding_box_size[1] > self.max_resolution_allowed:
                self.log.warning(f"Resolution {self.resolution} exceeds the maximum allowed size of {self.max_resolution_allowed}. Calculating new resolution based on the bounding box.")
                self.sat_hub_bounding_box_size = self.calculate_size_from_bbox(self.bounding_box.bounds)
                self.log.warning(f"New resolution: {self.sat_hub_bounding_box_size}")
        else:
            # If resolution is not provided, calculate it based on the bounding box and the maximum allowed size
            self.sat_hub_bounding_box_size = self.calculate_size_from_bbox(self.bounding_box.bounds)
        
        print("\n Resolution: ", self.sat_hub_bounding_box_size)
            
        

        # Calculate the bounding box size based on the resolution
        #self.sat_hub_bounding_box_size = self.calculate_size_from_bbox(self.bounding_box.bounds)
        
        

    def __get_response(self):
        self.log.info("Getting data from Sentinel Hub")
        request = self.get_request()
        response = request.get_data(save_data=False,show_progress=True,decode_data=False)
        return response

    def write_geotiff(self, output_file: str = None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/output.tif"
        response = self.__get_response()
        
        data_in_memory = BytesIO(response[0].content )
        with rasterio.open(data_in_memory) as src:
            data, meta = self.__default_rasterio_preprocess(src)
            _range = data.shape[0]
            
            with rasterio.open(output_file, "w", **meta) as dst:
                for i in range(1,_range+1):
                    dst.write(src.read(i),i)
    
    
    def extract_bandmatrix(self):
        response = self.__get_response()
        
        data_in_memory = BytesIO(response[0].content)
        with rasterio.open(data_in_memory) as src:
            data, meta = self.__default_rasterio_preprocess(src)
            return data


    def __default_rasterio_preprocess(self, geotiff):
            self.geotiff_meta = geotiff.meta
            self.geotiff_trasform = geotiff.transform
            
            data = geotiff.read()
            out_meta = geotiff.meta.copy()
            out_meta.update(
                height= data.shape[1],
                width= data.shape[2],
                driver="GTiff",
                count=data.shape[0],
                dtype=rasterio.uint8
            )
            return data, out_meta



    def get_request(self) -> SentinelHubRequest:
        geometry = Geometry(
            geometry={"coordinates": [self.bounding_box], "type": "Polygon"},
            crs=CRS.WGS84,
        )
        request = SentinelHubRequest(
            evalscript=self._get_evalscript(),
            data_folder=self.get_outfolder(),
            input_data=self._get_input_type(),
            responses=self._get_response_type(),
            size=self.sat_hub_bounding_box_size,
            bbox=self.sat_hub_bounding_box,
            config=self.config,
        )
        return request



    def calculate_size_from_bbox(self,bounding_box):
        """
        Calculate the size (in pixels) from a given bounding box while ensuring it does not exceed the maximum limit.
        bounding_box: List of [min_longitude, min_latitude, max_longitude, max_latitude]
        Returns: Tuple (horizontal_size, vertical_size)
        """
        min_lon, min_lat, max_lon, max_lat = bounding_box
        
        # Calculate the horizontal and vertical distances in degrees
        horizontal_distance = max_lon - min_lon
        vertical_distance = max_lat - min_lat
        
        # Define the maximum allowed size (2500)
        max_size = self.max_resolution_allowed
        
        
        
        # Calculate the aspect ratio (width/height)
        aspect_ratio = horizontal_distance / vertical_distance
        
        
        
        # Initialize horizontal and vertical sizes based on aspect ratio
        if aspect_ratio >= 1:
            horizontal_size = max_size
            vertical_size = int(max_size / aspect_ratio)
        else:
            vertical_size = max_size
            horizontal_size = int(max_size * aspect_ratio)
        
        # If either dimension exceeds max_size, scale the other dimension
        if horizontal_size > max_size:
            horizontal_size = max_size
            vertical_size = int(horizontal_size / aspect_ratio)
            
        if vertical_size > max_size:
            vertical_size = max_size
            horizontal_size = int(vertical_size * aspect_ratio)
        
        return horizontal_size, vertical_size
    
    def _get_response_type(self) -> list:
        return [
            SentinelHubRequest.output_response('default', MimeType.TIFF),
            #SentinelHubRequest.output_response('default', MimeType.JPG),
        ]
    

    @abstractmethod
    def _get_input_type(self) -> list:
        pass

    @abstractmethod
    def _get_evalscript(self) -> str:
        pass