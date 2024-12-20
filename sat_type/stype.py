from . import base_type
from sentinelhub import SentinelHubRequest, DataCollection
from utils.functions import extractImagesFromTar, convertImageTo4Colors
from os import path
class SatType(base_type.BaseType):
    
    def __init__(self, args : dict):
        super().__init__(args)
    
    def process(self):
        request = self.get_request()
        print("Request sent")
        response = request.get_data(save_data=True)
        print("Request completed")

        # Estrazione delle immagini dal file tar
        print("outputFolder: ", self.outputFolder)
        extractImagesFromTar(self.outputFolder)
        
        # L'immagine jpg scaricata viene convertita in un'immagine a 4 colori
        convertImageTo4Colors(path.join(self.outputFolder, "extracted_contents", "default.jpg"), path.join(self.outputFolder, "extracted_contents", "convertedDefault.tif"))


    def get_input_data(self):
         return [
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,     
                        time_interval=(self.timeIntervalStart, self.timeIntervalEnd),
                        other_args={"dataFilter": {"maxCloudCoverage": self.maxCloudCoverage}}
                    ),
                ]
    
    def get_evalscript(self) -> str:
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