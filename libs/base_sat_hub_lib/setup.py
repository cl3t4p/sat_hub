from setuptools import find_packages, setup

setup(
    name='sat_hub',
    packages=find_packages(),
    version='0.1.0',
    description='Package for downloading and extracting data from various sources',
    url = 'https://github.com/cl3t4p/sat_hub',
    author='cl3t4p',
    license='MIT',
    install_requires=[
        'boto3==1.36.3',
        'numpy==1.26.4',
        'rasterio==1.4.3',
        'shapely==2.0.6',
        'scipy==1.15.1',
        'pillow==11.1.0',
        'sentinelhub==3.11.0'
    ],
)
