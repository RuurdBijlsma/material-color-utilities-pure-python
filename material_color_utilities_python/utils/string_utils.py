# /**
#  * Utility methods for hexadecimal representations of colors.
#  */
# /**
#  * @param argb ARGB representation of a color.
#  * @return Hex string representing color, ex. #ff0000 for red.
#  */
from material_color_utilities_python.utils.color_utils import (
    red_from_argb,
    green_from_argb,
    blue_from_argb,
    rshift,
)


def hex_from_argb(argb):
    r = red_from_argb(argb)
    g = green_from_argb(argb)
    b = blue_from_argb(argb)
    out_parts = [f'{r:x}', f'{g:x}', f'{b:x}']
    # Pad single-digit output values
    for i, part in enumerate(out_parts):
        if len(part) == 1:
            out_parts[i] = '0' + part
    return '#' + ''.join(out_parts)

# /**
#  * @param hex String representing color as hex code. Accepts strings with or
#  *     without leading #, and string representing the color using 3, 6, or 8
#  *     hex characters.
#  * @return ARGB representation of color.
#  */
def parse_int_hex(value):
    # tslint:disable-next-line:ban
    return int(value, 16)

def argb_to_css_rgba(argb_int):
    # Extract alpha, red, green, and blue components
    alpha = (argb_int >> 24) & 0xFF
    red = (argb_int >> 16) & 0xFF
    green = (argb_int >> 8) & 0xFF
    blue = argb_int & 0xFF

    # Convert alpha to a value between 0 and 1
    alpha_normalized = alpha / 255

    # Return the CSS rgba() string
    return f"rgba({red}, {green}, {blue}, {alpha_normalized})"

def argb_from_hex(hex_color):
    hex_color = hex_color.replace('#', '')
    is_three = len(hex_color) == 3
    is_six = len(hex_color) == 6
    is_eight = len(hex_color) == 8
    if not is_three and not is_six and not is_eight:
        raise Exception('unexpected hex ' + hex_color)

    r = 0
    g = 0
    b = 0
    if is_three:
        r = parse_int_hex(hex_color[0:1]*2)
        g = parse_int_hex(hex_color[1:2]*2)
        b = parse_int_hex(hex_color[2:3]*2)
    elif is_six:
        r = parse_int_hex(hex_color[0:2])
        g = parse_int_hex(hex_color[2:4])
        b = parse_int_hex(hex_color[4:6])
    elif is_eight:
        r = parse_int_hex(hex_color[2:4])
        g = parse_int_hex(hex_color[4:6])
        b = parse_int_hex(hex_color[6:8])

    return rshift(((255 << 24) | ((r & 0x0ff) << 16) | ((g & 0x0ff) << 8) | (b & 0x0ff)), 0)
