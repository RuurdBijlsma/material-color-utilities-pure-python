import math

from material_color_utilities_python.utils.math_utils import clamp_int, matrix_multiply

# /**
#  * Color science utilities.
#  *
#  * Utility methods for color science constants and color space
#  * conversions that aren't HCT or CAM16.
#  */
SRGB_TO_XYZ = [
    [0.41233895, 0.35762064, 0.18051042],
    [0.2126, 0.7152, 0.0722],
    [0.01932141, 0.11916382, 0.95034478],
]
XYZ_TO_SRGB = [
    [
        3.2413774792388685,
        -1.5376652402851851,
        -0.49885366846268053,
    ],
    [
        -0.9691452513005321,
        1.8758853451067872,
        0.04156585616912061,
    ],
    [
        0.05562093689691305,
        -0.20395524564742123,
        1.0571799111220335,
    ],
]

WHITE_POINT_D65 = [95.047, 100.0, 108.883]


# /**
#  * Converts a color from RGB components to ARGB format.
#  */
def rshift(val, n):
    return val >> n if val >= 0 else (val + 0x100000000) >> n


def argb_from_rgb(red, green, blue):
    return rshift((255 << 24 | (red & 255) << 16 | (green & 255) << 8 | blue & 255), 0)


# /**
#  * Returns the alpha component of a color in ARGB format.
#  */
def alpha_from_argb(argb):
    return argb >> 24 & 255


# /**
#  * Returns the red component of a color in ARGB format.
#  */
def red_from_argb(argb):
    return argb >> 16 & 255


# /**
#  * Returns the green component of a color in ARGB format.
#  */
def green_from_argb(argb):
    return argb >> 8 & 255


# /**
#  * Returns the blue component of a color in ARGB format.
#  */
def blue_from_argb(argb):
    return argb & 255


# /**
#  * Returns whether a color in ARGB format is opaque.
#  */
def is_opaque(argb):
    return alpha_from_argb(argb) >= 255


# /**
#  * Converts a color from ARGB to XYZ.
#  */
def argb_from_xyz(x, y, z):
    matrix = XYZ_TO_SRGB
    linear_r = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z
    linear_g = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z
    linear_b = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z
    r = delinearized(linear_r)
    g = delinearized(linear_g)
    b = delinearized(linear_b)
    return argb_from_rgb(r, g, b)


# /**
#  * Converts a color from XYZ to ARGB.
#  */
def xyz_from_argb(argb):
    r = linearized(red_from_argb(argb))
    g = linearized(green_from_argb(argb))
    b = linearized(blue_from_argb(argb))
    return matrix_multiply([r, g, b], SRGB_TO_XYZ)


# /**
#  * Converts a color represented in Lab color space into an ARGB
#  * integer.
#  */
def lab_inv_f(ft):
    e = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    ft3 = ft * ft * ft
    if ft3 > e:
        return ft3
    else:
        return (116 * ft - 16) / kappa


