# /**
#  * A color system built using CAM16 hue and chroma, and L* from
#  * L*a*b*.
#  *
#  * Using L* creates a link between the color system, contrast, and thus
#  * accessibility. Contrast ratio depends on relative luminance, or Y in the XYZ
#  * color space. L*, or perceptual luminance can be calculated from Y.
#  *
#  * Unlike Y, L* is linear to human perception, allowing trivial creation of
#  * accurate color tones.
#  *
#  * Unlike contrast ratio, measuring contrast in L* is linear, and simple to
#  * calculate. A difference of 40 in HCT tone guarantees a contrast ratio >= 3.0,
#  * and a difference of 50 guarantees a contrast ratio >= 4.5.
#  */
from material_color_utilities_python.hct.cam16 import Cam16
from material_color_utilities_python.hct.viewing_conditions import (
    default_viewing_conditions,
)
from material_color_utilities_python.utils.color_utils import (
    argb_from_lstar,
    lstar_from_argb,
)
from material_color_utilities_python.utils.math_utils import (
    clamp_double,
    sanitize_degrees_double,
)

# /**
#  * When the delta between the floor & ceiling of a binary search for maximum
#  * chroma at a hue and tone is less than this, the binary search terminates.
#  */
CHROMA_SEARCH_ENDPOINT = 0.4

# /**
#  * The maximum color distance, in CAM16-UCS, between a requested color and the
#  * color returned.
#  */
DE_MAX = 1.0

# /** The maximum difference between the requested L* and the L* returned. */
DL_MAX = 0.2

# /**
#  * When the delta between the floor & ceiling of a binary search for J,
#  * lightness in CAM16, is less than this, the binary search terminates.
#  */
LIGHTNESS_SEARCH_ENDPOINT = 0.01


# /**
#  * @param hue CAM16 hue
#  * @param chroma CAM16 chroma
#  * @param tone L*a*b* lightness
#  * @return CAM16 instance within error tolerance of the provided dimensions,
#  *     or null.
#  */
def find_cam_by_j(hue, chroma, tone):
    low = 0.0
    high = 100.0
    best_dist_l = 1000.0
    best_dist_e = 1000.0
    best_cam = None
    while abs(low - high) > LIGHTNESS_SEARCH_ENDPOINT:
        mid = low + (high - low) / 2
        cam_before_clip = Cam16.from_jch(mid, chroma, hue)
        clipped = cam_before_clip.to_int()  # noqa: F821
        clipped_lstar = lstar_from_argb(clipped)
        dist_l = abs(tone - clipped_lstar)
        if dist_l < DL_MAX:
            cam_clipped = Cam16.from_int(clipped)
            d_e = cam_clipped.distance(
                Cam16.from_jch(cam_clipped.j, cam_clipped.chroma, hue)
            )
            if d_e <= DE_MAX and d_e <= best_dist_e:
                best_dist_l = dist_l
                best_dist_e = d_e
                best_cam = cam_clipped
        if best_dist_l == 0 and best_dist_e == 0:
            break
        if clipped_lstar < tone:
            low = mid
        else:
            high = mid
    return best_cam


# /**
#  * @param hue CAM16 hue.
#  * @param chroma CAM16 chroma.
#  * @param tone L*a*b* lightness.
#  * @param viewing_conditions Information about the environment where the color
#  *     was observed.
#  */
def get_int_in_viewing_conditions(hue, chroma, tone, viewing_conditions):
    if chroma < 1.0 or round(tone) <= 0.0 or round(tone) >= 100.0:
        return argb_from_lstar(tone)

    hue = sanitize_degrees_double(hue)
    high = chroma
    mid = chroma
    low = 0.0
    is_first_loop = True
    answer = None
    while abs(low - high) >= CHROMA_SEARCH_ENDPOINT:
        possible_answer = find_cam_by_j(hue, mid, tone)
        if is_first_loop:
            if possible_answer is not None:
                return possible_answer.viewed(viewing_conditions)
            else:
                is_first_loop = False
                mid = low + (high - low) / 2.0
                continue
        if possible_answer is None:
            high = mid
        else:
            answer = possible_answer
            low = mid
        mid = low + (high - low) / 2.0
    if answer is None:
        return argb_from_lstar(tone)
    return answer.viewed(viewing_conditions)


