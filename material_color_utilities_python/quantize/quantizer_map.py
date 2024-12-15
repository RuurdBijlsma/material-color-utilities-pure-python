from collections import OrderedDict

from material_color_utilities_python.utils.color_utils import alpha_from_argb


# /**
#  * Quantizes an image into a map, with keys of ARGB colors, and values of the
#  * number of times that color appears in the image.
#  */
# // libmonet is designed to have a consistent API across platforms
# // and modular components that can be moved around easily. Using a class as a
# // namespace facilitates this.
# //
# // tslint:disable-next-line:class-as-namespace
class QuantizerMap:
    # /**
    #  * @param pixels Colors in ARGB format.
    #  * @return A Map with keys of ARGB colors, and values of the number of times
    #  *     the color appears in the image.
    #  */
    @staticmethod
    def quantize(pixels):
        count_by_color = OrderedDict()
        for i in range(len(pixels)):
            pixel = pixels[i]
            alpha = alpha_from_argb(pixel)
            if alpha < 255:
                continue
            count_by_color[pixel] = (count_by_color[pixel] if pixel in count_by_color.keys() else 0) + 1
        return count_by_color
