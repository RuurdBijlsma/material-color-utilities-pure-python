from pathlib import Path

import PIL.Image

from material_color_utilities_python import (
    argb_from_hex,
    hex_from_argb,
    source_color_from_image,
    theme_from_source_color,
)


def test_theme_from_color():
    color = "#4285f4"
    theme = theme_from_source_color(argb_from_hex(color))
    assert len(theme.custom_colors) == 0
    hex_source = hex_from_argb(theme.source)
    assert hex_source == color


def test_color_from_image(assets_folder: Path):
    img = PIL.Image.open(assets_folder / "image.jpg")
    argb = source_color_from_image(img)

    print(hex_from_argb(argb))
    print(assets_folder)
