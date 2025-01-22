
from sat_product.sentinel.basetype_sent import SentinelBaseType
from sentinelhub import MimeType, SentinelHubRequest, bbox_to_dimensions, DataCollection


class Test(SentinelBaseType):
    def __init__(self, config: dict):
        super().__init__(config)
        
    def process(self):
        # Define area of interest
        resolution = 10  # Sentinel-2 resolution in meters
        size = bbox_to_dimensions(self.bbox, resolution=resolution)

        # Define custom script for RGB
        evalscript_rgb = """
            // Custom RGB script
            function setup() {
                return {
                    input: ["B04", "B03", "B02"],
                    output: { bands: 3 }
                };
            }

            function evaluatePixel(samples) {
                return [samples.B04, samples.B03, samples.B02];
            }
        """

        # Create Sentinel Hub request
        request = SentinelHubRequest(
            evalscript=evalscript_rgb,
            input_data=[SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=('2023-01-01', '2023-12-31')
            )],
            responses=[SentinelHubRequest.output_response('default', MimeType.PNG)],
            bbox=self.bbox,
            size=size,
            config=self.config
        )

        # Get the response
        image = request.get_data()[0]

        # Visualize or analyze the image
        import matplotlib.pyplot as plt
        plt.imshow(image)
        plt.title("Tree Crown Colors (RGB)")
        plt.show()

    def get_evalscript(self):
        return super().get_evalscript()
    
    def get_input_type(self):
        return [
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,     
                    time_interval=(self.timeIntervalStart, self.timeIntervalEnd),
                    other_args={"dataFilter": {"maxCloudCoverage": self.maxCloudCoverage}}
                ),
            ]