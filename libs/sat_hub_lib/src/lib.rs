use gdal::raster::Buffer;
use gdal::{Driver, DriverManager};
use pyo3::prelude::*;
use gdal::{Dataset, raster::RasterBand};
use gdal::errors::GdalError;
use std::path::Path;

#[pyfunction]
fn combine_geotiffs_with_box(
    input_paths: Vec<String>,
    bbox: (f64, f64, f64, f64),
    output_path: String,
) -> PyResult<()> {
    let mut datasets = Vec::new();

    // Load all input datasets
    for path in &input_paths {
        match Dataset::open(Path::new(path)) {
            Ok(dataset) => datasets.push(dataset),
            Err(err) => return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("GDAL error: {:?}", err))),
        }
    }

    let (min_x, min_y, max_x, max_y) = bbox;

    // Determine the spatial reference and initialize the output dataset
    let spatial_ref = datasets[0].spatial_ref().map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("GDAL error: {:?}", err)))?;
    let driver = DriverManager::get_driver_by_name("GTiff").unwrap();
    let mut output_dataset = driver.create(
        &output_path,
        datasets[0].raster_size().0,
        datasets[0].raster_size().1,
        datasets[0].raster_count() as usize,
    ).map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("GDAL error: {:?}", err)))?;

    output_dataset.set_spatial_ref(&spatial_ref);

    for dataset in datasets {
        let transform = dataset.geo_transform()
            .map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("GDAL error: {:?}", err)))?;
        let pixel_size_x = transform[1];
        let pixel_size_y = transform[5];
        let origin_x = transform[0];
        let origin_y = transform[3];

        let x_offset = ((min_x - origin_x) / pixel_size_x).floor() as usize;
        let y_offset = ((min_y - origin_y) / pixel_size_y).floor() as usize;

        let x_end = ((max_x - origin_x) / pixel_size_x).ceil() as usize;
        let y_end = ((max_y - origin_y) / pixel_size_y).ceil() as usize;

        let x_size = x_end - x_offset;
        let y_size = y_end - y_offset;

        for band_index in 1..=dataset.raster_count() {
            let input_band = dataset.rasterband(band_index)
                .map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("GDAL error: {:?}", err)))?;
            let mut buffer = vec![0u8; x_size * y_size];
            let mut buffer: Buffer<u8> = input_band.read_as((x_offset as isize, y_offset as isize), (x_size, y_size), (x_size, y_size), None)
                .map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("GDAL error: {:?}", err)))?;

            let output_band = output_dataset.rasterband(band_index)
                .map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("GDAL error: {:?}", err)))?;
            output_band.write((x_offset as isize, y_offset as isize), (x_size, y_size), &mut &buffer)
                .map_err(|err| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("GDAL error: {:?}", err)))?;
        }
    }

    Ok(())
}




/// A Python module implemented in Rust.
#[pymodule]
fn sat_hub_lib(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(combine_geotiffs_with_box, m)?)?;
    Ok(())
}