def argb_from_lab(lightness, a, b):
    white_point = WHITE_POINT_D65
    fy = (lightness + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0
    x_normalized = lab_inv_f(fx)
    y_normalized = lab_inv_f(fy)
    z_normalized = lab_inv_f(fz)
    x = x_normalized * white_point[0]
    y = y_normalized * white_point[1]
    z = z_normalized * white_point[2]
    return argb_from_xyz(x, y, z)


# /**
#  * Converts a color from ARGB representation to L*a*b*
#  * representation.
#  *
#  * @param argb the ARGB representation of a color
#  * @return a Lab object representing the color
#  */
def lab_f(t):
    e = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    if t > e:
        return math.pow(t, 1.0 / 3.0)
    else:
        return (kappa * t + 16) / 116


def lab_from_argb(argb):
    linear_r = linearized(red_from_argb(argb))
    linear_g = linearized(green_from_argb(argb))
    linear_b = linearized(blue_from_argb(argb))
    matrix = SRGB_TO_XYZ
    x = matrix[0][0] * linear_r + matrix[0][1] * linear_g + matrix[0][2] * linear_b
    y = matrix[1][0] * linear_r + matrix[1][1] * linear_g + matrix[1][2] * linear_b
    z = matrix[2][0] * linear_r + matrix[2][1] * linear_g + matrix[2][2] * linear_b
    white_point = WHITE_POINT_D65
    x_normalized = x / white_point[0]
    y_normalized = y / white_point[1]
    z_normalized = z / white_point[2]
    fx = lab_f(x_normalized)
    fy = lab_f(y_normalized)
    fz = lab_f(z_normalized)
    lightness = 116.0 * fy - 16
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return [lightness, a, b]


# /**
#  * Converts an L* value to an ARGB representation.
#  *
#  * @param lstar L* in L*a*b*
#  * @return ARGB representation of grayscale color with lightness
#  * matching L*
#  */
def argb_from_lstar(lstar):
    fy = (lstar + 16.0) / 116.0
    fz = fy
    fx = fy
    kappa = 24389.0 / 27.0
    epsilon = 216.0 / 24389.0
    l_exceeds_epsilon_kappa = lstar > 8.0
    y = fy * fy * fy if l_exceeds_epsilon_kappa else lstar / kappa
    cube_exceed_epsilon = fy * fy * fy > epsilon
    x = fx * fx * fx if cube_exceed_epsilon else lstar / kappa
    z = fz * fz * fz if cube_exceed_epsilon else lstar / kappa
    white_point = WHITE_POINT_D65
    return argb_from_xyz(x * white_point[0], y * white_point[1], z * white_point[2])


# /**
#  * Computes the L* value of a color in ARGB representation.
#  *
#  * @param argb ARGB representation of a color
#  * @return L*, from L*a*b*, coordinate of the color
#  */
def lstar_from_argb(argb):
    y = xyz_from_argb(argb)[1] / 100.0
    e = 216.0 / 24389.0
    if y <= e:
        return 24389.0 / 27.0 * y
    else:
        y_intermediate = math.pow(y, 1.0 / 3.0)
        return 116.0 * y_intermediate - 16.0


# /**
#  * Converts an L* value to a Y value.
#  *
#  * L* in L*a*b* and Y in XYZ measure the same quantity, luminance.
#  *
#  * L* measures perceptual luminance, a linear scale. Y in XYZ
#  * measures relative luminance, a logarithmic scale.
#  *
#  * @param lstar L* in L*a*b*
#  * @return Y in XYZ
#  */
def y_from_lstar(lstar):
    ke = 8.0
    if lstar > ke:
        return math.pow((lstar + 16.0) / 116.0, 3.0) * 100.0
    else:
        return lstar / (24389.0 / 27.0) * 100.0


# /**
#  * Linearizes an RGB component.
#  *
#  * @param rgbComponent 0 <= rgb_component <= 255, represents R/G/B
#  * channel
#  * @return 0.0 <= output <= 100.0, color channel converted to
#  * linear RGB space
#  */
def linearized(rgb_component):
    normalized = rgb_component / 255.0
    if normalized <= 0.040449936:
        return normalized / 12.92 * 100.0
    else:
        return math.pow((normalized + 0.055) / 1.055, 2.4) * 100.0


# /**
#  * Delinearizes an RGB component.
#  *
#  * @param rgbComponent 0.0 <= rgb_component <= 100.0, represents
#  * linear R/G/B channel
#  * @return 0 <= output <= 255, color channel converted to regular
#  * RGB space
#  */
def delinearized(rgb_component):
    normalized = rgb_component / 100.0
    if normalized <= 0.0031308:
        delinearized_value = normalized * 12.92
    else:
        delinearized_value = 1.055 * math.pow(normalized, 1.0 / 2.4) - 0.055
    return clamp_int(0, 255, round(delinearized_value * 255.0))


# /**
#  * Returns the standard white point white on a sunny day.
#  *
#  * @return The white point
#  */
def white_point_d65():
    return WHITE_POINT_D65
