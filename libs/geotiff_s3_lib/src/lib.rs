use image::{GenericImageView, ImageBuffer, Rgb};
use ndarray::{Array2};
use numpy::{PyArray2, IntoPyArray};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;


#[pyfunction]
fn generate_image(py: Python, matrix: &PyArray2<f64>, output_path: &str) {
    
}