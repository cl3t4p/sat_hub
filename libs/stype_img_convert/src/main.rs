use image::{GenericImageView, Rgb};
use std::f32;

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
    img.save(output_path).expect("Could not save the image");
    println!("\nImage saved successfully");
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        println!("Usage: {} <input_image> <output_image>", args[0]);
        return;
    }

    convert_image_to_4_colors(&args[1], &args[2]);
}