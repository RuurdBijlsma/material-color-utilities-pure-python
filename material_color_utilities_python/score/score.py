from collections import OrderedDict

from material_color_utilities_python.hct.cam16 import Cam16
from material_color_utilities_python.utils.color_utils import lstar_from_argb
from material_color_utilities_python.utils.math_utils import (
    difference_degrees,
    sanitize_degrees_int,
)


# /**
#  *  Given a large set of colors, remove colors that are unsuitable for a UI
#  *  theme, and rank the rest based on suitability.
#  *
#  *  Enables use of a high cluster count for image quantization, thus ensuring
#  *  colors aren't muddied, while curating the high cluster count to a much
#  *  smaller number of appropriate choices.
#  */
class Score:
    def __init__(self):
        pass

    # /**
    #  * Given a map with keys of colors and values of how often the color appears,
    #  * rank the colors based on suitability for being used for a UI theme.
    #  *
    #  * @param colorsToPopulation map with keys of colors and values of how often
    #  *     the color appears, usually from a source image.
    #  * @return Colors sorted by suitability for a UI theme. The most suitable
    #  *     color is the first item, the least suitable is the last. There will
    #  *     always be at least one color returned. If all the input colors
    #  *     were not suitable for a theme, a default fallback color will be
    #  *     provided, Google Blue.
    #  */
    # Using OrderedDict for JavaScript Map
    @staticmethod
    def score(colors_to_population):
        # // Determine the total count of all colors.
        population_sum = 0
        for population in colors_to_population.values():
            population_sum += population
        # // Turn the count of each color into a proportion by dividing by the total
        # // count. Also, fill a cache with CAM16 colors representing each color, and
        # // record the proportion of colors for each CAM16 hue.
        colors_to_proportion = OrderedDict()
        colors_to_cam = OrderedDict()
        hue_proportions = [0] * 361
        for color, population in colors_to_population.items():
            proportion = population / population_sum
            colors_to_proportion[color] = proportion
            cam = Cam16.from_int(color)
            colors_to_cam[color] = cam
            hue = round(cam.hue)
            hue_proportions[hue] += proportion
        # // Determine the proportion of the colors around each color, by summing the
        # // proportions around each color's hue.
        colors_to_excited_proportion = OrderedDict()
        for color, cam in colors_to_cam.items():
            hue = round(cam.hue)
            excited_proportion = 0
            for i in range((hue - 15), (hue + 15)):
                neighbor_hue = sanitize_degrees_int(i)
                excited_proportion += hue_proportions[neighbor_hue]
            colors_to_excited_proportion[color] = excited_proportion
        # // Score the colors by their proportion, as well as how chromatic they are.
        colors_to_score = OrderedDict()
        for color, cam in colors_to_cam.items():
            proportion = colors_to_excited_proportion[color]
            proportion_score = proportion * 100.0 * Score.WEIGHT_PROPORTION
            chroma_weight = (
                Score.WEIGHT_CHROMA_BELOW
                if cam.chroma < Score.TARGET_CHROMA
                else Score.WEIGHT_CHROMA_ABOVE
            )
            chroma_score = (cam.chroma - Score.TARGET_CHROMA) * chroma_weight
            score = proportion_score + chroma_score
            colors_to_score[color] = score
        # // Remove colors that are unsuitable, ex. very dark or unchromatic colors.
        # // Also, remove colors that are very similar in hue.
        filtered_colors = Score.filter(colors_to_excited_proportion, colors_to_cam)
        deduplicated_colors_to_score = OrderedDict()
        for color in filtered_colors:
            duplicate_hue = False
            hue = colors_to_cam[color].hue
            for alreadyChosenColor in deduplicated_colors_to_score:
                already_chosen_hue = colors_to_cam[alreadyChosenColor].hue
                if difference_degrees(hue, already_chosen_hue) < 15:
                    duplicate_hue = True
                    break
            if duplicate_hue:
                continue
            deduplicated_colors_to_score[color] = colors_to_score[color]
        # // Ensure the list of colors returned is sorted such that the first in the
        # // list is the most suitable, and the last is the least suitable.
        colors_by_score_descending = list(deduplicated_colors_to_score.items())
        colors_by_score_descending.sort(reverse=True, key=lambda x: x[1])
        answer = list(map(lambda x: x[0], colors_by_score_descending))
        # // Ensure that at least one color is returned.
        if len(answer) == 0:
            answer.append(0xFF4285F4)  # // Google Blue
        return answer

    @staticmethod
    def filter(colors_to_excited_proportion, colors_to_cam):
        filtered = []
        for color, cam in colors_to_cam.items():
            proportion = colors_to_excited_proportion[color]
            if (
                cam.chroma >= Score.CUTOFF_CHROMA
                and lstar_from_argb(color) >= Score.CUTOFF_TONE
                and proportion >= Score.CUTOFF_EXCITED_PROPORTION
            ):
                filtered.append(color)
        return filtered


Score.TARGET_CHROMA = 48.0
Score.WEIGHT_PROPORTION = 0.7
Score.WEIGHT_CHROMA_ABOVE = 0.3
Score.WEIGHT_CHROMA_BELOW = 0.1
Score.CUTOFF_CHROMA = 15.0
Score.CUTOFF_TONE = 10.0
Score.CUTOFF_EXCITED_PROPORTION = 0.01
