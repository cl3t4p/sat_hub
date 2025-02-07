import arguments
import logging 
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("MAIN")






# Parse the arguments
parser = arguments.base_parser()
args = parser.parse_args()
try:
    arguments.check_args(args)
except Exception as e:
    log.error(f"An error occurred: {e}")
    exit()
    
config = vars(args)
config["cache_folder"] = 'cache'




match args.type:
    case "sentinel_gprox":
        from sat_hub_lib.sentinel import Landcover, SAT_LANDCOVER_MAPCODE
        from sat_hub_lib.extension import GProx
        product = Landcover(config)
        gprox = GProx(product,config)
        gprox.write_geotiff()
    #product.write_geotiff()
    case "landcover":
        from sat_hub_lib.sentinel import Landcover
        product = Landcover(config)
        product.write_geotiff()
    case "vis":
        from sat_hub_lib.sentinel import Vis
        product = Vis(config)
        product.write_geotiff()
    case "rgb":
        from sat_hub_lib.sentinel import RGB
        product = RGB(config)
        product.write_geotiff()
    case "stemp":
        from sat_hub_lib.sentinel import STemp
        product = STemp(config)
        product.write_geotiff()
    case "s3_esaworldcover":
        from sat_hub_lib.geotiff.s3 import S3_EsaWorldCover
        product = S3_EsaWorldCover(config)
        output_file = f"{product.get_outfolder()}/esaworldcover.tif"
        product.write_geotiff(output_file)
    case "s3_gprox":
        from sat_hub_lib.geotiff.s3 import S3_EsaWorldCover, ESAWC_MAPCODE
        from sat_hub_lib.extension import GProx
        product = S3_EsaWorldCover(config)
        gprox = GProx(product,config)
        output_file = f"{gprox.get_outfolder()}/gprox.tif"
        gprox.write_geotiff(output_file)
    case "file_gprox":
        from sat_hub_lib.geotiff import Local_GeoTiff
        from sat_hub_lib.extension import GProx
        product = Local_GeoTiff(config)

        value = config.get("value_to_map")
        gprox = GProx(product,config,value)
        output_file = f"{gprox.get_outfolder()}/gprox.tif"
        gprox.write_geotiff(output_file)
    case _:
        log.error(f"Type {args.type} not supported")
        exit()
        
log.info("Process completed")