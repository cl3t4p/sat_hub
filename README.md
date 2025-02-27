# Sat Hub

Sat Hub is a Python-based project designed to process and analyze satellite imagery data. It supports various satellite data products and provides functionalities for downloading, processing, and visualizing satellite images.

## Table of Contents

- [Installation](#installation)
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

## GeoTIFF_Reader
GeoTIFF reader simple web page to visualize GeoTIFF files.

Usage:
```sh
Open in any browser the file `geotiff_reader.html`
```

## Products
- [RGB](https://github.com/cl3t4p/sat_hub/wiki/Products#RGB)
- [Landcover](https://github.com/cl3t4p/sat_hub/wiki/Products#Landcover)
- [S3_ESAWorldCover](https://github.com/cl3t4p/sat_hub/wiki/Products#S3_ESAWorldCover)
- [Sentinel_GProx](https://github.com/cl3t4p/sat_hub/wiki/Products#Sentinel_GProx)
- [S3_GProx](https://github.com/cl3t4p/sat_hub/wiki/Products#S3_GProx)
- [Local_GEOTiff](https://github.com/cl3t4p/sat_hub/wiki/Products#Local_GEOTiff)

## PackageInstall
### Sat Hub Lib [Link](https://github.com/cl3t4p/sat_hub_lib)
Installation of `sat_hub_lib` package on your local machine for development.

0. Install the setuptools
    ```sh
    pip install setuptools
    ```

1. Clone the repository:
    ```sh
    git clone https://github.com/cl3t4p/sat_hub.git
    cd libs/sat_hub_lib
    ```

2. Install the package:
    ```sh
    python setup.py install
    ```

Now you can use the `sat_hub_lib` package in your project.