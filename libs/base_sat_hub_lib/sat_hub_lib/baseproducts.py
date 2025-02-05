from abc import ABC, abstractmethod
import datetime
import os
from shapely import Polygon
from shapely.geometry import Point
import logging
import rasterio


class BaseProduct(ABC):

    def __init__(self, config: dict):
        self.__output_folder = self.__get_outfolder(config["output"])
        self.output_file = None
        self.log = logging.getLogger(type(self).__name__)

    @abstractmethod
    def write_geotiff(self, output_file: str = None):
        """
        Abstract method to write the data to a GeoTIFF file.

        Parameters:
        output_file (str, optional): The path to the output GeoTIFF file. If not provided, a default path should be used.

        Raises:
        NotImplementedError: This method must be overridden in a subclass.
        """
        pass

    @abstractmethod
    def extract_bandmatrix(self):
        """
        Abstract method to extract the band matrix from the data.

        Returns:
        np.ndarray: The band matrix. (Remember that the matrix is with the format [bands, rows, cols])

        Raises:
        NotImplementedError: This method must be overridden in a subclass.
        """
        pass

    def __get_outfolder(self, outfolder):
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
            className = type(self).__name__
            return f"output/{className}_{time}"

    def get_outfolder(self, no_create=True) -> str:
        """
        Returns the output folder path if it exists, otherwise creates it.
        """
        if not os.path.exists(self.__output_folder) and no_create:
            os.makedirs(self.__output_folder)
        return self.__output_folder
    
    def _default_rasterio_preprocess(self, geotiff):
        self.geotiff_meta = geotiff.meta
        self.geotiff_trasform = geotiff.transform

        data = geotiff.read()
        out_meta = geotiff.meta.copy()
        out_meta.update(
            height=data.shape[1],
            width=data.shape[2],
            driver="GTiff",
            count=data.shape[0],
            dtype=rasterio.uint8,
        )
        return data, out_meta


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

        self.bounding_box = Polygon(
            [
                (self.NW_Long, self.NW_Lat),
                (self.NW_Long, self.SE_Lat),
                (self.SE_Long, self.SE_Lat),
                (self.SE_Long, self.NW_Lat),
            ]
        )
        self.geotiff_trasform = None
        self.geotiff_meta = None
        self.output_file = None
