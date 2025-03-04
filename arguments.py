import argparse
from datetime import datetime
import re
valuemap_re = re.compile(r'([\d.]+,[\d.]+)')

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date: '{s}'.")

def valid_value_map(s):
    try:
        all_matches = valuemap_re.findall(s)
        if len(all_matches) == 0:
            raise Exception
        return tuple(map(float, all_matches[0].split(',')))
    except Exception:
        raise argparse.ArgumentTypeError(f"Not a valid value map: '{s}'. Must be in the form of 'value1,weight1 value2,weight2'")
            
def get_value_map(values : list):
    if values is None:
        return None
    return {value[0]:value[1] for value in values}
    
def initialize_sentinelhub_subparser(subparser):
    subparser.add_argument('-id', '--client_id', type=str, required=True, help='Client ID')
    subparser.add_argument('-s', '--client_secret', type=str, required=True, help='Client Secret')
    subparser.add_argument('-sd', '--start_date', type=valid_date, required=True, help='Start date')
    subparser.add_argument('-ed', '--end_date', type=valid_date, required=True, help='End date')
    subparser.add_argument('-cc','--cloud_coverage', type=int, default=20, help='Cloud Coverage percentage (default: 20)')
    subparser.add_argument('--resolution', type=int, help='Resolution in meters per pixel')
    return subparser

def initialize_esa_subparser(subparser):
    subparser.add_argument('-v', '--version', type=int, required=True, help='Version of the ESA World Cover 1 (2020) or 2 (2021)')
    subparser.add_argument('--disable_cache', action='store_true',default=False, help='Use cache')
    return subparser

def gprox_subparser(subparser):
    subparser.add_argument('-mr', '--meter_radius', type=int, required=True, help='Meter radius for gprox')
    subparser.add_argument('--value_map', type=valid_value_map, nargs='+', required=False, help='Default value is predefined for each product, but you can specify a value map in the form of "value1,weight1 value2,weight2"')
    subparser.add_argument('--omega', type=float, default=1, help='Omega value for gprox (default: 1) 1-(x/distance)^omega where x is the distance from the center')
    subparser.add_argument('--function', type=str, default='1-(x/r)**o', help='Function to calculate the weight of the pixel based on the distance from the center. x is the distance from the center, r is the radius and o is the omega value. Default is 1-(x/r)**o')
    return subparser


def landcover_subparser(subparser):
    subparser.add_argument('--ndwi_threshold', type=float, default=0.2, help='NDWI threshold (default: 0.2)')
    subparser.add_argument('--ndvi_grass_min', type=float, default=0.3, help='NDVI grass minimum (default: 0.3)')
    subparser.add_argument('--ndvi_trees_min', type=float, default=0.6, help='NDVI trees minimum (default: 0.6)')
    subparser.add_argument('--ndbi_building_min', type=float, default=0.16, help='NDBI building minimum (default: 0.16)')

    
def base_parser():
    """
    Creates and returns the argument parser for the sat_hub
    """
    parser = argparse.ArgumentParser(description='Sat Hub')
    parser.add_argument('-p1', '--point1', type=float, nargs=2, required=True, help='First point (latitude and longitude)')
    parser.add_argument('-p2', '--point2', type=float, nargs=2, required=True, help='Second point (latitude and longitude)')
    parser.add_argument('-o', '--output', type=str, help="Output file default is 'output/{type}_*date_time*.tif' where *date_time* is a placeholder for the current date and time")
    
    #parser.add_argument('--output_type', type=str, default='tiff', help='Output type (default: tiff)')


    # Add subparsers
    subparsers = parser.add_subparsers(dest='type', help='Type of classification', required=True)

    #RGB specific options
    rgb_parser = subparsers.add_parser('rgb', help='RGB specific options')
    rgb_parser.add_argument('--brightness', type=float, default=2.5, help='Brightness factor (default: 2.5)')
    initialize_sentinelhub_subparser(rgb_parser)
 
    #Landcover specific options
    landcover_parser = subparsers.add_parser('landcover', help='Landcover specific options')
    landcover_subparser(landcover_parser)
    initialize_sentinelhub_subparser(landcover_parser)

    

    #Vis specific options
    vis_parser = subparsers.add_parser('vis', help='Vis specific options')
    initialize_sentinelhub_subparser(vis_parser)

    #NDVI specific options
    ndvi_parser = subparsers.add_parser('ndvi', help='NDVI specific options')
    initialize_sentinelhub_subparser(ndvi_parser)

    #Stemp specific options
    stemp_parser = subparsers.add_parser('stemp', help='Stemp specific options')
    initialize_sentinelhub_subparser(stemp_parser)

    # Sentinel GProx specific options
    sent_gprox_parser = subparsers.add_parser('sentinel_gprox', help='Sentinel GProx specific options')
    gprox_subparser(sent_gprox_parser)
    landcover_subparser(sent_gprox_parser)
    initialize_sentinelhub_subparser(sent_gprox_parser)

    #S3 Gprox specific options
    s3_gprox_parser = subparsers.add_parser('s3_gprox', help='Gprox specific options')
    gprox_subparser(s3_gprox_parser)
    initialize_esa_subparser(s3_gprox_parser)
    
    #S3 ESA World Cover specific options
    esa_s3_parser = subparsers.add_parser('s3_esaworldcover', help='S3 ESA World Cover specific options')
    initialize_esa_subparser(esa_s3_parser)

    #Local File
    local_parser = subparsers.add_parser('file_gprox', help='Local GEO TIFF specific options')
    local_parser.add_argument('-f', '--input_file', type=str, required=True, help='Local file path')
    local_parser.add_argument('-res', '--resolution', type=float,nargs=2 , required=True, help='Resolution in meters per pixel (x,y)')
    gprox_subparser(local_parser)
    
    
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
    