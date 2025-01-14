from utils.arguments import check_args, base_parser
from sat_product.sentinel.basetype_sent import BaseSatType
import toml

# Parse the arguments
parser = base_parser()
args = parser.parse_args()
try:
    check_args(args)
except Exception as e:
    print(f"An error occurred: {e}")
    exit()
    
config = vars(args)
# Load config.toml
config.update(toml.load("config.toml"))

product : BaseSatType = None
match args.type:
    case "gprox":
        from sat_product.sentinel.gprox import GProx
        product = GProx(vars(args))
    case "stype":
        from sat_product.sentinel.stype import SType
        product = SType(vars(args))
    case "vis":
        from sat_product.sentinel.vis import Vis
        product = Vis(vars(args))
    case "stemp":
        from sat_product.sentinel.stemp import STemp
        product = STemp(vars(args))
    case "s3_esaworldcover":
        from sat_product.geotiff.s3.esaworldcover import S3_EsaWorldCover
        product = S3_EsaWorldCover(vars(args))
    case _:
        print("Invalid type")
        exit()

# Process the data
product.process()
print("Process completed")