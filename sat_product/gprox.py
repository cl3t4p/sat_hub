from .base_type import BaseType
from sentinelhub import SentinelHubRequest, DataCollection
import sat_img_processing
import cv2
import numpy as np
import os
from PIL import Image

class GProx(BaseType):
    
    def __init__(self, args : dict):
        super().__init__(args)
        resolution = self.longSide / 750
        # Il valore di metri di raggio sono i metri di raggio che l'utente vuole considerare per il calcolo dell'indice di prossimità di verde
        # Dividendo i metri di raggio per la risoluzione si ottiene il raggio in pixel, che verrà utilizzato per il calcolo dell'indice di prossimità di verde
        self.vegetationIndexRadius = round(float(args["meterRadius"]) / resolution)
        print(f"Output folder: {self.outputFolder}")
        
    def process(self):
        request = self.get_request()
        print("Request sent")
        response = request.get_data(save_data=True)
        print("Request completed")
        BaseType.extractImagesFromTar(self.outputFolder)
        
        
        
        value_matrix = GProx.getValuesMatrix(self.outputFolder + "/extracted_contents/default.tif")
        percentage_matrix = sat_img_processing.get_percentage_matrix(value_matrix, self.vegetationIndexRadius)
        
        sat_img_processing.generate_image(percentage_matrix, self.outputFolder + "/output.tif")
        
        os.rename(self.outputFolder + "/extracted_contents/default.jpg", self.outputFolder + "/extracted_contents/default1.jpg")
        GProx.tiff2Jpg(self.outputFolder + "/extracted_contents/default.tiff", self.outputFolder+ "/extracted_contents/default.jpg")
        
        
        
        
    def get_input_data(self):
        return [
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,     
                time_interval=(self.timeIntervalStart, self.timeIntervalEnd),
                other_args={"dataFilter": {"maxCloudCoverage": self.maxCloudCoverage}}
            ),
        ]
        
    @staticmethod
    def tiff2Jpg(inputPath, outputPath):
        try:
            # Apri l'immagine TIFF
            with Image.open(inputPath) as img:
                # Converti l'immagine in RGB (necessario per salvare come JPG)
                img = img.convert("RGB")
                # Salva l'immagine in formato JPG
                img.save(outputPath, "JPEG")
        except Exception as e:
            print(f"Conversion error: {e}")
        
    @staticmethod
    def getValuesMatrix(inputImagePath):
        print(f"Reading image: {inputImagePath}")
        image = cv2.imread(inputImagePath)
        height, width, _ = image.shape

        # La matrice viene inizializzata con tutti zeri
        value_matrix = np.zeros((height, width), dtype=np.int32)

        for y in range(height):
            for x in range(width):
                pixelColor = image[y, x]
                # Verifica se il colore del pixel è nero (RGB: 0, 0, 0)
                if np.array_equal(pixelColor, [0, 0, 0]):
                    value_matrix[y][x] = 1

        return value_matrix
    
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