from abc import abstractmethod
from io import BytesIO

import rasterio
from sat_product.basesat import BaseSatType
from sentinelhub import SentinelHubRequest, MimeType, CRS, SHConfig
import sentinelhub.geo_utils as geo_utils
import sentinelhub
import math


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
                
        self.resolution = config.get("resolution",None)
        if self.resolution is not None:
            self.sat_hub_bounding_box_size= sentinelhub.bbox_to_dimensions(self.sat_hub_bounding_box, self.resolution)
            if self.sat_hub_bounding_box_size[0] > self.max_resolution_allowed or self.sat_hub_bounding_box_size[1] > self.max_resolution_allowed:
                self.resolution = None
                self.sat_hub_bounding_box_size = self.calculate_size_from_bbox(self.sat_hub_bounding_box)
                self.log.warning(f"Resolution is too high. Max resolution allowed is {self.max_resolution_allowed}, setting resolution to {self.resolution} based on bounding box size")
        else:
            self.sat_hub_bounding_box_size = self.calculate_size_from_bbox(self.sat_hub_bounding_box)

        self.log.info(f"Resolution: {self.resolution}, Bounding box size: {self.sat_hub_bounding_box_size}")
            
        

        # Calculate the bounding box size based on the resolution
        #self.sat_hub_bounding_box_size = self.calculate_size_from_bbox(self.bounding_box.bounds)
        
        

    def _get_response(self):
        self.log.info("Getting data from Sentinel Hub")
        request = self.get_request()
        response = request.get_data(save_data=False,show_progress=True,decode_data=False)
        return response

    def write_geotiff(self, output_file: str = None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/output.tif"
        response = self._get_response()
        
        data_in_memory = BytesIO(response[0].content )
        with rasterio.open(data_in_memory) as src:
            data, meta = self._default_rasterio_preprocess(src)
            _range = data.shape[0]
            
            with rasterio.open(output_file, "w", **meta) as dst:
                for i in range(1,_range+1):
                    dst.write(data[i-1],i)
    
    
    def extract_bandmatrix(self):
        response = self._get_response()
        
        data_in_memory = BytesIO(response[0].content)
        with rasterio.open(data_in_memory) as src:
            data, meta = self._default_rasterio_preprocess(src)
            return data


    def _default_rasterio_preprocess(self, geotiff):
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



    def calculate_size_from_bbox(self, bbox):
        """
            Calculate the width and height of a bounding box based on its resolution.
            Parameters:
            bbox (object): A bounding box object with attributes lower_left and upper_right, 
                           which are tuples representing the coordinates (east, north).
            Returns:
            tuple: A tuple containing the width and height of the bounding box.
            Notes:
            - If the resolution is not set or is less than or equal to 0, the method calculates 
              the minimal resolution that ensures the maximum width/height is less than or equal 
              to 2500 units.
            - The resolution is then used to calculate the width and height of the bounding box.
        """
        if self.resolution is None:
            self.resolution = 0
        utm_bbox = geo_utils.to_utm_bbox(bbox)
        east1, north1 = utm_bbox.lower_left
        east2, north2 = utm_bbox.upper_right

        delta_x = abs(east2 - east1)
        delta_y = abs(north2 - north1)

        if not self.resolution or self.resolution <= 0:
            # find the minimal resolution that ensures max width/height <= 2500
            self.resolution = max(delta_x / self.max_resolution_allowed, delta_y / self.max_resolution_allowed)
            self.resolution = math.ceil(self.resolution)

        width = int(round(delta_x / self.resolution))
        height = int(round(delta_y / self.resolution))
        return width, height
        
    
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