# Sat Hub

Sat Hub is a Python-based project designed to process and analyze satellite imagery data. It supports various satellite data products and provides functionalities for downloading, processing, and visualizing satellite images.

## Table of Contents

- [Installation](#installation)
- [Example](#example)
- [GeoTIFF_Reader](#geotiff_reader)
- [Produtcs](#products)
- [PackageInstall](#packageinstall)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/cl3t4p/sat_hub.git
    cd sat_hub
    ```

2. Set up the virtual environment and install dependencies:
    ```sh
    python setup_env.py
    ```

## How to Use

```sh
python main.py --help
```

## Example
Example command for downloading RGB images from SentinelHub:

```sh
python main.py `
    --point1 45.68 10.58 `
    --point2 45.42 10.98 `
    rgb `
    --client_id <CLIENT_ID> `
    --client_secret <CLIENT_SECRET> `
    --start_date "2023-01-01" `
    --end_date "2023-12-31" `
    --cloud_coverage 20
```

## GeoTIFF_Reader
GeoTIFF reader is a tool to read and visualize GeoTIFF files.

After running the `python setup_env.py` command, you can run the GeoTIFF reader tool using the following command:
Usage:
```sh
geotiff_reader <path_to_geotiff_files | path_to_geotiff_file | path_to_directory> 
```
After running the command, go to the browser and open the link `http://127.0.0.1:5000/` to visualize the GeoTIFF file.


## Products
Required parameters for all products
- `--point1` and `--point2` are the coordinates of the bounding box.

Optional parameters for all products:
- `--output` is the output directory | default: 'output/{type}_*date_time*' where *date_time* is a placeholder for the current date and time


### SentinelHub
SentinelHub specific parameters:

Required parameters:
- `--client_id` is the client ID
- `--client_secret` is the client secret
- `--start_date` is the start date
- `--end_date` is the end date

Optional parameters:
- `--cloud_coverage` is the maximum cloud coverage | default: 20
- `--resolution` is the resolution of the image | default: is the maximum resolution available within the bounding box as SentinelHub has a limit of 2500 pixels for the width and height

----

- RGB (Sentinel-2)
    - Optional parameters:
        - `--brightness` is the brightness of the image | default: 2.5
- ESA WorldCover
    - PDF 
        - [PDF_V1](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v100/2020/docs/WorldCover_PUM_V1.0.pdf)
        - [PDF_V2](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PUM_V2.0.pdf)
    - Optional parameters:
        - `--version` is the version of data v1 (2020) or v2 (2021) | default: 2
        - `--disable_cache` to disable the cache | default: False

- GProx


## GProx
- Required parameters:
    - `--meter_radius` is the radius of the kernel
- Optional parameters:
    - `--value_map` is the value map in the form of "value1,weight1 value2,weight2" | default: predefined for each compatible product

## Local
- Local_GProx
    - Required parameters:
        - `--path` is the path to the image
        - `--meter_radius` is the radius of the kernel
        - `--value_to_map` is the value to map | default: 1

-----

## PackageInstall
#### Sat Hub Lib
Installation of `sat_hub_lib` package on your local machine for development.

0. Install the setuptools
    ```sh
    pip install setuptools
    ```

1. Clone the repository:
    ```sh
    git clone https://github.com/cl3t4p/sat_hub.git
    cd libs/base_sat_hub_lib
    ```

2. Install the package:
    ```sh
    python setup.py install
    ```

Now you can use the `sat_hub_lib` package in your project.

#### GeoTIFF Reader
Installation of `GeoTIFF_Reader` package on your local machine.

0. Install the setuptools
    ```sh
    pip install setuptools
    ```

1. Clone the repository:
    ```sh
    git clone https://github.com/cl3t4p/sat_hub.git
    cd libs/base_geotiff_reader
    ```

2. Install the package:
    ```sh
    python setup.py install
    ```