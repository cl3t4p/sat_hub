import os
import tarfile
import numpy as np
from PIL import Image
import shutil

def extractImagesFromTar(outputFolderPath : str):
    print("Extracting images...")
    
    for subdir in os.listdir(outputFolderPath):
        subdir_path = os.path.join(outputFolderPath, subdir)
        if os.path.isdir(subdir_path):
            if "response.tar" in os.listdir(subdir_path):
                tarPath = os.path.join(subdir_path, "response.tar")
                targetFolder = os.path.join(outputFolderPath, "extracted_contents")
                if not os.path.exists(targetFolder):
                    os.makedirs(targetFolder)
                with tarfile.open(tarPath, 'r') as tar:
                    tar.extractall(targetFolder)
                 # Rimuovere la tar
                os.remove(tarPath)
                
                # Move the extracted contents to the target folder
                for item in os.listdir(subdir_path):
                    s = os.path.join(subdir_path, item)
                    d = os.path.join(outputFolderPath, item)
                    shutil.move(s, d)
                
                # Remove the now empty extracted_contents folder
                os.rmdir(subdir_path)

    print("Extraction completed")
    
def convertImageTo4Colors(inputPath, outputPath):

    print("Image Conversion...")

    # Definire i colori di destinazione
    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 128, 255),
        "white": (255, 255, 255)
    }

   # Funzione per trovare il colore più vicino
    def closestColor(pixel, colors):
        min_dist = float('inf')
        closest_color = None
        for color_value in colors.values():
            dist = np.linalg.norm(np.array(pixel) - np.array(color_value))
            if dist < min_dist:
                min_dist = dist
                closest_color = color_value
        return closest_color

    try:
        # Aprire l'immagine
        img = Image.open(inputPath)
        img = img.convert("RGB")  # Assicurarsi che l'immagine sia in RGB

        # Convertire l'immagine in un array numpy
        img_array = np.array(img)

        totalPixel = img_array.shape[0] * img_array.shape[1]
        lastProgress = -1

        # Approssimare ogni pixel al colore più vicino
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                img_array[i, j] = closestColor(img_array[i, j], colors)

                
                # Stampa della percentuale di completamento
                progress = (i * img_array.shape[1] + j) / totalPixel * 100
                progress_int = int(progress)
                if progress_int > lastProgress:
                    print('Progress: {:.0f}%'.format(progress_int), end='\r')
                lastProgress = progress_int

        # Convertire l'array numpy di nuovo in un'immagine
        newImg = Image.fromarray(img_array.astype('uint8'), 'RGB')

        # Salvare l'immagine in formato TIFF
        newImg.save(outputPath, format='TIFF')

    except Exception as e:
        print(f"Conversion error: {e}")