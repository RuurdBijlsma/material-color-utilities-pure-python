import json

from material_color_utilities_python.palettes.core_palette import CorePalette


# /**
#  * Represents a Material color scheme, a mapping of color roles to colors.
#  */
# Using dictionary instead of JavaScript Object
class Scheme:
    def __init__(self, props):
        self.props = props

    def get_primary(self):
        return self.props["primary"]

    def get_primary_container(self):
        return self.props["primary_container"]

    def get_on_primary(self):
        return self.props["on_primary"]

    def get_on_primary_container(self):
        return self.props["on_primary_container"]

    def get_secondary(self):
        return self.props["secondary"]

    def get_secondary_container(self):
        return self.props["secondary_container"]

    def get_on_secondary(self):
        return self.props["on_secondary"]

    def get_on_secondary_container(self):
        return self.props["on_secondary_container"]

    def get_tertiary(self):
        return self.props["tertiary"]

    def get_on_tertiary(self):
        return self.props["on_tertiary"]

    def get_tertiary_container(self):
        return self.props["tertiary_container"]

    def get_on_tertiary_container(self):
        return self.props["on_tertiary_container"]

    def get_error(self):
        return self.props["error"]

    def get_on_error(self):
        return self.props["on_error"]

    def get_error_container(self):
        return self.props["error_container"]

    def get_on_error_container(self):
        return self.props["on_error_container"]

    def get_background(self):
        return self.props["background"]

    def get_on_background(self):
        return self.props["on_background"]

    def get_surface(self):
        return self.props["surface"]

    def get_on_surface(self):
        return self.props["on_surface"]

    def get_surface_variant(self):
        return self.props["surface_variant"]

    def get_on_surface_variant(self):
        return self.props["on_surface_variant"]

    def get_outline(self):
        return self.props["outline"]

    def get_shadow(self):
        return self.props["shadow"]

    def get_inverse_surface(self):
        return self.props["inverse_surface"]

    def get_inverse_on_surface(self):
        return self.props["inverse_on_surface"]

    def get_inverse_primary(self):
        return self.props["inverse_primary"]

    primary = property(get_primary)
    primary_container = property(get_primary_container)
    on_primary = property(get_on_primary)
    on_primary_container = property(get_on_primary_container)
    secondary = property(get_secondary)
    secondary_container = property(get_secondary_container)
    on_secondary = property(get_on_secondary)
    on_secondary_container = property(get_on_secondary_container)
    tertiary = property(get_tertiary)
    on_tertiary = property(get_on_tertiary)
    tertiary_container = property(get_tertiary_container)
    on_tertiary_container = property(get_on_tertiary_container)
    error = property(get_error)
    on_error = property(get_on_error)
    error_container = property(get_error_container)
    on_error_container = property(get_on_error_container)
    background = property(get_background)
    on_background = property(get_on_background)
    surface = property(get_surface)
    on_surface = property(get_on_surface)
    surface_variant = property(get_surface_variant)
    on_surface_variant = property(get_on_surface_variant)
    outline = property(get_outline)
    shadow = property(get_shadow)
    inverse_surface = property(get_inverse_surface)
    inverse_on_surface = property(get_inverse_on_surface)
    inverse_primary = property(get_inverse_primary)

    # /**
    #  * @param argb ARGB representation of a color.
    #  * @return Light Material color scheme, based on the color's hue.
    #  */
    @staticmethod
    def light(argb):
        core = CorePalette.of(argb)
        return Scheme(
            {
                "primary": core.a1.tone(40),
                "on_primary": core.a1.tone(100),
                "primary_container": core.a1.tone(90),
                "on_primary_container": core.a1.tone(10),
                "secondary": core.a2.tone(40),
                "on_secondary": core.a2.tone(100),
                "secondary_container": core.a2.tone(90),
                "on_secondary_container": core.a2.tone(10),
                "tertiary": core.a3.tone(40),
                "on_tertiary": core.a3.tone(100),
                "tertiary_container": core.a3.tone(90),
                "on_tertiary_container": core.a3.tone(10),
                "error": core.error.tone(40),
                "on_error": core.error.tone(100),
                "error_container": core.error.tone(90),
                "on_error_container": core.error.tone(10),
                "background": core.n1.tone(99),
                "on_background": core.n1.tone(10),
                "surface": core.n1.tone(99),
                "on_surface": core.n1.tone(10),
                "surface_variant": core.n2.tone(90),
                "on_surface_variant": core.n2.tone(30),
                "outline": core.n2.tone(50),
                "shadow": core.n1.tone(0),
                "inverse_surface": core.n1.tone(20),
                "inverse_on_surface": core.n1.tone(95),
                "inverse_primary": core.a1.tone(80),
            }
        )

    # /**
    #  * @param argb ARGB representation of a color.
    #  * @return Dark Material color scheme, based on the color's hue.
    #  */
    @staticmethod
    def dark(argb):
        core = CorePalette.of(argb)
        return Scheme(
            {
                "primary": core.a1.tone(80),
                "on_primary": core.a1.tone(20),
                "primary_container": core.a1.tone(30),
                "on_primary_container": core.a1.tone(90),
                "secondary": core.a2.tone(80),
                "on_secondary": core.a2.tone(20),
                "secondary_container": core.a2.tone(30),
                "on_secondary_container": core.a2.tone(90),
                "tertiary": core.a3.tone(80),
                "on_tertiary": core.a3.tone(20),
                "tertiary_container": core.a3.tone(30),
                "on_tertiary_container": core.a3.tone(90),
                "error": core.error.tone(80),
                "on_error": core.error.tone(20),
                "error_container": core.error.tone(30),
                "on_error_container": core.error.tone(80),
                "background": core.n1.tone(10),
                "on_background": core.n1.tone(90),
                "surface": core.n1.tone(10),
                "on_surface": core.n1.tone(90),
                "surface_variant": core.n2.tone(30),
                "on_surface_variant": core.n2.tone(80),
                "outline": core.n2.tone(60),
                "shadow": core.n1.tone(0),
                "inverse_surface": core.n1.tone(90),
                "inverse_on_surface": core.n1.tone(20),
                "inverse_primary": core.a1.tone(40),
            }
        )

    def to_json(self):
        return json.dumps(self.props)
