use image::{GenericImageView, ImageBuffer, Rgb};
use ndarray::{Array2, Zip};
use numpy::{PyArray2, IntoPyArray};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[derive(Copy, Clone)]
struct Color {
    r: u8,
    g: u8,
    b: u8,
}

const COLORS: [Color; 4] = [
    Color { r: 255, g: 0, b: 0 },    // red
    Color { r: 0, g: 255, b: 0 },    // green
    Color { r: 0, g: 128, b: 255 },  // blue
    Color { r: 255, g: 255, b: 255 } // white
];

fn closest_color(pixel: Rgb<u8>) -> Color {
    let mut min_dist = f32::MAX;
    let mut closest_color = Color { r: 0, g: 0, b: 0 };
    for &color in COLORS.iter() {
        let dist = ((pixel[0] as f32 - color.r as f32).powi(2)
            + (pixel[1] as f32 - color.g as f32).powi(2)
            + (pixel[2] as f32 - color.b as f32).powi(2))
            .sqrt();
        if dist < min_dist {
            min_dist = dist;
            closest_color = color;
        }
    }
    closest_color
}

#[pyfunction]
fn get_percentage_matrix(py: Python, matrix: &PyArray2<i32>, radius: usize) -> Py<PyArray2<f64>> {
    let matrix = matrix.as_array();
    let height = matrix.shape()[0];
    let width = matrix.shape()[1];
    let mut percentage_matrix = Array2::<f64>::zeros((height, width));

    let total_pixel = height * width;
    let mut last_progress = -1;

    for y in 0..height {
        let center_y = y;
        for x in 0..width {
            let mut green_counter = 0;
            let mut total_cells = 0;
            let center_x = x;

            for i in y.saturating_sub(radius)..=(y + radius).min(height - 1) {
                for j in x.saturating_sub(radius)..=(x + radius).min(width - 1) {
                    let distance = (((j as isize - center_x as isize).pow(2) + (i as isize - center_y as isize).pow(2)) as f64).sqrt();
                    if distance <= radius as f64 {
                        total_cells += 1;
                        if matrix[[i, j]] == 1 {
                            green_counter += 1;
                        }
                    }
                }
            }

            let green_percentage = if total_cells == 0 {
                0.0
            } else {
                (green_counter as f64 / total_cells as f64) * 100.0
            };
            percentage_matrix[[y, x]] = green_percentage;

            // Print progress percentage
            let progress = (y * width + x) * 100 / total_pixel;
            if progress > last_progress {
                println!("Progress: {}%", progress);
                last_progress = progress;
            }
        }
    }

    percentage_matrix.into_pyarray(py).to_owned()
}

#[pyfunction]
fn convert_image_to_4_colors(input_path: &str, output_path: &str) {
    println!("Image Conversion...");

    // Read the image
    let img = image::open(input_path).expect("Could not open or find the image");
    let (width, height) = img.dimensions();
    let mut img = img.to_rgb8();

    let total_pixel = width * height;
    let mut last_progress = -1;

    // Approximate each pixel to the closest color
    for (i, pixel) in img.pixels_mut().enumerate() {
        let new_color = closest_color(*pixel);
        *pixel = Rgb([new_color.r, new_color.g, new_color.b]);

        // Print progress percentage
        let progress = (i as u32 * 100 / total_pixel) as i32;
        if progress > last_progress {
            print!("Progress: {}%\r", progress);
            last_progress = progress;
        }
    }

    // Save the image in TIFF format
    img.save(output_path).expect("Could not save image");
    println!("\nImage saved successfully");
}

#[pymodule]
fn stype_img_convert(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(convert_image_to_4_colors, m)?)?;
    m.add_function(wrap_pyfunction!(get_percentage_matrix, m)?)?;
    Ok(())
}