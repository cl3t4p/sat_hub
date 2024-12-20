from utils.arguments import check_args, base_parser

# Parse the arguments
parser = base_parser()
args = parser.parse_args()
try:
    check_args(args)
except Exception as e:
    print(f"An error occurred: {e}")
    exit()

# Import the necessary modules
from sat_type.stype import SatType


# Create the SatType object
stype = SatType(vars(args))

# Process the data
stype.process()
print("Process completed")