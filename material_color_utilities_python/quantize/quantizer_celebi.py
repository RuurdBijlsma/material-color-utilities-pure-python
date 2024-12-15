from material_color_utilities_python.quantize.quantizer_wsmeans import QuantizerWsMeans
from material_color_utilities_python.quantize.quantizer_wu import QuantizerWu


# /**
#  * An image quantizer that improves on the quality of a standard K-Means
#  * algorithm by setting the K-Means initial state to the output of a Wu
#  * quantizer, instead of random centroids. Improves on speed by several
#  * optimizations, as implemented in Wsmeans, or Weighted Square Means, K-Means
#  * with those optimizations.
#  *
#  * This algorithm was designed by M. Emre Celebi, and was found in their 2011
#  * paper, Improving the Performance of K-Means for Color Quantization.
#  * https://arxiv.org/abs/1101.0395
#  */
# // libmonet is designed to have a consistent API across platforms
# // and modular components that can be moved around easily. Using a class as a
# // namespace facilitates this.
# //
# // tslint:disable-next-line:class-as-namespace
class QuantizerCelebi:
    # /**
    #  * @param pixels Colors in ARGB format.
    #  * @param maxColors The number of colors to divide the image into. A lower
    #  *     number of colors may be returned.
    #  * @return Map with keys of colors in ARGB format, and values of number of
    #  *     pixels in the original image that correspond to the color in the
    #  *     quantized image.
    #  */
    @staticmethod
    def quantize(pixels, max_colors):
        wu = QuantizerWu()
        wu_result = wu.quantize(pixels, max_colors)
        return QuantizerWsMeans.quantize(pixels, wu_result, max_colors)
