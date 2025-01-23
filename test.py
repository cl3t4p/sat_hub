from PIL import Image

Image.MAX_IMAGE_PIXELS = None

image = Image.open('output\S3_EsaWorldCover_20250122_234359\output.tif')
palette = image.getpalette()
for i in range(0, len(palette), 3):
    print(f"Color {i//3}: {palette[i:i+3]}")