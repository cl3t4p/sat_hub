from .basetype_sent import SentinelBaseType
from sentinelhub import SentinelHubRequest, DataCollection

class GProx(SentinelBaseType):
    
    def __init__(self, args : dict):
        super().__init__(args)
        self.meter_radius = args["meter_radius"]
        
    def write_geotiff(self,output_file:str = None):
        pass


    def extract_bandmatrix(self):
        pass
        
        
    def _get_input_type(self):
        return [
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,     
                time_interval=(self.timeIntervalStart, self.timeIntervalEnd),
                other_args={"dataFilter": {"maxCloudCoverage": self.cloud_coverage}}
            ),
        ]
        

    
    def _get_evalscript(self):
        return """
        //VERSION=3
        function evaluatePixel(samples) {
            var NDWI = index(samples.B03, samples.B08); 
            var NDVI = index(samples.B08, samples.B04);
            var BareSoil = 2.5 * ((samples.B11 + samples.B04) - (samples.B08 + samples.B02)) / ((samples.B11 + samples.B04) + (samples.B08 + samples.B02));

            if (NDWI > 0.2) {
                return [0, 1, 0, samples.dataMask];
            }
            if ((samples.B11 > 0.8) || (NDVI < 0.1)) {
                return [1, 1, 1, samples.dataMask];
            }
            if (NDVI > 0.2) {
                return [0, 1, 0, samples.dataMask];
            } else {
                return [1, 1, 1, samples.dataMask];
            }
        }
        function setup() {
            return {
                input: ["B02", "B03", "B04", "B08", "B11", "dataMask"],
                output: { bands: 1 }
            };
        }
    """