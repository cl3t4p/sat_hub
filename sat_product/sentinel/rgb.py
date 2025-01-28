from .basetype_sent import SentinelBaseType
from sentinelhub import SentinelHubRequest, DataCollection, MosaickingOrder

class RGB(SentinelBaseType):
    
    def __init__(self, args : dict):
        super().__init__(args)
    
    def _get_input_type(self):
        return [
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=("2020-06-01", "2020-06-30"),
                mosaicking_order=MosaickingOrder.LEAST_CC,
            )
        ]
    
    def write_geotiff(self,output_file:str = None):
        return super().write_geotiff(output_file)
    
    def extract_bandmatrix(self):
        return super().extract_bandmatrix()
    
    def _get_default_resolution(self):
        return 13
        
    def _get_evalscript(self):
        return """    
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04"]
                }],
                output: {
                    bands: 3
                }
            };
        }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
        """