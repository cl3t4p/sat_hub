from utils.arguments import check_args, base_parser

parser = base_parser()
args = parser.parse_args()
try:
    check_args(args)
except Exception as e:
    print(f"An error occurred: {e}")
    exit()


from sat_type.stype import SatType


stype = SatType(vars(args))

stype.process()
print("Process completed")