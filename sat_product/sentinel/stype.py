from . import basetype_sent
from sentinelhub import SentinelHubRequest, DataCollection
from io import BytesIO
import rasterio

class SType(basetype_sent.SentinelBaseType):
    
    def __init__(self, args : dict):
        super().__init__(args)
    
    def write_geotiff(self,output_file:str = None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/output.tif"

        self.log.info("Requesting data")
        request = self.get_request()
        response = request.get_data(save_data=False,show_progress=True,decode_data=False)
        self.log.info("Data received")
        
        data_in_memory = BytesIO(response[0].content )
        with rasterio.open(data_in_memory) as src:
            profile = src.profile
            profile.update(
                driver="GTiff",
                count=4,
                compress="lzw",
                dtype=rasterio.uint8
            )
            with rasterio.open(output_file, "w", **profile) as dst:
                _range = src.read().shape[0]
                for i in range(1,_range+1):
                    dst.write(src.read(i),i)


    def extract_bandmatrix(self):
        self.log.info("Requesting data")
        request = self.get_request()
        response = request.get_data(save_data=False,show_progress=True,decode_data=False)
        self.log.info("Data received")
        
        data_in_memory = BytesIO(response[0].content )
        with rasterio.open(data_in_memory) as src:
            profile = src.profile
            profile.update(
                driver="GTiff",
                count=4,
                compress="lzw",
                dtype=rasterio.uint8
            )
            return src.read()

    def _get_input_type(self):
         return [
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,     
                        time_interval=(self.timeIntervalStart, self.timeIntervalEnd),
                        other_args={"dataFilter": {"maxCloudCoverage": self.maxCloudCoverage}}
                    ),
                ]
        
    

    
    def _get_evalscript(self) -> str:
        return """
        //VERSION=3
        function evaluatePixel(samples) {
            var NDWI = index(samples.B03, samples.B08); 
            var NDVI = index(samples.B08, samples.B04);
            var BareSoil = 2.5 * ((samples.B11 + samples.B04) - (samples.B08 + samples.B02)) / ((samples.B11 + samples.B04) + (samples.B08 + samples.B02));

            if (NDWI > 0.2) {
                return [0, 0.5, 1, samples.dataMask];
            }
            if ((samples.B11 > 0.8) || (NDVI < 0.1)) {
                return [1, 1, 1, samples.dataMask];
            }
            if (NDVI > 0.2) {
                return [0, 1, 0, samples.dataMask];
            } else {
                return [1, 0, 0, samples.dataMask];
            }
        }
        function setup() {
            return {
                input: ["B02", "B03", "B04", "B08", "B11", "dataMask"],
                output: { bands: 4 }
            };
        }
    """