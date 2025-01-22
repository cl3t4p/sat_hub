use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::fs::File;
use tiff::decoder::{Decoder, DecodingResult};
use tiff::encoder::{colortype::Gray16, TiffEncoder};

/// Combines multiple GeoTIFFs by extracting a region specified by a bounding box and writing to a single output GeoTIFF.
///
/// # Arguments
/// - `input_paths`: A vector of paths to input GeoTIFF files.
/// - `bounding_box`: A tuple specifying the bounding box (x_min, y_min, x_max, y_max) in pixels.
/// - `output_path`: The path for the output GeoTIFF file.
///
/// # Returns
/// A result indicating success or failure.
#[pyfunction]
fn combine_geotiffs_with_box(
    input_paths: Vec<String>,
    bounding_box: (u32, u32, u32, u32),
    output_path: String,
) -> PyResult<bool> {
    let (x_min, y_min, x_max, y_max) = bounding_box;
    let mut combined_data = Vec::new();

    for input_path in input_paths {
        let file = File::open(&input_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        let mut decoder = Decoder::new(file)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        let (width, height) = decoder
            .dimensions()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        if x_max > width || y_max > height {
            return Ok(false);
        }

        if let DecodingResult::U16(data) = decoder
            .read_image()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?
        {
            let mut cropped = Vec::new();
            for y in y_min..y_max {
                let start = (y * width + x_min) as usize;
                let end = (y * width + x_max) as usize;
                cropped.extend_from_slice(&data[start..end]);
            }
            combined_data.push(cropped);
        } else {
            return Ok(false);
        }
    }

    // Write the combined data to a new GeoTIFF
    let output_file = File::create(output_path)?;
    let mut encoder = TiffEncoder::new(output_file)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    let combined_width = x_max - x_min;
    let combined_height = (y_max - y_min) * (combined_data.len() as u32);
    encoder
        .write_image::<Gray16>(combined_width, combined_height, &combined_data.concat())
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

    Ok(true)
}

/// Python module definition
#[pymodule]
fn geotiff_s3_lib(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(combine_geotiffs_with_box, m)?)?;
    Ok(())
}
