from abc import abstractmethod

import os
from shapely.geometry import box
from sat_hub_lib.baseproducts import BaseSatType

class BaseSat_GeoTiff(BaseSatType):
    def __init__(self, config):
        super().__init__(config)

        # Bounding box
        self.cord_bounding_box = box(
            self.NW_Long, self.SE_Lat, self.SE_Long, self.NW_Lat
        )
