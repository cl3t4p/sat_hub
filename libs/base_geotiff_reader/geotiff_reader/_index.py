html_file = '''
<!DOCTYPE html>
<html>

<head>
    <title>GeoTIFF Viewer</title>
    <!-- Include Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <!-- Include Leaflet JS -->
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

    <!-- Include GeoRaster Layer for Leaflet -->
    <script src="https://cdn.jsdelivr.net/npm/georaster/dist/georaster.browser.bundle.min.js"></script>
    <script src="https://unpkg.com/georaster-layer-for-leaflet/dist/georaster-layer-for-leaflet.min.js"></script>
    <style>
        html,
        body,
        #map {
            height: 100%;
            margin: 0;
            padding: 0;
        }

        #slider {
            position: absolute;
            align-items:start;
            text-align: center;
            bottom: 2rem;
            display: block;
            right: 10px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        }

        .sliders {
            margin: 5px;
            display: flex;
        }
    </style>
</head>

<body>
    <!-- Map container -->
    <div id="map"></div>

    <!-- Slider for opacity control -->
    <div id="slider">
    {% for geotiff in geotiffs %}
        <div class="sliders">
            <input type="range" min="0" max="1" step="0.01" value="1" id="opacityRange-{{ loop.index0 }}">
            <label for="opacityRange-{{ loop.index0 }}">Opacità GeoTIFF {{ geotiff }}</label>
        </div>
    {% endfor %}

        <label for="resolution">Risoluzione: </label>
        <input type="number" id="resolution" min="1" value="256">
        <button id="applyResolution">Applica</button>
    </div>


    <script>


        function setGeotiffLayer(){
            elements =  document.getElementsByClassName('leaflet-control-layers-selector')
            for (var i = 0; i < elements.length; i++) {
                if (elements[i].type == 'checkbox'){
                    if (elements[i].checked == false)
                        elements[i].click();
                }
            }
        }



        var baseMaps = {
            "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 20,
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            })
        };




        // Initialize the map
        var map = L.map('map', {
            zoom: {{ zoom }},
            layers: [baseMaps.OpenStreetMap]
        });

        map.setView([45.68, 10.58], 10);


        var layerControl = L.control.layers(baseMaps, {}, {
            collapsed: false
        }).addTo(map);


        L.control.scale({
            imperial: false
        }).addTo(map);




        function addGeotiffLayer(geotiff_id,layer_name) {
            
        // Fetch and load the GeoTIFF file
        fetch(`get_geotiff/${geotiff_id}`)
            .then(response => response.arrayBuffer())
            .then(arrayBuffer => {
                parseGeoraster(arrayBuffer).then(georaster => {
                    var resolution = document.getElementById('resolution').value;
                    var opacity = document.getElementById(`opacityRange-${geotiff_id}`).value;
                    var layer = new GeoRasterLayer({
                        georaster: georaster,
                        opacity: opacity,
                        resolution: resolution
                    });

                    document.getElementById(`opacityRange-${geotiff_id}`).addEventListener('input', function (e) {
                        var opacity = e.target.value;
                        layer.setOpacity(opacity);
                    });
                    map.fitBounds(layer.getBounds());

                    layerControl.addOverlay(layer, layer_name);
                    console.log("Just added layer", layer_name);

                });
            });
        }

        function reloadGeotiffLayer() {
            {% for geotiff in geotiffs %}
                addGeotiffLayer({{ loop.index0 }}, '{{ geotiff }}');
            {% endfor %}
        }


        document.getElementById('applyResolution').addEventListener('click', function (e) {
            var resolution = document.getElementById('resolution').value;
            //Remove the layer and add it again with the new resolution

            map.eachLayer(function (l) {
                if (l instanceof GeoRasterLayer) {
                    map.removeLayer(l);
                }
            });
            reloadGeotiffLayer();
        });

        reloadGeotiffLayer();

        // URL to the GeoTIFF file

    </script>

</body>

</html>
'''