# /**
#  * @param hue a number, in degrees, representing ex. red, orange, yellow, etc.
#  *     Ranges from 0 <= hue < 360.
#  * @param chroma Informally, colorfulness. Ranges from 0 to roughly 150.
#  *    Like all perceptually accurate color systems, chroma has a different
#  *    maximum for any given hue and tone, so the color returned may be lower
#  *    than the requested chroma.
#  * @param tone Lightness. Ranges from 0 to 100.
#  * @return ARGB representation of a color in default viewing conditions
#  */
def get_int(hue, chroma, tone):
    return get_int_in_viewing_conditions(
        sanitize_degrees_double(hue),
        chroma,
        clamp_double(0.0, 100.0, tone),
        default_viewing_conditions,
    )


# /**
#  * HCT, hue, chroma, and tone. A color system that provides a perceptually
#  * accurate color measurement system that can also accurately render what colors
#  * will appear as in different lighting environments.
#  */
class Hct:
    def __init__(self, internal_hue, internal_chroma, internal_tone):
        self.internal_hue = internal_hue
        self.internal_chroma = internal_chroma
        self.internal_tone = internal_tone
        self.set_internal_state(self.to_int())

    # /**
    #  * @param hue 0 <= hue < 360; invalid values are corrected.
    #  * @param chroma 0 <= chroma < ?; Informally, colorfulness. The color
    #  *     returned may be lower than the requested chroma. Chroma has a different
    #  *     maximum for any given hue and tone.
    #  * @param tone 0 <= tone <= 100; invalid values are corrected.
    #  * @return HCT representation of a color in default viewing conditions.
    #  */
    # Function renamed from "from" to "fromHct", from is reserved in Python
    @staticmethod
    def from_hct(hue, chroma, tone):
        return Hct(hue, chroma, tone)

    # /**
    #  * @param argb ARGB representation of a color.
    #  * @return HCT representation of a color in default viewing conditions
    #  */
    @staticmethod
    def from_int(argb):
        cam = Cam16.from_int(argb)
        tone = lstar_from_argb(argb)
        return Hct(cam.hue, cam.chroma, tone)

    def to_int(self):
        return get_int(self.internal_hue, self.internal_chroma, self.internal_tone)

    # /**
    #  * A number, in degrees, representing ex. red, orange, yellow, etc.
    #  * Ranges from 0 <= hue < 360.
    #  */
    def get_hue(self):
        return self.internal_hue

    # /**
    #  * @param newHue 0 <= newHue < 360; invalid values are corrected.
    #  * Chroma may decrease because chroma has a different maximum for any given
    #  * hue and tone.
    #  */
    def set_hue(self, new_hue):
        self.set_internal_state(
            get_int(
                sanitize_degrees_double(new_hue),
                self.internal_chroma,
                self.internal_tone,
            )
        )

    def get_chroma(self):
        return self.internal_chroma

    # /**
    #  * @param newChroma 0 <= newChroma < ?
    #  * Chroma may decrease because chroma has a different maximum for any given
    #  * hue and tone.
    #  */
    def set_chroma(self, new_chroma):
        self.set_internal_state(
            get_int(self.internal_hue, new_chroma, self.internal_tone)
        )

    # /** Lightness. Ranges from 0 to 100. */
    def get_tone(self):
        return self.internal_tone

    # /**
    #  * @param newTone 0 <= newTone <= 100; invalid valids are corrected.
    #  * Chroma may decrease because chroma has a different maximum for any given
    #  * hue and tone.
    #  */
    def set_tone(self, new_tone):
        self.set_internal_state(
            get_int(self.internal_hue, self.internal_chroma, new_tone)
        )

    def set_internal_state(self, argb):
        cam = Cam16.from_int(argb)
        tone = lstar_from_argb(argb)
        self.internal_hue = cam.hue
        self.internal_chroma = cam.chroma
        self.internal_tone = tone

    # Adding properties for getters and setters
    hue = property(get_hue, set_hue)
    chroma = property(get_chroma, set_chroma)
    tone = property(get_tone, set_tone)
