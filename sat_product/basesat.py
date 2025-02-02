from abc import abstractmethod
from shapely import Polygon
from shapely.geometry import Point
import logging
from sat_product.baseproduct import BaseProduct

class BaseSatType(BaseProduct):
    
    
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.NW_point = Point(config["point1"])
        self.SE_point = Point(config["point2"])
        self.NW_Long = config["point1"][1]
        self.NW_Lat = config["point1"][0]
        self.SE_Long = config["point2"][1]
        self.SE_Lat = config["point2"][0]
        # Output folder
        
        self.bounding_box = Polygon([
            (self.NW_Long, self.NW_Lat),
            (self.NW_Long, self.SE_Lat),
            (self.SE_Long, self.SE_Lat),
            (self.SE_Long, self.NW_Lat)
        ])
        self.geotiff_trasform = None
        self.geotiff_meta = None
        self.output_file = None