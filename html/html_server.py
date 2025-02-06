from flask import Flask, Response, render_template, send_file, jsonify
from io import BytesIO
from PIL import Image
import os
import argparse

import rasterio

app = Flask(__name__, template_folder="templates")
app.config['TEMPLATES_FOLDER'] = "templates"

data_file = BytesIO()
input_file = None
bounds = None


def extract_content_from_geotiff(geotiff_path):
    image = Image.open(geotiff_path)
    image.save(data_file, format="PNG")
    with rasterio.open(geotiff_path) as src:
        global bounds
        bounds = src.bounds


@app.route('/')
def index():
    mitpoint_lat = (bounds.top + bounds.bottom) / 2
    mitpoint_lon = (bounds.left + bounds.right) / 2
    return render_template('index.jinja', 
                           lonNW=bounds.left, 
                           lonSE=bounds.right, 
                           latNW=bounds.top, 
                           latSE=bounds.bottom, 
                           middle_lat=mitpoint_lat, 
                           middle_lon=mitpoint_lon,
                           zoom=13)


@app.route('/data.png')
def get_data():
    return Response(data_file.getvalue(), mimetype='image/png', direct_passthrough=True)
@app.route('/data.tif')
def get_data_tif():
    data_file = open(input_file, 'rb').read()
    return Response(data_file, mimetype='image/tiff', direct_passthrough=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--input_file", required=True,
                        help="Path to the geotiff file")
    args = parser.parse_args()
    input_file = args.input_file
    extract_content_from_geotiff(input_file)
    app.run(debug=True)
