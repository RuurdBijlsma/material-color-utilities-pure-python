from material_color_utilities_python.quantize.quantizer_map import QuantizerMap
from material_color_utilities_python.utils.color_utils import (
    blue_from_argb,
    green_from_argb,
    red_from_argb,
)

INDEX_BITS = 5
SIDE_LENGTH = 33 # ((1 << INDEX_INDEX_BITS) + 1)
TOTAL_SIZE = 35937 # SIDE_LENGTH * SIDE_LENGTH * SIDE_LENGTH
directions = {
    "RED" : 'red',
    "GREEN" : 'green',
    "BLUE": 'blue',
}

# /**
#  * An image quantizer that divides the image's pixels into clusters by
#  * recursively cutting an RGB cube, based on the weight of pixels in each area
#  * of the cube.
#  *
#  * The algorithm was described by Xiaolin Wu in Graphic Gems II, published in
#  * 1991.
#  */
class QuantizerWu:
    def __init__(self, weights = [], moments_r = [], moments_g = [], moments_b = [], moments = [], cubes = []):
        self.weights = weights
        self.moments_r = moments_r
        self.moments_g = moments_g
        self.moments_b = moments_b
        self.moments = moments
        self.cubes = cubes

    # /**
    #  * @param pixels Colors in ARGB format.
    #  * @param maxColors The number of colors to divide the image into. A lower
    #  *     number of colors may be returned.
    #  * @return Colors in ARGB format.
    #  */
    def quantize(self, pixels, max_colors):
        self.construct_histogram(pixels)
        self.compute_moments()
        create_boxes_result = self.create_boxes(max_colors)
        results = self.create_result(create_boxes_result.result_count)
        return results

    def construct_histogram(self, pixels):
        _a = None
        self.weights = [0] * TOTAL_SIZE
        self.moments_r = [0] * TOTAL_SIZE
        self.moments_g = [0] * TOTAL_SIZE
        self.moments_b = [0] * TOTAL_SIZE
        self.moments = [0] * TOTAL_SIZE
        count_by_color = QuantizerMap.quantize(pixels)
        for (pixel, count) in count_by_color.items():
            red = red_from_argb(pixel)
            green = green_from_argb(pixel)
            blue = blue_from_argb(pixel)
            bits_to_remove = 8 - INDEX_BITS
            i_r = (red >> bits_to_remove) + 1
            i_g = (green >> bits_to_remove) + 1
            i_b = (blue >> bits_to_remove) + 1
            index = self.get_index(i_r, i_g, i_b)
            self.weights[index] = (self.weights[index] if len(self.weights) > index else 0) + count
            self.moments_r[index] += count * red
            self.moments_g[index] += count * green
            self.moments_b[index] += count * blue
            self.moments[index] += count * (red * red + green * green + blue * blue)

    def compute_moments(self):
        for r in range(1, SIDE_LENGTH):
            area = [0] * SIDE_LENGTH
            area_r = [0] * SIDE_LENGTH
            area_g = [0] * SIDE_LENGTH
            area_b = [0] * SIDE_LENGTH
            area2 = [0.0] * SIDE_LENGTH
            for g in range(1, SIDE_LENGTH):
                line = 0
                line_r = 0
                line_g = 0
                line_b = 0
                line2 = 0.0
                for b in range(1, SIDE_LENGTH):
                    index = self.get_index(r, g, b)
                    line += self.weights[index]
                    line_r += self.moments_r[index]
                    line_g += self.moments_g[index]
                    line_b += self.moments_b[index]
                    line2 += self.moments[index]
                    area[b] += line
                    area_r[b] += line_r
                    area_g[b] += line_g
                    area_b[b] += line_b
                    area2[b] += line2
                    previous_index = self.get_index(r - 1, g, b)
                    self.weights[index] = self.weights[previous_index] + area[b]
                    self.moments_r[index] = self.moments_r[previous_index] + area_r[b]
                    self.moments_g[index] = self.moments_g[previous_index] + area_g[b]
                    self.moments_b[index] = self.moments_b[previous_index] + area_b[b]
                    self.moments[index] = self.moments[previous_index] + area2[b]

    def create_boxes(self, max_colors):
        self.cubes = [Box() for _ in [0] * max_colors]
        volume_variance = [0.0] * max_colors
        self.cubes[0].r0 = 0
        self.cubes[0].g0 = 0
        self.cubes[0].b0 = 0
        self.cubes[0].r1 = SIDE_LENGTH - 1
        self.cubes[0].g1 = SIDE_LENGTH - 1
        self.cubes[0].b1 = SIDE_LENGTH - 1
        generated_color_count = max_colors
        next_index = 0
        for i in range(1, max_colors):
            if self.cut(self.cubes[next_index], self.cubes[i]):
                volume_variance[next_index] = self.variance(self.cubes[next_index]) if self.cubes[next_index].vol > 1 else 0.0
                volume_variance[i] = self.variance(self.cubes[i]) if self.cubes[i].vol > 1 else 0.0
            else:
                volume_variance[next_index] = 0.0
                i -= 1
            next_index = 0
            temp = volume_variance[0]
            for j in range(1, i):
                if volume_variance[j] > temp:
                    temp = volume_variance[j]
                    next_index = j
            if temp <= 0.0:
                generated_color_count = i + 1
                break
        return CreateBoxesResult(max_colors, generated_color_count)

    def create_result(self, color_count):
        colors = []
        for i in range(color_count):
            cube = self.cubes[i]
            weight = self.volume(cube, self.weights)
            if weight > 0:
                r = round(self.volume(cube, self.moments_r) / weight)
                g = round(self.volume(cube, self.moments_g) / weight)
                b = round(self.volume(cube, self.moments_b) / weight)
                color = (255 << 24) | ((r & 0x0ff) << 16) | ((g & 0x0ff) << 8) | (b & 0x0ff)
                colors.append(color)
        return colors

    def variance(self, cube):
        dr = self.volume(cube, self.moments_r)
        dg = self.volume(cube, self.moments_g)
        db = self.volume(cube, self.moments_b)
        xx = self.moments[self.get_index(cube.r1, cube.g1, cube.b1)] - self.moments[self.get_index(cube.r1, cube.g1, cube.b0)] - self.moments[self.get_index(cube.r1, cube.g0, cube.b1)] + self.moments[self.get_index(cube.r1, cube.g0, cube.b0)] - self.moments[self.get_index(cube.r0, cube.g1, cube.b1)] + self.moments[self.get_index(cube.r0, cube.g1, cube.b0)] + self.moments[self.get_index(cube.r0, cube.g0, cube.b1)] - self.moments[self.get_index(cube.r0, cube.g0, cube.b0)]
        hypotenuse = dr * dr + dg * dg + db * db
        volume = self.volume(cube, self.weights)
        return xx - hypotenuse / volume

    def cut(self, one, two):
        whole_r = self.volume(one, self.moments_r)
        whole_g = self.volume(one, self.moments_g)
        whole_b = self.volume(one, self.moments_b)
        whole_w = self.volume(one, self.weights)
        max_r_result = self.maximize(one, directions["RED"], one.r0 + 1, one.r1, whole_r, whole_g, whole_b, whole_w)
        max_g_result = self.maximize(one, directions["GREEN"], one.g0 + 1, one.g1, whole_r, whole_g, whole_b, whole_w)
        max_b_result = self.maximize(one, directions["BLUE"], one.b0 + 1, one.b1, whole_r, whole_g, whole_b, whole_w)
        max_r = max_r_result.maximum
        max_g = max_g_result.maximum
        max_b = max_b_result.maximum
        if max_r >= max_g and max_r >= max_b:
            if max_r_result.cut_location < 0:
                return False
            direction = directions["RED"]
        elif max_g >= max_r and max_g >= max_b:
            direction = directions["GREEN"]
        else:
            direction = directions["BLUE"]
        two.r1 = one.r1
        two.g1 = one.g1
        two.b1 = one.b1

        if direction == directions["RED"]:
            one.r1 = max_r_result.cut_location
            two.r0 = one.r1
            two.g0 = one.g0
            two.b0 = one.b0
        elif direction == directions["GREEN"]:
            one.g1 = max_g_result.cut_location
            two.r0 = one.r0
            two.g0 = one.g1
            two.b0 = one.b0
        elif direction == directions["BLUE"]:
            one.b1 = max_b_result.cut_location
            two.r0 = one.r0
            two.g0 = one.g0
            two.b0 = one.b1
        else:
            raise Exception('unexpected direction ' + direction)

        one.vol = (one.r1 - one.r0) * (one.g1 - one.g0) * (one.b1 - one.b0)
        two.vol = (two.r1 - two.r0) * (two.g1 - two.g0) * (two.b1 - two.b0)
        return True

    def maximize(self, cube, direction, first, last, whole_r, whole_g, whole_b, whole_w):
        bottom_r = self.bottom(cube, direction, self.moments_r)
        bottom_g = self.bottom(cube, direction, self.moments_g)
        bottom_b = self.bottom(cube, direction, self.moments_b)
        bottom_w = self.bottom(cube, direction, self.weights)
        maximized = 0.0
        cut = -1
        for i in range(first, last):
            half_r = bottom_r + self.top(cube, direction, i, self.moments_r)
            half_g = bottom_g + self.top(cube, direction, i, self.moments_g)
            half_b = bottom_b + self.top(cube, direction, i, self.moments_b)
            half_w = bottom_w + self.top(cube, direction, i, self.weights)
            if half_w == 0:
                continue
            temp_numerator = (half_r * half_r + half_g * half_g + half_b * half_b) * 1.0
            temp_denominator = half_w * 1.0
            temp = temp_numerator / temp_denominator
            half_r = whole_r - half_r
            half_g = whole_g - half_g
            half_b = whole_b - half_b
            half_w = whole_w - half_w
            if half_w == 0:
                continue
            temp_numerator = (half_r * half_r + half_g * half_g + half_b * half_b) * 1.0
            temp_denominator = half_w * 1.0
            temp += temp_numerator / temp_denominator
            if temp > maximized:
                maximized = temp
                cut = i
        return MaximizeResult(cut, maximized)

    def volume(self, cube, moment):
        return moment[self.get_index(cube.r1, cube.g1, cube.b1)] - moment[self.get_index(cube.r1, cube.g1, cube.b0)] - moment[self.get_index(cube.r1, cube.g0, cube.b1)] + moment[self.get_index(cube.r1, cube.g0, cube.b0)] - moment[self.get_index(cube.r0, cube.g1, cube.b1)] + moment[self.get_index(cube.r0, cube.g1, cube.b0)] + moment[self.get_index(cube.r0, cube.g0, cube.b1)] - moment[self.get_index(cube.r0, cube.g0, cube.b0)]

    def bottom(self, cube, direction, moment):
        if direction == directions["RED"]:
            return -moment[self.get_index(cube.r0, cube.g1, cube.b1)] + moment[self.get_index(cube.r0, cube.g1, cube.b0)] + moment[self.get_index(cube.r0, cube.g0, cube.b1)] - moment[self.get_index(cube.r0, cube.g0, cube.b0)]
        elif direction == directions["GREEN"]:
            return -moment[self.get_index(cube.r1, cube.g0, cube.b1)] + moment[self.get_index(cube.r1, cube.g0, cube.b0)] + moment[self.get_index(cube.r0, cube.g0, cube.b1)] - moment[self.get_index(cube.r0, cube.g0, cube.b0)]
        elif direction == directions["BLUE"]:
            return -moment[self.get_index(cube.r1, cube.g1, cube.b0)] + moment[self.get_index(cube.r1, cube.g0, cube.b0)] + moment[self.get_index(cube.r0, cube.g1, cube.b0)] - moment[self.get_index(cube.r0, cube.g0, cube.b0)]
        else:
            raise Exception('unexpected direction ' + direction)

    def top(self, cube, direction, position, moment):
        if direction == directions["RED"]:
            return moment[self.get_index(position, cube.g1, cube.b1)] - moment[self.get_index(position, cube.g1, cube.b0)] - moment[self.get_index(position, cube.g0, cube.b1)] + moment[self.get_index(position, cube.g0, cube.b0)]
        elif direction == directions["GREEN"]:
            return moment[self.get_index(cube.r1, position, cube.b1)] - moment[self.get_index(cube.r1, position, cube.b0)] - moment[self.get_index(cube.r0, position, cube.b1)] + moment[self.get_index(cube.r0, position, cube.b0)]
        elif direction == directions["BLUE"]:
            return moment[self.get_index(cube.r1, cube.g1, position)] - moment[self.get_index(cube.r1, cube.g0, position)] - moment[self.get_index(cube.r0, cube.g1, position)] + moment[self.get_index(cube.r0, cube.g0, position)]
        else:
            raise Exception('unexpected direction ' + direction)

    def get_index(self, r, g, b):
        return (r << (INDEX_BITS * 2)) + (r << (INDEX_BITS + 1)) + r + (g << INDEX_BITS) + g + b

# /**
#  * Keeps track of the state of each box created as the Wu  quantization
#  * algorithm progresses through dividing the image's pixels as plotted in RGB.
#  */
class Box:
    def __init__(self, r0 = 0, r1 = 0, g0 = 0, g1 = 0, b0 = 0, b1 = 0, vol = 0):
        self.r0 = r0
        self.r1 = r1
        self.g0 = g0
        self.g1 = g1
        self.b0 = b0
        self.b1 = b1
        self.vol = vol

# /**
#  * Represents final result of Wu algorithm.
#  */
class CreateBoxesResult:
    # /**
    #  * @param requested_count how many colors the caller asked to be returned from
    #  *     quantization.
    #  * @param result_count the actual number of colors achieved from quantization.
    #  *     May be lower than the requested count.
    #  */
    def __init__(self, requested_count, result_count):
        self.requested_count = requested_count
        self.result_count = result_count

# /**
#  * Represents the result of calculating where to cut an existing box in such
#  * a way to maximize variance between the two new boxes created by a cut.
#  */
class MaximizeResult:
    def __init__(self, cut_location, maximum):
        self.cut_location = cut_location
        self.maximum = maximum
