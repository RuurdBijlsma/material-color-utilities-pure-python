# /**
#  * Get the source color from an image.
#  *
#  * @param image The image element
#  * @return Source color - the color most suitable for creating a UI theme
#  */

from material_color_utilities_python.quantize.quantizer_celebi import QuantizerCelebi
from material_color_utilities_python.score.score import Score
from material_color_utilities_python.utils.color_utils import argb_from_rgb


def get_argb_pixels(image):
    pixels = []
    # Load the image as a 2D array of RGBA values
    img_data = image.convert("RGBA").load()

    # Loop through every pixel directly
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = img_data[x, y]  # Get the RGBA values directly
            if a < 255:
                continue
            argb = argb_from_rgb(r, g, b)
            pixels.append(argb)

    return pixels


def source_color_from_image(image):
    # profiler = Profiler()
    # profiler.start()

    pixels = get_argb_pixels(image)

    # // Convert Pixels to Material Colors
    result = QuantizerCelebi.quantize(pixels, 128)
    ranked = Score.score(result)
    top = ranked[0]

    # profiler.stop()
    # profiler.open_in_browser()
    return top
