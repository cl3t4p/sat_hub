# Sat Hub

Sat Hub is a Python-based project designed to process and analyze satellite imagery data. It supports various satellite data products and provides functionalities for downloading, processing, and visualizing satellite images.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Available Commands](#available-commands)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/sat_hub.git
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

## Products
Required parameters for all products:
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
    - Optional parameters:
        - `--version` is the version of data v1 (2020) or v2 (2021) | default: 2
        - `--disable_cache` to disable the cache | default: False

- GProx
    - Required parameters:
        - `--meter_radius` is the radius of the kernel
