from .base_type import BaseType
from sentinelhub import SentinelHubRequest, DataCollection

class GProx(BaseType):
    
    def __init__(self, args : dict):
        super().__init__(args)
        resolution = self.longSide / 750
        # Il valore di metri di raggio sono i metri di raggio che l'utente vuole considerare per il calcolo dell'indice di prossimità di verde
        # Dividendo i metri di raggio per la risoluzione si ottiene il raggio in pixel, che verrà utilizzato per il calcolo dell'indice di prossimità di verde
        self.vegetationIndexRadius = round(float(args["meterRadius"]) / resolution)
        
    def process(self):
        request = self.get_request()
        print("Request sent")
        response = request.get_data(save_data=True)
        print("Request completed")
        BaseType.extractImagesFromTar(self.outputFolder)
        
        
    def get_input_data(self):
        return [
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,     
                time_interval=(self.timeIntervalStart, self.timeIntervalEnd),
                other_args={"dataFilter": {"maxCloudCoverage": self.maxCloudCoverage}}
            ),
        ]
    
    def get_evalscript(self):
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
                output: { bands: 4 }
            };
        }
    """