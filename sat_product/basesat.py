from abc import ABC, abstractmethod
import datetime
from shapely.geometry import Point

class BaseSatType(ABC):
    
    def __init__(self, config: dict):
        self.NW_point = Point(config["point1"])
        self.SE_point = Point(config["point2"])
        self.NW_Long = config["point1"][1]
        self.NW_Lat = config["point1"][0]
        self.SE_Long = config["point2"][1]
        self.SE_Lat = config["point2"][0]
    
    @abstractmethod
    def process(self):
        pass
    
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
            return outfolder.replace("output/*date_time*", time)
        else:
            className = self.__class__.__name__
            return f"{className}_{time}"