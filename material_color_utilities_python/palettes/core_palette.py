# /**
#  * An intermediate concept between the key color for a UI theme, and a full
#  * color scheme. 5 sets of tones are generated, all except one use the same hue
#  * as the key color, and all vary in chroma.
#  */
from material_color_utilities_python.hct.hct import Hct
from material_color_utilities_python.palettes.tonal_palette import TonalPalette


class CorePalette:
    def __init__(self, argb):
        hct = Hct.from_int(argb)
        hue = hct.hue
        self.a1 = TonalPalette.from_hue_and_chroma(hue, max(48, hct.chroma))
        self.a2 = TonalPalette.from_hue_and_chroma(hue, 16)
        self.a3 = TonalPalette.from_hue_and_chroma(hue + 60, 24)
        self.n1 = TonalPalette.from_hue_and_chroma(hue, 4)
        self.n2 = TonalPalette.from_hue_and_chroma(hue, 8)
        self.error = TonalPalette.from_hue_and_chroma(25, 84)

    # /**
    #  * @param argb ARGB representation of a color
    #  */
    @staticmethod
    def of(argb):
        return CorePalette(argb)
