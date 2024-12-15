# /**
#  * Generate custom color group from source and target color
#  *
#  * @param source Source color
#  * @param color Custom color
#  * @return Custom color group
#  *
#  * @link https://m3.material.io/styles/color/the-color-system/color-roles
#  */
# NOTE: Changes made to output format to be Dictionary
from material_color_utilities_python.blend.blend import Blend
from material_color_utilities_python.palettes.core_palette import CorePalette
from material_color_utilities_python.scheme.scheme import Scheme
from material_color_utilities_python.types.theme_type import Theme
from material_color_utilities_python.utils.image_utils import source_color_from_image


def custom_color(source, color):
    value = color["value"]
    from_v = value
    to = source
    if color["blend"]:
        value = Blend.harmonize(from_v, to)
    palette = CorePalette.of(value)
    tones = palette.a1
    return {
        "color": color,
        "value": value,
        "light": {
            "color": tones.tone(40),
            "on_color": tones.tone(100),
            "color_container": tones.tone(90),
            "on_color_container": tones.tone(10),
        },
        "dark": {
            "color": tones.tone(80),
            "on_color": tones.tone(20),
            "color_container": tones.tone(30),
            "on_color_container": tones.tone(90),
        },
    }


# /**
#  * Generate a theme from a source color
#  *
#  * @param source Source color
#  * @param custom_colors Array of custom colors
#  * @return Theme object
#  */
# NOTE: Changes made to output format to be Dictionary
def theme_from_source_color(source, custom_colors=[]) -> Theme:
    palette = CorePalette.of(source)
    return Theme.model_validate({
        "source": source,
        "schemes": {
            "light": Scheme.light(source),
            "dark": Scheme.dark(source),
        },
        "palettes": {
            "primary": palette.a1,
            "secondary": palette.a2,
            "tertiary": palette.a3,
            "neutral": palette.n1,
            "neutral_variant": palette.n2,
            "error": palette.error,
        },
        "custom_colors": [custom_color(source, c) for c in custom_colors],
    })


# /**
#  * Generate a theme from an image source
#  *
#  * @param image Image element
#  * @param custom_colors Array of custom colors
#  * @return Theme object
#  */
def theme_from_image(image, custom_colors=[]):
    source = source_color_from_image(image)
    return theme_from_source_color(source, custom_colors)


# Not really applicable to python CLI
# # /**
# #  * Apply a theme to an element
# #  *
# #  * @param theme Theme object
# #  * @param options Options
# #  */
# export function applyTheme(theme, options) {
#     var _a;
#     const target = (options === null || options === void 0 ? void 0 : options.target) || document.body;
#     const isDark = (_a = options === null || options === void 0 ? void 0 : options.dark) !== null && _a !== void 0 ? _a : false;
#     const scheme = isDark ? theme.schemes.dark : theme.schemes.light;
#     for (const [key, value] of Object.entries(scheme.toJSON())) {
#         const token = key.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
#         const color = hex_from_argb(value);
#         target.style.setProperty(`--md-sys-color-${token}`, color);
#     }
# }
# //# sourceMappingURL=theme_utils.js.map
