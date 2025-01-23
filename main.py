from utils.arguments import check_args, base_parser

import toml

import logging 
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("MAIN")



log.info("Parsing arguments")
# Parse the arguments
parser = base_parser()
args = parser.parse_args()
try:
    check_args(args)
except Exception as e:
    log.error(f"An error occurred: {e}")
    exit()
    
config = vars(args)
# Load config.toml
config.update(toml.load("config.toml"))


match args.type:
    case "stype":
        from sat_product.sentinel.stype import SType
        product = SType(vars(args))
        product.process()
    case "vis":
        from sat_product.sentinel.vis import Vis
        product = Vis(vars(args))
        product.process()
    case "stemp":
        from sat_product.sentinel.stemp import STemp
        product = STemp(vars(args))
        product.process()
    case "s3_esaworldcover":
        from sat_product.geotiff.s3.esaworldcover import S3_EsaWorldCover
        product = S3_EsaWorldCover(vars(args))
        product.process()
    case "s3_gprox":
        from sat_product.geotiff.s3.esaworldcover import S3_EsaWorldCover,S3_GProx
        import utils.geotiff.geotiff_lib as geotiff_lib
        product = S3_EsaWorldCover(vars(args))
        gprox = S3_GProx(product,vars(args))
        percentage_matrix = gprox.get_percentage_convolution_matrix()
        gprox.write_matrix_to_geotiff(percentage_matrix,product,f"{product.get_outfolder()}/gprox.tif")
    case _:
        log.error(f"Type {args.type} not supported")
        exit()



log.info("Process completed")