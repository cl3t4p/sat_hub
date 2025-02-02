import argparse
from datetime import datetime

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: '{s}'.")


#TODO Ask if html should stay in the code
def output_type(s):
    valid_types = ['tiff', 'jpg', 'png','html']
    if s not in valid_types:
        raise argparse.ArgumentTypeError(f"Invalid output type: '{s}'. Valid types are {valid_types}.")
    return s

    
def initialize_sentinelhub_subparser(subparser):
    subparser.add_argument('-id', '--client_id', type=str, required=True, help='Client ID')
    subparser.add_argument('-s', '--client_secret', type=str, required=True, help='Client Secret')
    subparser.add_argument('-sd', '--start_date', type=valid_date, required=True, help='Start date')
    subparser.add_argument('-ed', '--end_date', type=valid_date, required=True, help='End date')
    subparser.add_argument('-c','--cloud_coverage', type=int, default=20, help='Cloud Coverage percentage (default: 20)')
    subparser.add_argument('--html', action='store_true', help='Output html file') # TODO: Ask if this should stay in the code
    subparser.add_argument('-res','--resolution', type=int, help='Resolution in meters per pixel')
    return subparser

def initialize_s3_subparser(subparser):
    subparser.add_argument('-v', '--version', type=int, required=True, help='Version of the ESA World Cover 1 (2020) or 2 (2021)')
    subparser.add_argument('--disable_cache', action='store_true',default=False, help='Use cache')
    return subparser

    
def base_parser():
    """
    Creates and returns the argument parser for the sat_hub
    """
    parser = argparse.ArgumentParser(description='Sat Hub')
    parser.add_argument('-p1', '--point1', type=float, nargs=2, required=True, help='First point (latitude and longitude)')
    parser.add_argument('-p2', '--point2', type=float, nargs=2, required=True, help='Second point (latitude and longitude)')
    parser.add_argument('-o', '--output', type=str, help="Output folder default is 'output/{type}_*date_time*' where *date_time* is a placeholder for the current date and time")
    
    parser.add_argument('--output_type', type=str, default='tiff', help='Output type (default: tiff)')


    # Add subparsers
    subparsers = parser.add_subparsers(dest='type', help='Type of classification', required=True)

    #RGB specific options
    rgb_parser = subparsers.add_parser('rgb', help='RGB specific options')
    rgb_parser.add_argument('--brightness', type=float, default=2.5, help='Brightness factor (default: 2.5)')
    initialize_sentinelhub_subparser(rgb_parser)
 
    #Landcover specific options
    landcover_parser = subparsers.add_parser('landcover', help='Landcover specific options')
    initialize_sentinelhub_subparser(landcover_parser)

    #Vis specific options
    vis_parser = subparsers.add_parser('vis', help='Vis specific options')
    initialize_sentinelhub_subparser(vis_parser)

    #Stemp specific options
    stemp_parser = subparsers.add_parser('stemp', help='Stemp specific options')
    initialize_sentinelhub_subparser(stemp_parser)

    # Sentinel GProx specific options
    sent_gprox_parser = subparsers.add_parser('sentinel_gprox', help='Sentinel GProx specific options')
    sent_gprox_parser.add_argument('-mr', '--meter_radius', type=int, required=True, help='Meter radius for gprox')
    initialize_sentinelhub_subparser(sent_gprox_parser)

    #S3 Gprox specific options
    gprox_parser = subparsers.add_parser('s3_gprox', help='Gprox specific options')
    gprox_parser.add_argument('-mr', '--meter_radius', type=int, required=True, help='Meter radius for gprox')
    initialize_s3_subparser(gprox_parser)
    
    #S3 ESA World Cover specific options
    esa_s3_parser = subparsers.add_parser('s3_esaworldcover', help='S3 ESA World Cover specific options')
    initialize_s3_subparser(esa_s3_parser)
    
    
    return parser



def check_args(args):

    if args.point1[0] < -90 or args.point1[0] > 90 or args.point1[1] < -180 or args.point1[1] > 180:
        raise argparse.ArgumentTypeError(f"Latitude and longitude must be between -90 and 90 and -180 and 180 respectively")
    if args.point2[0] < -90 or args.point2[0] > 90 or args.point2[1] < -180 or args.point2[1] > 180:
        raise argparse.ArgumentTypeError(f"Latitude and longitude must be between -90 and 90 and -180 and 180 respectively")

    
    if hasattr(args, 'start_date') and hasattr(args, 'end_date') and args.start_date > args.end_date:
        raise argparse.ArgumentTypeError(f"Start date must be before end date")
    if hasattr(args, 'cloud_coverage') and (args.cloud_coverage < 0 or args.cloud_coverage > 100):
        raise argparse.ArgumentTypeError(f"Cloud coverage must be between 0 and 100")
    
    #GProx specific checks
    if args.type == 'gprox' or args.type == 's3_gprox':
        if args.meter_radius < 0:
            raise argparse.ArgumentTypeError(f"Meter radius must be positive")
    