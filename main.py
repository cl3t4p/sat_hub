from utils.arguments import check_args, base_parser
from sat_product.base_type import BaseType

# Parse the arguments
parser = base_parser()
args = parser.parse_args()
try:
    check_args(args)
except Exception as e:
    print(f"An error occurred: {e}")
    exit()


product : BaseType = None
match args.type:
    case "gprox":
        from sat_product.gprox import GProx
        product = GProx(vars(args))
    case "stype":
        from sat_product.stype import SType
        product = SType(vars(args))
    case "vis":
        from sat_product.vis import Vis
        product = Vis(vars(args))
    case "stemp":
        from sat_product.stemp import STemp
        product = STemp(vars(args))
    case _:
        print("Invalid type")
        exit()


# Process the data
product.process()
print("Process completed")