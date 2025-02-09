from sat_hub_lib.sentinel import SentinelBaseType
import sat_hub_lib.utils.geotiff_lib as geotiff_lib
from sentinelhub import SentinelHubRequest, DataCollection


class NDVI(SentinelBaseType):

    def __init__(self, args: dict):
        super().__init__(args)
        

    def write_geotiff(self, output_file: str = None):
        if output_file is None:
            output_file = f"{self.get_outfolder()}/ndvi.tif"
        super().write_geotiff(output_file)
        # Apply the color map
        geotiff_lib.apply_colormap(output_file, self.get_color_map())

    def extract_bandmatrix(self):
        return super().extract_bandmatrix()

    def _get_input_type(self):
        return [
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(self.timeIntervalStart, self.timeIntervalEnd),
                other_args={"dataFilter": {"maxCloudCoverage": self.cloud_coverage}},
            ),
        ]

    def _get_evalscript(self) -> str:
        return """
/// Normalizes NDVI from [-0.5, 1] to [0, 150]
function setup() {
    return {
        input: ["B08", "B04"],
        output: { bands: 1, sampleType: "UINT8" }
    };
}

function evaluatePixel(sample) {
    let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
    
    // Normalize NDVI from [-0.5, 1] to [0, 150]
    let normalized_ndvi = Math.round(((ndvi + 0.5) / 1.5) * 150);

    return [normalized_ndvi];
}
"""
    color_ramp = [
        (0, 0x0c0c0c),
        (30, 0xbfbfbf),
        (40, 0xdbdbdb),
        (50, 0xeaeaea),
        (53, 0xfff9cc),
        (55, 0xede8b5),
        (58, 0xddd89b),
        (60, 0xccc682),
        (63, 0xbcb76b),
        (65, 0xafc160),
        (68, 0xa3cc59),
        (70, 0x91bf51),
        (75, 0x7fb247),
        (80, 0x70a33f),
        (85, 0x609635),
        (90, 0x4f892d),
        (95, 0x3f7c23),
        (100, 0x306d1c),
        (105, 0x216011),
        (110, 0x0f540a),
        (150, 0x004400),
    ]

    def get_color_map(self):
        return geotiff_lib.generate_colormap(self.color_ramp)