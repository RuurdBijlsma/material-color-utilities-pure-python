import math
import random
from collections import OrderedDict

from material_color_utilities_python.quantize.lab_point_provider import (
    lab_distance,
    lab_to_int,
)
from material_color_utilities_python.utils.color_utils import lab_from_argb

MAX_ITERATIONS = 10
MIN_MOVEMENT_DISTANCE = 3.0


# /**
#  * An image quantizer that improves on the speed of a standard K-Means algorithm
#  * by implementing several optimizations, including deduping identical pixels
#  * and a triangle inequality rule that reduces the number of comparisons needed
#  * to identify which cluster a point should be moved to.
#  *
#  * Wsmeans stands for Weighted Square Means.
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
class QuantizerWsMeans:
    # /**
    #  * @param inputPixels Colors in ARGB format.
    #  * @param startingClusters Defines the initial state of the quantizer. Passing
    #  *     an empty array is fine, the implementation will create its own initial
    #  *     state that leads to reproducible results for the same inputs.
    #  *     Passing an array that is the result of Wu quantization leads to higher
    #  *     quality results.
    #  * @param maxColors The number of colors to divide the image into. A lower
    #  *     number of colors may be returned.
    #  * @return Colors in ARGB format.
    #  */
    # Replacing Map() with OrderedDict()
    @staticmethod
    def quantize(input_pixels, starting_clusters, max_colors):
        random.seed(69)
        pixel_to_count = OrderedDict()
        points = []
        pixels = []
        point_count = 0
        for i in range(len(input_pixels)):
            input_pixel = input_pixels[i]
            if input_pixel not in pixel_to_count.keys():
                point_count += 1
                points.append(lab_from_argb(input_pixel))
                pixels.append(input_pixel)
                pixel_to_count[input_pixel] = 1
            else:
                pixel_to_count[input_pixel] = pixel_to_count[input_pixel] + 1
        counts = []
        for i in range(point_count):
            pixel = pixels[i]
            if pixel in pixel_to_count.keys():
                # counts[i] = pixel_to_count[pixel]
                counts.append(pixel_to_count[pixel])
        cluster_count = min(max_colors, point_count)
        if len(starting_clusters) > 0:
            cluster_count = min(cluster_count, len(starting_clusters))
        clusters = []
        for i in range(len(starting_clusters)):
            clusters.append(lab_from_argb(starting_clusters[i]))
        additional_clusters_needed = cluster_count - len(clusters)
        if len(starting_clusters) == 0 and additional_clusters_needed > 0:
            for i in range(additional_clusters_needed):
                lightness = random.uniform(0, 1) * 100.0
                a = random.uniform(0, 1) * (100.0 - (-100.0) + 1) + -100
                b = random.uniform(0, 1) * (100.0 - (-100.0) + 1) + -100
                clusters.append([lightness, a, b])
        cluster_indices = []
        for i in range(point_count):
            cluster_indices.append(math.floor(random.uniform(0, 1) * cluster_count))
        index_matrix = []
        for i in range(cluster_count):
            index_matrix.append([])
            for j in range(cluster_count):
                index_matrix[i].append(0)
        distance_to_index_matrix = []
        for i in range(cluster_count):
            distance_to_index_matrix.append([])
            for j in range(cluster_count):
                distance_to_index_matrix[i].append(DistanceAndIndex())
        pixel_count_sums = []
        for i in range(cluster_count):
            pixel_count_sums.append(0)
        for iteration in range(MAX_ITERATIONS):
            for i in range(cluster_count):
                for j in range(i + 1, cluster_count):
                    distance = lab_distance(clusters[i], clusters[j])
                    distance_to_index_matrix[j][i].distance = distance
                    distance_to_index_matrix[j][i].index = i
                    distance_to_index_matrix[i][j].distance = distance
                    distance_to_index_matrix[i][j].index = j
                # This sort here doesn't seem to do anything because arr of objects
                # leaving just in case though
                # distance_to_index_matrix[i].sort()
                for j in range(cluster_count):
                    index_matrix[i][j] = distance_to_index_matrix[i][j].index
            points_moved = 0
            for i in range(point_count):
                point = points[i]
                previous_cluster_index = cluster_indices[i]
                previous_cluster = clusters[previous_cluster_index]
                previous_distance = lab_distance(point, previous_cluster)
                minimum_distance = previous_distance
                new_cluster_index = -1
                for j in range(cluster_count):
                    if (
                        distance_to_index_matrix[previous_cluster_index][j].distance
                        >= 4 * previous_distance
                    ):
                        continue
                    distance = lab_distance(point, clusters[j])
                    if distance < minimum_distance:
                        minimum_distance = distance
                        new_cluster_index = j
                if new_cluster_index != -1:
                    distance_change = abs(
                        (math.sqrt(minimum_distance) - math.sqrt(previous_distance))
                    )
                    if distance_change > MIN_MOVEMENT_DISTANCE:
                        points_moved += 1
                        cluster_indices[i] = new_cluster_index
            if points_moved == 0 and iteration != 0:
                break
            component_a_sums = [0] * cluster_count
            component_b_sums = [0] * cluster_count
            component_c_sums = [0] * cluster_count
            for i in range(cluster_count):
                pixel_count_sums[i] = 0
            for i in range(point_count):
                cluster_index = cluster_indices[i]
                point = points[i]
                count = counts[i]
                pixel_count_sums[cluster_index] += count
                component_a_sums[cluster_index] += point[0] * count
                component_b_sums[cluster_index] += point[1] * count
                component_c_sums[cluster_index] += point[2] * count
            for i in range(cluster_count):
                count = pixel_count_sums[i]
                if count == 0:
                    clusters[i] = [0.0, 0.0, 0.0]
                    continue
                a = component_a_sums[i] / count
                b = component_b_sums[i] / count
                c = component_c_sums[i] / count
                clusters[i] = [a, b, c]
        argb_to_population = OrderedDict()
        for i in range(cluster_count):
            count = pixel_count_sums[i]
            if count == 0:
                continue
            possible_new_cluster = lab_to_int(clusters[i])
            if possible_new_cluster in argb_to_population.keys():
                continue
            argb_to_population[possible_new_cluster] = count
        return argb_to_population


# /**
#  *  A wrapper for maintaining a table of distances between K-Means clusters.
#  */
class DistanceAndIndex:
    def __init__(self):
        self.distance = -1
        self.index = -1
