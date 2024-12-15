# /**
#  * Provides conversions needed for K-Means quantization. Converting input to
#  * points, and converting the final state of the K-Means algorithm to colors.
#  */
from material_color_utilities_python.utils.color_utils import argb_from_lab

# /**
#  * Convert a 3-element array to a color represented in ARGB.
#  */
def lab_to_int(point):
    return argb_from_lab(point[0], point[1], point[2])

# /**
#  * Standard CIE 1976 delta E formula also takes the square root, unneeded
#  * here. This method is used by quantization algorithms to compare distance,
#  * and the relative ordering is the same, with or without a square root.
#  *
#  * This relatively minor optimization is helpful because this method is
#  * called at least once for each pixel in an image.
#  */
# Renamed "from" to "from_v", from is reserved in Python
def lab_distance(from_v, to):
    dist_lightness = from_v[0] - to[0]
    dist_a = from_v[1] - to[1]
    dist_b = from_v[2] - to[2]
    return dist_lightness * dist_lightness + dist_a * dist_a + dist_b * dist_b
