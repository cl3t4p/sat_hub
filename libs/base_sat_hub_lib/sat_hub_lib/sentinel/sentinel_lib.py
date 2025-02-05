import sentinelhub.geo_utils as geo_utils
import math
from sentinelhub import BBox


def calculate_dimensions(bbox, resolution):
    """
    Calculate the width and height of a bounding box based on a given resolution in decimal degrees.

    Parameters:
        bbox (tuple): A tuple representing the bounding box in the format (min_lon, min_lat, max_lon, max_lat).
        resolution (float): The desired resolution in decimal degrees.

    Returns:
        tuple: A tuple containing the width and height in pixels.
    """
    min_lon, min_lat, max_lon, max_lat = bbox

    # Calculate the width and height in degrees
    width_deg = max_lon - min_lon
    height_deg = max_lat - min_lat

    # Calculate the width and height in pixels
    width_px = int(width_deg / resolution)
    height_px = int(height_deg / resolution)

    return width_px, height_px

def _meters_to_decimal_degrees(meters, latitude=None, direction='lat'):
    """
    Convert a distance in meters to an equivalent value in decimal degrees.
    
    For latitude, the conversion is roughly constant (~111,320 meters per degree).
    For longitude, the conversion factor decreases with latitude:
    
        degrees_lon ≈ meters / (111320 * cos(latitude_in_radians))
    
    Parameters:
        meters (float): Distance in meters.
        latitude (float, optional): Latitude in decimal degrees, required for longitude conversion.
        direction (str): 'lat' for latitude or 'lon' for longitude conversion. Default is 'lat'.
        
    Returns:
        float: The equivalent distance in decimal degrees.
    
    Raises:
        ValueError: If direction is 'lon' and no latitude is provided,
                    or if an unsupported direction is given.
    """
    # Approximate length of one degree of latitude in meters
    deg_lat_meters = 111320.0

    if direction.lower() == 'lat':
        return meters / deg_lat_meters
    elif direction.lower() == 'lon':
        if latitude is None:
            raise ValueError("Latitude must be provided for longitude conversion.")
        # Convert latitude to radians for the cosine function
        lat_rad = math.radians(latitude)
        # Length of one degree of longitude (in meters) varies with latitude:
        deg_lon_meters = deg_lat_meters * math.cos(lat_rad)
        return meters / deg_lon_meters
    else:
        raise ValueError("Direction must be 'lat' or 'lon'.")
    

def get_resolution_degree_from_meters(bounding_box : BBox, resolution:float):
    """
    Calculate the latitudinal and longitudinal resolution in degrees based on a given resolution in meters.

    Args:
        resolution (float): The ground resolution in meters.
        bounding_box (BBox): An object representing the bounding box for the area.
            The midpoint of this bounding box is used to determine the longitudinal conversion.

    Returns:
        tuple:
            - float: Latitudinal resolution in degrees.
            - float: Longitudinal resolution in degrees.
    """
    lat = _meters_to_decimal_degrees(resolution, 'lat')
    lon = _meters_to_decimal_degrees(resolution, bounding_box.middle[0], 'lon')
    return (lat, lon)



def get_valid_resolution(bounding_box : BBox, resolution,max_pixels=2500):
    lon,lat = get_resolution_degree_from_meters(bounding_box,resolution)
    calculated_dim = calculate_dimensions(bounding_box,lon)
    #TODO : Fix the resolution with a function and not with a recursive call
    if calculated_dim[0] > max_pixels or calculated_dim[1] > max_pixels:
        return get_valid_resolution(bounding_box,resolution+1,max_pixels)
    return resolution