import rasterio
import json

#input_file = 'test_files/res/esaworldcover.tif'
input_file = 'cache/S3_EsaWorldCover/ESA_WorldCover_10m_2021_v200_N45E009_Map.tif'

with rasterio.open(input_file) as src:
    
    print(src.profile)
    print('-'*50)
    print(src.meta)