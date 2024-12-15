# // libmonet is designed to have a consistent API across platforms
# // and modular components that can be moved around easily. Using a class as a
# // namespace facilitates this.
# //
# // tslint:disable:class-as-namespace
# /**
#  * Functions for blending in HCT and CAM16.
#  */
from material_color_utilities_python.hct.cam16 import Cam16
from material_color_utilities_python.hct.hct import Hct
from material_color_utilities_python.utils.color_utils import lstar_from_argb
from material_color_utilities_python.utils.math_utils import (
    difference_degrees,
    sanitize_degrees_double,
)


class Blend:
    # /**
    #  * Blend the design color's HCT hue towards the key color's HCT
    #  * hue, in a way that leaves the original color recognizable and
    #  * recognizably shifted towards the key color.
    #  *
    #  * @param designColor ARGB representation of an arbitrary color.
    #  * @param sourceColor ARGB representation of the main theme color.
    #  * @return The design color with a hue shifted towards the
    #  * system's color, a slightly warmer/cooler variant of the design
    #  * color's hue.
    #  */
    # Changed var differenceDegrees to differenceDegrees_v to avoid overwrite
    @staticmethod
    def harmonize(design_color, source_color):
        from_hct = Hct.from_int(design_color)
        to_hct = Hct.from_int(source_color)
        difference_degrees_v = difference_degrees(from_hct.hue, to_hct.hue)
        rotation_degrees = min(difference_degrees_v * 0.5, 15.0)
        output_hue = sanitize_degrees_double(
            from_hct.hue
            + rotation_degrees * Blend.rotation_direction(from_hct.hue, to_hct.hue)
        )
        return Hct.from_hct(output_hue, from_hct.chroma, from_hct.tone).to_int()

    # /**
    #  * Blends hue from one color into another. The chroma and tone of
    #  * the original color are maintained.
    #  *
    #  * @param from ARGB representation of color
    #  * @param to ARGB representation of color
    #  * @param amount how much blending to perform; 0.0 >= and <= 1.0
    #  * @return from, with a hue blended towards to. Chroma and tone
    #  * are constant.
    #  */
    # Changed "from" arg to "from_v", from is reserved in Python
    @staticmethod
    def hctHue(from_v, to, amount):
        ucs = Blend.cam16_ucs(from_v, to, amount)
        ucs_cam = Cam16.from_int(ucs)
        from_cam = Cam16.from_int(from_v)
        blended = Hct.from_hct(ucs_cam.hue, from_cam.chroma, lstar_from_argb(from_v))
        return blended.to_int()

    # /**
    #  * Blend in CAM16-UCS space.
    #  *
    #  * @param from ARGB representation of color
    #  * @param to ARGB representation of color
    #  * @param amount how much blending to perform; 0.0 >= and <= 1.0
    #  * @return from, blended towards to. Hue, chroma, and tone will
    #  * change.
    #  */
    # Changed "from" arg to "from_v", from is reserved in Python
    @staticmethod
    def cam16_ucs(from_v, to, amount):
        from_cam = Cam16.from_int(from_v)
        to_cam = Cam16.from_int(to)
        from_j = from_cam.j_star
        from_a = from_cam.a_star
        from_b = from_cam.b_star
        to_j = to_cam.j_star
        to_a = to_cam.a_star
        to_b = to_cam.b_star
        j_star = from_j + (to_j - from_j) * amount
        a_star = from_a + (to_a - from_a) * amount
        b_star = from_b + (to_b - from_b) * amount
        return Cam16.from_ucs(j_star, a_star, b_star).to_int()

    # /**
    #  * Sign of direction change needed to travel from one angle to
    #  * another.
    #  *
    #  * @param from The angle travel starts from, in degrees.
    #  * @param to The angle travel ends at, in degrees.
    #  * @return -1 if decreasing from leads to the shortest travel
    #  * distance, 1 if increasing from leads to the shortest travel
    #  * distance.
    #  */
    # Changed "from" arg to "from_v", from is reserved in Python
    @staticmethod
    def rotation_direction(from_v, to):
        a = to - from_v
        b = to - from_v + 360.0
        c = to - from_v - 360.0
        a_abs = abs(a)
        b_abs = abs(b)
        c_abs = abs(c)
        if a_abs <= b_abs and a_abs <= c_abs:
            return 1.0 if a >= 0.0 else -1.0
        elif b_abs <= a_abs and b_abs <= c_abs:
            return 1.0 if b >= 0.0 else -1.0
        else:
            return 1.0 if c >= 0.0 else -1.0
