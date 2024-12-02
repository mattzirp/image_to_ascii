from pillow import Image, ImageEnhance 
import os
import numpy as np
import svgwrite

SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg')
MAX_SIZE = 200
DENSITY_STRING = "Ñ@#W$9876543210?!abc;:+=-,. "
SCALE_FACTOR = 10
FONT_FAMILY = "Courier, monospace"
ENHANCEMENT_FACTOR = 1.5
INPUT_DIRECTORY = "input/"
OUTPUT_DIRECTORY = "output/"

def load_image(file_path: str) -> Image.Image:
     """
     Load image from the specified file path and convert into
     RGB color values.
     """
     with Image.open(file_path) as img:
          return img.convert('RGB')
     

def load_images_from_directory(directory: str) -> tuple[list[str], list[Image.Image]]:
    """
    Load all images from the specified directory and return them in a list.
    """
    file_names: list[str] = []
    images: list[Image.Image] = []
    for file_name in os.listdir(directory):
         if file_name.lower().endswith(SUPPORTED_FORMATS):
              file_path = os.path.join(directory, file_name)
              image = load_image(file_path)
              file_names.append(file_name)
              images.append(image)
         else:
             raise TypeError("This file type is not supported.")
    return file_names, images


def resize_image(image: Image.Image, max_size: int = MAX_SIZE) -> Image.Image:
     """
     Resize an image to fit within a bounding box of max_size, while maintaining the 
     original aspect ratio.
     """
    # Determine orientation of the image. The longer side will be scaled to max_size
    # and the other side will be scaled proportionally, to maintain aspect ratio.
     width, height = image.size
     if width > height:
          scale_factor = max_size / width
     else: 
          scale_factor = max_size / height
     new_size = (int(width * scale_factor), int(height * scale_factor))
     return image.resize(new_size, Image.Resampling.LANCZOS)


def get_pixel_data(image: Image.Image) -> list[tuple[int, int, int]]:
     """
     Get the pixel data from an image, as a list of tuples (R, G, B)
     """
     return list(image.getdata())


def rgb_to_luminance(pixel_data: list[tuple[int, int, int]]) -> list[int]:
     """
     Convert a list of RGB pixel tuples to a list of luminance values using 
     conversion from W3C for perceived luminance.
     """
     luminance_values = [
          int(0.299 * r + 0.587 * g + 0.114 * b) 
          for r, g, b in pixel_data
          ]
     return luminance_values


def luminance_to_ascii_char(luminance_data: int) -> str:
     """
     Convert a luminance value to the appropriate character from the DENSITY_STRING.
     """
     density_index = int(luminance_data / 255 * (len(DENSITY_STRING) - 1) + 0.5)
     return len(DENSITY_STRING) - density_index - 1


def create_svg(luminance_data: list[int], dimensions: tuple[int, int], file_name: str)->str:
     """
     Create an SVG file that uses luminance to convert to characters in the density string.
     Returns the name of the saved file.
     """
     width, height = dimensions
     scaled_width = SCALE_FACTOR * width
     scaled_height = SCALE_FACTOR * height
     cell_size = max(scaled_width, scaled_height)
     file_name = os.path.join(OUTPUT_DIRECTORY, f"{file_name}.svg")
     dwg: svgwrite.Drawing = svgwrite.Drawing(
          file_name,
          size = (scaled_width, scaled_height),
          profile = 'full'
     )
     dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill="black"))
     for y in range(height):
          for x in range(width):
               x_position = x * cell_size + cell_size // 2
               y_position = y * cell_size + cell_size // 2
               index = y * width + x
               character = luminance_to_ascii_char(luminance_data[index])
               text = dwg.text(
                    character, 
                    insert=(x_position, y_position),
                    text_anchor='middle',
                    dominant_baseline='middle',
                    font_size=cell_size,
                    font_family=FONT_FAMILY,
                    fill="white"
                )
               dwg.add(text)
     dwg.save()
     return file_name

def main():
    file_names, original_images = load_images_from_directory(INPUT_DIRECTORY)
    resized_images = [resize_image(image) for image in original_images]
    contrasted_images = []
    for image in resized_images:
         enhancer = ImageEnhance.Contrast(image)
         enhanced_image = enhancer.enhance(ENHANCEMENT_FACTOR)
         contrasted_images.append(enhanced_image)
    rgb_data = [get_pixel_data(image) for image in contrasted_images]
    luminance_data = [rgb_to_luminance(rgb) for rgb in rgb_data]
    for i in range(len(luminance_data)):
         file_name = create_svg(
              luminance_data[i],
              contrasted_images[i].size,
              file_names[i].split(".")[0],
              )
    print(f"Saved file: {file_name}")

if __name__() == "__main__":
     main()