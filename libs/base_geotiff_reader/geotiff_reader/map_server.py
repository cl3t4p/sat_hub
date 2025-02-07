from . import _index
import bottle
from jinja2 import Template
import sys
import os

geotiffs = {}

@bottle.route('/')
def index():
    print(f'Keys: {bottle.json_dumps(list(geotiffs.keys()))}')
    template = Template(_index.html_file)
    
    return template.render(geotiffs=list(geotiffs.keys()),
                           zoom=17)


@bottle.route('/get_geotiff/<id:int>')
def get_geotiff(id):
    array = list(geotiffs.keys())
    if id < 0 or id >= len(array):
        bottle.response.status = 404
        return "File not found"
    name = array[id]
    bottle.response.content_type = 'image/tiff'
    bottle.response.headers['Content-Disposition'] = f'inline; filename="{name}"'
    
    return geotiffs[name]


def run_server(input_files):
    for i in input_files:
        with open(i, 'rb') as f:
            if '\\' in i:
                name = i.split('\\')[-1]
            else:
                name = i.split('/')[-1]
            if name in geotiffs:
                name = '01_' + name 
            geotiffs[name] = f.read()
    bottle.run(port=5000,debug=True)
    




def main():
    if len(sys.argv) < 2:
        print("No input geotiff files or folders provided")
        exit()
    input_files = sys.argv[1:]
    for i in input_files:
        if not os.path.exists(i):
            print(f"File or Folder {i} does not exist")
            exit()
        if os.path.isdir(i):
            for f in os.listdir(i):
                if f.endswith(".tif"):
                    input_files.append(f)
                    

    run_server(input_files)