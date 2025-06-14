# Sat Hub

Sat Hub is a Python-based project designed to process and analyze satellite imagery data. It supports various satellite data products and provides functionalities for downloading, processing, and visualizing satellite images.

## Table of Contents

- [Installation](#installation)
- [GeoTIFF-Reader](#geotiff-reader)
- [Produtcs](#products)
- [Package-Install](#package-install)

## Installation

1. Prerequisite
    ```sh
    sudo apt-get install python3-dev
    sudo dnf install python-devel
    ```

2. Clone the repository:
    ```sh
    git clone --recursive https://github.com/cl3t4p/sat_hub.git
    cd sat_hub
    ```

3. Set up the virtual environment and install dependencies:
    ```sh
    python setup_env.py
    ```

## How to Use

```sh
# Activate the virtual enviroment
. .venv/bin/activate
python main.py --help # or click any of the links below for specific product help
```


## Products
- [RGB](https://github.com/cl3t4p/sat_hub/wiki/RGB)
- [Landcover](https://github.com/cl3t4p/sat_hub/wiki/Landcover)
- [S3_ESAWorldCover](https://github.com/cl3t4p/sat_hub/wiki/S3_ESAWorldCover)
- [Sentinel_GProx](https://github.com/cl3t4p/sat_hub/wiki/Sentinel_GProx)
- [S3_GProx](https://github.com/cl3t4p/sat_hub/wiki/S3_GProx)
- [Local_GEOTiff](https://github.com/cl3t4p/sat_hub/wiki/Local_GProx)

## GeoTIFF-Reader
GeoTIFF reader simple web page to visualize GeoTIFF files.

Usage:
```sh
Open in any browser the file `geotiff_reader.html`
```

## Package-Install
### Sat Hub Lib 
Please refer to the [GitHub Link](https://github.com/cl3t4p/sat_hub_lib)
