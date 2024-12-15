import math

from material_color_utilities_python.hct.viewing_conditions import (
    ViewingConditions,
    default_viewing_conditions,
)
from material_color_utilities_python.utils.color_utils import argb_from_xyz, linearized
from material_color_utilities_python.utils.math_utils import signum


# /**
#  * CAM16, a color appearance model. Colors are not just defined by their hex
#  * code, but rather, a hex code and viewing conditions.
#  *
#  * CAM16 instances also have coordinates in the CAM16-UCS space, called J*, a*,
#  * b*, or j_star, a_star, b_star in code. CAM16-UCS is included in the CAM16
#  * specification, and should be used when measuring distances between colors.
#  *
#  * In traditional color spaces, a color can be identified solely by the
#  * observer's measurement of the color. Color appearance models such as CAM16
#  * also use information about the environment where the color was
#  * observed, known as the viewing conditions.
#  *
#  * For example, white under the traditional assumption of a midday sun white
#  * point is accurately measured as a slightly chromatic blue by CAM16. (roughly,
#  * hue 203, chroma 3, lightness 100)
#  */
class Cam16:
    # /**
    #  * All the CAM16 dimensions can be calculated from 3 of the dimensions, in
    #  * the following combinations:
    #  *      -  {j or q} and {c, m, or s} and hue
    #  *      - j_star, a_star, b_star
    #  * Prefer using a static method that constructs from 3 of those dimensions.
    #  * This constructor is intended for those methods to use to return all
    #  * possible dimensions.
    #  *
    #  * @param hue
    #  * @param chroma informally, colorfulness / color intensity. like saturation
    #  *     in HSL, except perceptually accurate.
    #  * @param j lightness
    #  * @param q brightness ratio of lightness to white point's lightness
    #  * @param m colorfulness
    #  * @param s saturation ratio of chroma to white point's chroma
    #  * @param j_star CAM16-UCS J coordinate
    #  * @param a_star CAM16-UCS a coordinate
    #  * @param b_star CAM16-UCS b coordinate
    #  */
    def __init__(self, hue, chroma, j, q, m, s, j_star, a_star, b_star):
        self.hue = hue
        self.chroma = chroma
        self.j = j
        self.q = q
        self.m = m
        self.s = s
        self.j_star = j_star
        self.a_star = a_star
        self.b_star = b_star

    # /**
    #  * CAM16 instances also have coordinates in the CAM16-UCS space, called J*,
    #  * a*, b*, or j_star, a_star, b_star in code. CAM16-UCS is included in the CAM16
    #  * specification, and is used to measure distances between colors.
    #  */
    def distance(self, other):
        dist_j = self.j_star - other.j_star
        dist_a = self.a_star - other.a_star
        dist_b = self.b_star - other.b_star
        dist_e_prime = math.sqrt(dist_j * dist_j + dist_a * dist_a + dist_b * dist_b)
        dist_e = 1.41 * pow(dist_e_prime, 0.63)
        return dist_e

    # /**
    #  * @param argb ARGB representation of a color.
    #  * @return CAM16 color, assuming the color was viewed in default viewing
    #  *     conditions.
    #  */
    @staticmethod
    def from_int(argb):
        return Cam16.from_int_in_viewing_conditions(argb, default_viewing_conditions)

    # /**
    #  * @param argb ARGB representation of a color.
    #  * @param viewing_conditions Information about the environment where the color
    #  *     was observed.
    #  * @return CAM16 color.
    #  */
    @staticmethod
    def from_int_in_viewing_conditions(argb, viewing_conditions):
        red = (argb & 0x00FF0000) >> 16
        green = (argb & 0x0000FF00) >> 8
        blue = argb & 0x000000FF
        red_l = linearized(red)
        green_l = linearized(green)
        blue_l = linearized(blue)
        x = 0.41233895 * red_l + 0.35762064 * green_l + 0.18051042 * blue_l
        y = 0.2126 * red_l + 0.7152 * green_l + 0.0722 * blue_l
        z = 0.01932141 * red_l + 0.11916382 * green_l + 0.95034478 * blue_l
        r_c = 0.401288 * x + 0.650173 * y - 0.051461 * z
        g_c = -0.250268 * x + 1.204414 * y + 0.045854 * z
        b_c = -0.002079 * x + 0.048952 * y + 0.953127 * z
        r_d = viewing_conditions.rgbD[0] * r_c
        g_d = viewing_conditions.rgbD[1] * g_c
        b_d = viewing_conditions.rgbD[2] * b_c
        r_af = pow((viewing_conditions.fl * abs(r_d)) / 100.0, 0.42)
        g_af = pow((viewing_conditions.fl * abs(g_d)) / 100.0, 0.42)
        b_af = pow((viewing_conditions.fl * abs(b_d)) / 100.0, 0.42)
        r_a = (signum(r_d) * 400.0 * r_af) / (r_af + 27.13)
        g_a = (signum(g_d) * 400.0 * g_af) / (g_af + 27.13)
        b_a = (signum(b_d) * 400.0 * b_af) / (b_af + 27.13)
        a = (11.0 * r_a + -12.0 * g_a + b_a) / 11.0
        b = (r_a + g_a - 2.0 * b_a) / 9.0
        u = (20.0 * r_a + 20.0 * g_a + 21.0 * b_a) / 20.0
        p2 = (40.0 * r_a + 20.0 * g_a + b_a) / 20.0
        atan2 = math.atan2(b, a)
        atan_degrees = (atan2 * 180.0) / math.pi
        hue = (
            atan_degrees + 360.0
            if atan_degrees < 0
            else atan_degrees - 360.0
            if atan_degrees >= 360
            else atan_degrees
        )
        hue_radians = (hue * math.pi) / 180.0
        ac = p2 * viewing_conditions.nbb
        j = 100.0 * pow(
            ac / viewing_conditions.aw, viewing_conditions.c * viewing_conditions.z
        )
        q = (
            (4.0 / viewing_conditions.c)
            * math.sqrt(j / 100.0)
            * (viewing_conditions.aw + 4.0)
            * viewing_conditions.fLRoot
        )
        hue_prime = hue + 360 if hue < 20.14 else hue
        e_hue = 0.25 * (math.cos((hue_prime * math.pi) / 180.0 + 2.0) + 3.8)
        p1 = (50000.0 / 13.0) * e_hue * viewing_conditions.nc * viewing_conditions.ncb
        t = (p1 * math.sqrt(a * a + b * b)) / (u + 0.305)
        alpha = pow(t, 0.9) * pow(1.64 - pow(0.29, viewing_conditions.n), 0.73)
        c = alpha * math.sqrt(j / 100.0)
        m = c * viewing_conditions.fLRoot
        s = 50.0 * math.sqrt(
            (alpha * viewing_conditions.c) / (viewing_conditions.aw + 4.0)
        )
        j_star = ((1.0 + 100.0 * 0.007) * j) / (1.0 + 0.007 * j)
        mstar = (1.0 / 0.0228) * math.log(1.0 + 0.0228 * m)
        a_star = mstar * math.cos(hue_radians)
        b_star = mstar * math.sin(hue_radians)
        return Cam16(hue, c, j, q, m, s, j_star, a_star, b_star)

    # /**
    #  * @param j CAM16 lightness
    #  * @param c CAM16 chroma
    #  * @param h CAM16 hue
    #  */
    @staticmethod
    def from_jch(j, c, h):
        return Cam16.from_jch_in_viewing_conditions(j, c, h, default_viewing_conditions)

    # /**
    #  * @param j CAM16 lightness
    #  * @param c CAM16 chroma
    #  * @param h CAM16 hue
    #  * @param viewing_conditions Information about the environment where the color
    #  *     was observed.
    #  */
    @staticmethod
    def from_jch_in_viewing_conditions(j, c, h, viewing_conditions):
        q = (
            (4.0 / viewing_conditions.c)
            * math.sqrt(j / 100.0)
            * (viewing_conditions.aw + 4.0)
            * viewing_conditions.fLRoot
        )
        m = c * viewing_conditions.fLRoot
        alpha = c / math.sqrt(j / 100.0)
        s = 50.0 * math.sqrt(
            (alpha * viewing_conditions.c) / (viewing_conditions.aw + 4.0)
        )
        hue_radians = (h * math.pi) / 180.0
        j_star = ((1.0 + 100.0 * 0.007) * j) / (1.0 + 0.007 * j)
        mstar = (1.0 / 0.0228) * math.log(1.0 + 0.0228 * m)
        a_star = mstar * math.cos(hue_radians)
        b_star = mstar * math.sin(hue_radians)
        return Cam16(h, c, j, q, m, s, j_star, a_star, b_star)

    # /**
    #  * @param j_star CAM16-UCS lightness.
    #  * @param a_star CAM16-UCS a dimension. Like a* in L*a*b*, it is a Cartesian
    #  *     coordinate on the Y axis.
    #  * @param b_star CAM16-UCS b dimension. Like a* in L*a*b*, it is a Cartesian
    #  *     coordinate on the X axis.
    #  */
    @staticmethod
    def from_ucs(j_star, a_star, b_star):
        return Cam16.from_ucs_in_viewing_conditions(
            j_star, a_star, b_star, default_viewing_conditions
        )

    # /**
    #  * @param j_star CAM16-UCS lightness.
    #  * @param a_star CAM16-UCS a dimension. Like a* in L*a*b*, it is a Cartesian
    #  *     coordinate on the Y axis.
    #  * @param b_star CAM16-UCS b dimension. Like a* in L*a*b*, it is a Cartesian
    #  *     coordinate on the X axis.
    #  * @param viewing_conditions Information about the environment where the color
    #  *     was observed.
    #  */
    @staticmethod
    def from_ucs_in_viewing_conditions(j_star, a_star, b_star, viewing_conditions):
        a = a_star
        b = b_star
        m = math.sqrt(a * a + b * b)
        m = (math.exp(m * 0.0228) - 1.0) / 0.0228
        c = m / viewing_conditions.fLRoot
        h = math.atan2(b, a) * (180.0 / math.pi)
        if h < 0.0:
            h += 360.0
        j = j_star / (1 - (j_star - 100) * 0.007)
        return Cam16.from_jch_in_viewing_conditions(j, c, h, viewing_conditions)

    # /**
    #  *  @return ARGB representation of color, assuming the color was viewed in
    #  *     default viewing conditions, which are near-identical to the default
    #  *     viewing conditions for sRGB.
    #  */
    def to_int(self):
        return self.viewed(default_viewing_conditions)

    # /**
    #  * @param viewing_conditions Information about the environment where the color
    #  *     will be viewed.
    #  * @return ARGB representation of color
    #  */
    def viewed(self, viewing_conditions):
        alpha = (
            0.0
            if self.chroma == 0.0 or self.j == 0.0
            else self.chroma / math.sqrt(self.j / 100.0)
        )
        t = pow(alpha / pow(1.64 - pow(0.29, viewing_conditions.n), 0.73), 1.0 / 0.9)
        h_rad = (self.hue * math.pi) / 180.0
        e_hue = 0.25 * (math.cos(h_rad + 2.0) + 3.8)
        ac = viewing_conditions.aw * pow(
            self.j / 100.0, 1.0 / viewing_conditions.c / viewing_conditions.z
        )
        p1 = e_hue * (50000.0 / 13.0) * viewing_conditions.nc * viewing_conditions.ncb
        p2 = ac / viewing_conditions.nbb
        h_sin = math.sin(h_rad)
        h_cos = math.cos(h_rad)
        gamma = (23.0 * (p2 + 0.305) * t) / (
            23.0 * p1 + 11.0 * t * h_cos + 108.0 * t * h_sin
        )
        a = gamma * h_cos
        b = gamma * h_sin
        r_a = (460.0 * p2 + 451.0 * a + 288.0 * b) / 1403.0
        g_a = (460.0 * p2 - 891.0 * a - 261.0 * b) / 1403.0
        b_a = (460.0 * p2 - 220.0 * a - 6300.0 * b) / 1403.0
        r_c_base = max(0, (27.13 * abs(r_a)) / (400.0 - abs(r_a)))
        r_c = signum(r_a) * (100.0 / viewing_conditions.fl) * pow(r_c_base, 1.0 / 0.42)
        g_c_base = max(0, (27.13 * abs(g_a)) / (400.0 - abs(g_a)))
        g_c = signum(g_a) * (100.0 / viewing_conditions.fl) * pow(g_c_base, 1.0 / 0.42)
        b_c_base = max(0, (27.13 * abs(b_a)) / (400.0 - abs(b_a)))
        b_c = signum(b_a) * (100.0 / viewing_conditions.fl) * pow(b_c_base, 1.0 / 0.42)
        r_f = r_c / viewing_conditions.rgbD[0]
        g_f = g_c / viewing_conditions.rgbD[1]
        b_f = b_c / viewing_conditions.rgbD[2]
        x = 1.86206786 * r_f - 1.01125463 * g_f + 0.14918677 * b_f
        y = 0.38752654 * r_f + 0.62144744 * g_f - 0.00897398 * b_f
        z = -0.01584150 * r_f - 0.03412294 * g_f + 1.04996444 * b_f
        argb = argb_from_xyz(x, y, z)
        return argb
