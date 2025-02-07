from setuptools import find_packages, setup

setup(
    name='geotiff_reader',
    packages=find_packages(),
    version='0.1.0',
    description='Package for reading geotiff files',
    url = 'https://github.com/cl3t4p/sat_hub',
    author='cl3t4p',
    license='MIT',
    include_package_data=True,
    install_requires=[
        'bottle==0.13.2',
    ],
    entry_points = {
        'console_scripts': ['geotiff_reader=geotiff_reader.map_server:main'],
    }
)
