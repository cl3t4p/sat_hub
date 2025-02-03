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
        from sat_hub_lib.sentinel.landcover import Landcover, SAT_LANDCOVER_MAPCODE
        from sat_hub_lib.extension.gprox import GProx
        product = Landcover(config)
        # Define GProx target value to map
        value = SAT_LANDCOVER_MAPCODE.TREES
        
        gprox = GProx(product,config,value.code)
        gprox.write_geotiff()
    #product.write_geotiff()
    case "landcover":
        from sat_hub_lib.sentinel.landcover import Landcover
        product = Landcover(config)
        product.write_geotiff()
    case "vis":
        from sat_hub_lib.sentinel.vis import Vis
        product = Vis(config)
        product.write_geotiff()
    case "rgb":
        from sat_hub_lib.sentinel.rgb import RGB
        product = RGB(config)
        product.write_geotiff()
    case "stemp":
        from sat_hub_lib.sentinel.stemp import STemp
        product = STemp(config)
        product.write_geotiff()
    case "s3_esaworldcover":
        from sat_hub_lib.geotiff.s3.esaworldcover import S3_EsaWorldCover
        import sat_hub_lib.utils.geotiff_lib as geotiff_lib
        product = S3_EsaWorldCover(config)
        output_file = f"{product.get_outfolder()}/esaworldcover.tif"
        product.write_geotiff(output_file)
        geotiff_lib.tiff_to_png(output_file,f"{product.get_outfolder()}/esaworldcover.png")
    case "s3_gprox":
        from sat_hub_lib.geotiff.s3.esaworldcover import S3_EsaWorldCover, ESAWC_MAPCODE
        from sat_hub_lib.extension.gprox import GProx
        product = S3_EsaWorldCover(config)
        # Define GProx target value to map
        value = ESAWC_MAPCODE.TREE_COVER
        gprox = GProx(product,config,value.code)
        output_file = f"{gprox.get_outfolder()}/gprox.tif"
        gprox.write_geotiff(output_file)
    case _:
        log.error(f"Type {args.type} not supported")
        exit()
        
log.info("Process completed")