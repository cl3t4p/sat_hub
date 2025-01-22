use image::{GenericImageView, ImageBuffer, Rgb};
use ndarray::{Array2};
use numpy::{PyArray2, IntoPyArray, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn get_percentage_matrix(py: Python, matrix: PyReadonlyArray2<i32>, radius: usize) -> PyArray2<f64> {
    let matrix = matrix.as_array();
    let height = matrix.shape()[0];
    let width = matrix.shape()[1];
    let mut percentage_matrix = Array2::<f64>::zeros((height, width));

    let total_pixel = height * width;
    let mut last_progress: isize = -1;

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
            if progress as isize > last_progress {
                println!("Progress: {}%", progress);
                last_progress = progress as isize;
            }
        }
    }

    percentage_matrix.into_pyarray(py).unbind().
`}


fn closest_color(pixel: Rgb<u8>, colors: &[(u8, u8, u8)]) -> Rgb<u8> {
    let mut min_dist = f32::MAX;
    let mut closest_color = Rgb([0, 0, 0]);
    for &color in colors.iter() {
        let dist = ((pixel[0] as f32 - color.0 as f32).powi(2)
            + (pixel[1] as f32 - color.1 as f32).powi(2)
            + (pixel[2] as f32 - color.2 as f32).powi(2))
            .sqrt();
        if dist < min_dist {
            min_dist = dist;
            closest_color = Rgb([color.0, color.1, color.2]);
        }
    }
    closest_color
}

#[pyfunction]
fn convert_image_to_4_colors(input_path: &str, output_path: &str) {
    println!("Image Conversion...");

    // Read the image
    let img = image::open(input_path).expect("Could not open or find the image");
    let (width, height) = img.dimensions();
    let mut img = img.to_rgb8();

    let total_pixel = width * height;
    let mut last_progress: isize = -1;

    // Define the target colors
    let colors = [
        (255, 0, 0),    // red
        (0, 255, 0),    // green
        (0, 128, 255),  // blue
        (255, 255, 255) // white
    ];

    // Approximate each pixel to the closest color
    for (i, pixel) in img.pixels_mut().enumerate() {
        let new_color = closest_color(*pixel, &colors);
        *pixel = new_color;

        // Print progress percentage
        let progress = (i as u32 * 100 / total_pixel) as i32;
        if progress as isize > last_progress {
            print!("Progress: {}%\r", progress);
            last_progress = progress as isize;
        }
    }

    // Save the image in TIFF format
    img.save(output_path).expect("Could not save image");
    println!("\nImage saved successfully");
}

#[pyfunction]
fn generate_image(py: Python, matrix: PyReadonlyArray2<f64>, output_path: &str) {
    let matrix = matrix.as_array() ;
    let height = matrix.shape()[0];
    let width = matrix.shape()[1];

    // Create an empty image buffer with white background (u8 data type)
    let mut img: ImageBuffer<Rgb<u8>, Vec<u8>> = ImageBuffer::new(width as u32, height as u32);

    let thresholds = [20.0, 40.0, 60.0, 80.0, 100.0];
    let colors = [
        Rgb([255, 0, 0]),
        Rgb([255, 128, 0]),
        Rgb([255, 255, 0]),
        Rgb([128, 255, 0]),
        Rgb([0, 255, 0]),
    ];

    let total_pixel = height * width;
    let mut last_progress = -1;

    for (y, row) in matrix.outer_iter().enumerate() {
        for (x, &value) in row.iter().enumerate() {
            let mut color = colors[0];
            for (i, &threshold) in thresholds.iter().enumerate() {
                if value <= threshold {
                    color = colors[i];
                    break;
                }
            }
            img.put_pixel(x as u32, y as u32, color);

            let progress = ((y * width + x) * 100 / total_pixel) as i32;
            if progress > last_progress {
                println!("Progress: {}%", progress);
                last_progress = progress;
            }
        }
    }

    // Save the image in PNG format
    img.save(output_path).expect("Failed to save the image");
    println!("Image saved successfully to {}", output_path);
}



#[pymodule]
fn sat_img_processing(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_percentage_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(convert_image_to_4_colors, m)?)?;
    m.add_function(wrap_pyfunction!(generate_image, m)?)?;
    Ok(())
}