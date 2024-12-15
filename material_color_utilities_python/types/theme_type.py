from pydantic import BaseModel, ConfigDict


class ThemeScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    background: int
    error: int
    error_container: int
    inverse_on_surface: int
    inverse_primary: int
    inverse_surface: int
    on_background: int
    on_error: int
    on_error_container: int
    on_primary: int
    on_primary_container: int
    on_secondary: int
    on_secondary_container: int
    on_surface: int
    on_surface_variant: int
    on_tertiary: int
    on_tertiary_container: int
    outline: int
    primary: int
    primary_container: int
    secondary: int
    secondary_container: int
    shadow: int
    surface: int
    surface_variant: int
    tertiary: int
    tertiary_container: int


class ThemeSchemes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dark: ThemeScheme
    light: ThemeScheme


class ThemeTonalPalette(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chroma: float
    hue: float


class ThemePalettes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    primary: ThemeTonalPalette
    secondary: ThemeTonalPalette
    tertiary: ThemeTonalPalette
    neutral: ThemeTonalPalette
    neutral_variant: ThemeTonalPalette
    error: ThemeTonalPalette


class CustomColorScheme(BaseModel):
    color: int
    on_color: int
    color_container: int
    on_color_container: int


class CustomColor(BaseModel):
    value: int
    blend: int


class ThemeCustomColorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    color: CustomColor
    value: int
    light: CustomColorScheme
    dark: CustomColorScheme


class Theme(BaseModel):
    source: int
    schemes: ThemeSchemes
    palettes: ThemePalettes
    custom_colors: list[ThemeCustomColorResponse]
