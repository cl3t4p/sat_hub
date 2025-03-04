import arguments
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



from sat_hub_lib.sentinel import SentinelBaseSettings


output_file = getattr(args, "output", None)
sentinel_conf = {
    "client_id": getattr(args, "client_id", None),
    "client_secret": getattr(args, "client_secret", None),
    "start_date": getattr(args, "start_date", None),
    "end_date": getattr(args, "end_date", None),
    "cloud_coverage": getattr(args, "cloud_coverage", None),
    "resolution": getattr(args, "resolution", None),
    "point1": getattr(args, "point1", None),
    "point2": getattr(args, "point2", None),
    "output_file": output_file,
}

value_map = arguments.get_value_map(args.value_map) if hasattr(args, "value_map") else None

match args.type:
    case "ndvi":
        from sat_hub_lib.sentinel import NDVI, SentinelBaseSettings

        config = SentinelBaseSettings(**sentinel_conf)
        product = NDVI(config)
        product.write_geotiff()
    case "sentinel_gprox":
        from sat_hub_lib.sentinel import Landcover
        from sat_hub_lib.extension import GProx

        config = SentinelBaseSettings(**sentinel_conf)
        product = Landcover(config,args.ndwi_threshold,
                                        args.ndvi_grass_min,
                                        args.ndvi_trees_min,
                                        args.ndbi_building_min)
        gprox = GProx(product, args.meter_radius, value_map, args.omega,args.function, output_file)
        gprox.write_geotiff()
    case "landcover":
        from sat_hub_lib.sentinel import Landcover

        config = SentinelBaseSettings(**sentinel_conf)
        product = Landcover(config,args.ndwi_threshold,
                                        args.ndvi_grass_min,
                                        args.ndvi_trees_min,
                                        args.ndbi_building_min)
        product.write_geotiff()
    case "vis":
        from sat_hub_lib.sentinel.vis import Vis

        config = SentinelBaseSettings(**sentinel_conf)
        product = Vis(config)
        product.write_geotiff()
    case "rgb":
        from sat_hub_lib.sentinel import RGB

        config = SentinelBaseSettings(**sentinel_conf)
        product = RGB(config)
        product.write_geotiff()
    case "stemp":
        from sat_hub_lib.sentinel import STemp

        config = SentinelBaseSettings(**sentinel_conf)
        product = STemp(config)
        product.write_geotiff()
    case "s3_esaworldcover":
        from sat_hub_lib.geotiff.s3 import S3_EsaWorldCover
        product = S3_EsaWorldCover(
            args.point1,
            args.point2,
            args.version,
            "cache",
            args.disable_cache,
            output_file,
        )
        product.write_geotiff()
    case "s3_gprox":
        from sat_hub_lib.geotiff.s3 import S3_EsaWorldCover
        from sat_hub_lib.extension import GProx

        product = S3_EsaWorldCover(
            args.point1,
            args.point2,
            args.version,
            "cache",
            args.disable_cache,
            output_file,
        )
        gprox = GProx(product, args.meter_radius, value_map, args.omega,args.function, output_file)
        gprox.write_geotiff()
    case "file_gprox":
        from sat_hub_lib.geotiff import Local_GeoTiff
        from sat_hub_lib.extension import GProx

        product = Local_GeoTiff(
            
            args.input_file, args.point1, args.point2, (args.resolution[0],args.resolution[1]), output_file
        )
        gprox = GProx(product, args.meter_radius, value_map, args.omega,args.function, output_file)
        gprox.write_geotiff()
    case _:
        log.error(f"Type {args.type} not supported")
        exit()

log.info("Process completed")
