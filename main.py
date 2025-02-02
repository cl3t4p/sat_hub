import utils.arguments as arguments
import toml

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
    
# Load config.toml
config = vars(args)
config.update(toml.load("config.toml"))




match args.type:
    #case "gprox":
        #from sat_product.sentinel.gprox import GProx
        #product = GProx(config)
        #product.write_geotiff()
    case "landcover":
        from sat_product.sentinel.landcover import Landcover
        product = Landcover(config)
        product.write_geotiff()
    case "vis":
        from sat_product.sentinel.vis import Vis
        product = Vis(config)
        product.write_geotiff()
    case "rgb":
        from sat_product.sentinel.rgb import RGB
        product = RGB(config)
        product.write_geotiff()
    case "stemp":
        from sat_product.sentinel.stemp import STemp
        product = STemp(config)
        product.write_geotiff()
    case "s3_esaworldcover":
        from sat_product.geotiff.s3.esaworldcover import S3_EsaWorldCover
        import utils.geotiff.geotiff_lib as geotiff_lib
        product = S3_EsaWorldCover(config)
        output_file = f"{product.get_outfolder()}/esaworldcover.tif"
        product.write_geotiff(output_file)
        geotiff_lib.tiff_to_png(output_file,f"{product.get_outfolder()}/esaworldcover.png")
    case "s3_gprox":
        from sat_product.geotiff.s3.esaworldcover import S3_EsaWorldCover, ESAWC_MAPCODE
        from sat_product.extension.gprox import GProx
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