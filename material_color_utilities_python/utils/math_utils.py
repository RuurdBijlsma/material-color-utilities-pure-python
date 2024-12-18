#
# Utility methods for mathematical operations.
#
#
# The signum function.
#
# @return 1 if num > 0, -1 if num < 0, and 0 if num = 0
#
def signum(num):
    if num < 0:
        return -1
    elif num == 0:
        return 0
    else:
        return 1

# /**
#  * The linear interpolation function.
#  *
#  * @return start if amount = 0 and stop if amount = 1
#  */
def lerp(start, stop, amount):
    return (1.0 - amount) * start + amount * stop

# /**
#  * Clamps an integer between two integers.
#  *
#  * @return input when min <= input <= max, and either min or max
#  * otherwise.
#  */
def clamp_int(minimum, maximum, value):
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    return value

# /**
#  * Clamps an integer between two floating-point numbers.
#  *
#  * @return input when min <= input <= max, and either min or max
#  * otherwise.
#  */
def clamp_double(minimum, maximum, value):
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    return value

# /**
#  * Sanitizes a degree measure as an integer.
#  *
#  * @return a degree measure between 0 (inclusive) and 360
#  * (exclusive).
#  */
def sanitize_degrees_int(degrees):
    degrees = degrees % 360
    if degrees < 0:
        degrees = degrees + 360
    return degrees

# /**
#  * Sanitizes a degree measure as a floating-point number.
#  *
#  * @return a degree measure between 0.0 (inclusive) and 360.0
#  * (exclusive).
#  */
def sanitize_degrees_double(degrees):
    degrees = degrees % 360.0
    if degrees < 0:
        degrees = degrees + 360.0
    return degrees

# /**
#  * Distance of two points on a circle, represented using degrees.
#  */
def difference_degrees(a, b):
    return 180.0 - abs(abs(a - b) - 180.0)

# /**
#  * Multiplies a 1x3 row vector with a 3x3 matrix.
#  */
def matrix_multiply(row, matrix):
    a = row[0] * matrix[0][0] + row[1] * matrix[0][1] + row[2] * matrix[0][2]
    b = row[0] * matrix[1][0] + row[1] * matrix[1][1] + row[2] * matrix[1][2]
    c = row[0] * matrix[2][0] + row[1] * matrix[2][1] + row[2] * matrix[2][2]
    return [a, b, c]