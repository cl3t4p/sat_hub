import rasterio
from . import basetype_sent
from sentinelhub import SentinelHubRequest, DataCollection
import utils.geotiff.geotiff_lib as geotiff_lib

class Landcover(basetype_sent.SentinelBaseType):
    
    COLOR_MAP = {
    0: (255, 0, 0, 255),       # Buildings - Red
    1: (0, 0, 255, 255),       # Water - Blue
    2: (0, 100, 0, 255),       # Trees - Dark Green
    3: (154, 205, 50, 255),    # Grass - Yellow Green
    4: (255, 215, 0, 255),     # Agriculture - Gold
    5: (139, 69, 19, 255),     # Mountains - Brown
    6: (210, 180, 140, 255)    # Other - Tan
  }

    
    def __init__(self, args : dict):
        super().__init__(args)
        
    
    def write_geotiff(self,output_file:str = None):
        super().write_geotiff(output_file)
        # Apply the color map
        geotiff_lib.apply_colormap(output_file,self.COLOR_MAP)
        
        

    def extract_bandmatrix(self):
        return super().extract_bandmatrix()

    def _get_input_type(self):
         return [
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,     
                        time_interval=(self.timeIntervalStart, self.timeIntervalEnd),
                        other_args={"dataFilter": {"maxCloudCoverage": self.cloud_coverage}}
                    ),
                ]
        
    

    
    def _get_evalscript(self) -> str:
        return """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: ["B03", "B04", "B08", "B11", "B12",],
      units: "REFLECTANCE"
    }],
    output: { bands: 1, sampleType: "UINT8" }
  };
}

function evaluatePixel(sample) {
  // Calculate indices
  let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);  // Water
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);  // Vegetation
  let ndbi = (sample.B11 - sample.B08) / (sample.B11 + sample.B08);  // Built-up
  let mndwi = (sample.B03 - sample.B12) / (sample.B03 + sample.B12); // Modified Water
  
  // Terrain analysis (using SWIR bands for rock detection)
  let rock_index = (sample.B11 - sample.B12) / (sample.B11 + sample.B12);
  
  // Classification logic
  if (ndwi > 0.2 || mndwi > 0.4) {                  // Water
    return [1];
  } else if (ndbi > 0.2 && rock_index < 0.1) {       // Buildings
    return [0];
  } else if (ndbi > 0.15 && rock_index > 0.25) {     // Mountains/Rocks
    return [5]; 
  } else if (ndvi > 0.2) {                           // Vegetation
    if (ndvi > 0.6) return [2];                      // Trees
    if (ndvi > 0.3) return [4];                      // Agriculture
    return [3];                                       // Grass
  } else {                                            // Bare soil/other
    return [6];
  }
}
"""
