import argparse
from datetime import datetime

def valid_date(s):
    
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: '{s}'.")


def base_parser():
    """
    Creates and returns the argument parser for the Sentinel-2 Land Cover Classification script.
    Arguments:
        -sd, --start_date (str): Start date (required).
        -id, --client_id (str): Client ID (required).
        -s, --client_secret (str): Client Secret (required).
        -ed, --end_date (str): End date (required).
        -c, --cloud_coverage (int): Cloud Coverage percentage (default: 20).
        -p1, --point1 (float, nargs=2): First point (latitude and longitude) (required).
        -p2, --point2 (float, nargs=2): Second point (latitude and longitude) (required).
        -o, --output (str): Output folder using *unix_time* as placeholder for the current unix time, like 'result_*unix_time*'.
        --html: Output html file (flag).
    Subparsers:
        gprox: Gprox specific options.
            -mr, --meterRadius (int): Meter radius for gprox (required).
        stype: Stype specific options.
        vis: Vis specific options.
        stemp: Stemp specific options.
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description='Sentinel-2 Land Cover Classification')
    parser.add_argument('-id', '--client_id', type=str, required=True, help='Client ID')
    parser.add_argument('-s', '--client_secret', type=str, required=True, help='Client Secret')

    
    parser.add_argument('-sd','--start_date', type=valid_date, required=True, help='Start date')
    parser.add_argument('-ed','--end_date', type=valid_date, required=True, help='End date')
    parser.add_argument('-c','--cloud_coverage', type=int, default=20, help='Cloud Coverage percentage (default: 20)')
    parser.add_argument('-p1', '--point1', type=float, nargs=2, required=True, help='First point (latitude and longitude)')
    parser.add_argument('-p2', '--point2', type=float, nargs=2, required=True, help='Second point (latitude and longitude)')
    parser.add_argument('-o', '--output', type=str, help="Output folder default is '\{type\}_*date_time*' where *date_time* is a placeholder for the current date and time")
    parser.add_argument('--pixel_value', type=int, default=750, help='Pixel value for the long side of the area of interest (default: 750)')
    parser.add_argument('--html', action='store_true', help='Output html file')
    
    #GProx specific options 
    subparsers = parser.add_subparsers(dest='type', help='Type of classification',required=True)
    gprox_parser = subparsers.add_parser('gprox', help='Gprox specific options')
    gprox_parser.add_argument('-mr', '--meterRadius', type=int, required=True, help='Meter radius for gprox')
    
    #Stype specific options
    subparsers.add_parser('stype', help='Stype specific options')
    
    
    #Vis specific options
    subparsers.add_parser('vis', help='Vis specific options')
    
    #Stemp specific options
    subparsers.add_parser('stemp', help='Stemp specific options')


    return parser
    
    

def check_args(args):
    if args.start_date > args.end_date:
        raise argparse.ArgumentTypeError(f"Start date must be before end date")
    if args.point1[0] < -90 or args.point1[0] > 90 or args.point1[1] < -180 or args.point1[1] > 180:
        raise argparse.ArgumentTypeError(f"Latitude and longitude must be between -90 and 90 and -180 and 180 respectively")
    if args.point2[0] < -90 or args.point2[0] > 90 or args.point2[1] < -180 or args.point2[1] > 180:
        raise argparse.ArgumentTypeError(f"Latitude and longitude must be between -90 and 90 and -180 and 180 respectively")
    if args.cloud_coverage < 0 or args.cloud_coverage > 100:
        raise argparse.ArgumentTypeError(f"Cloud coverage must be between 0 and 100")
    #GProx specific checks
    if args.type == 'gprox':
        if args.meterRadius < 0:
            raise argparse.ArgumentTypeError(f"Meter radius must be positive")
    