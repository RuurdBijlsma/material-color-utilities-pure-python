from collections import OrderedDict

from material_color_utilities_python.hct.hct import Hct


# /**
#  *  A convenience class for retrieving colors that are constant in hue and
#  *  chroma, but vary in tone.
#  */
class TonalPalette:
    # Using OrderedDict() as replacement for Map()
    def __init__(self, hue, chroma):
        self.hue = hue
        self.chroma = chroma
        self.cache = OrderedDict()

    # /**
    #  * @param argb ARGB representation of a color
    #  * @return Tones matching that color's hue and chroma.
    #  */
    @staticmethod
    def from_int(argb):
        hct = Hct.from_int(argb)
        return TonalPalette.from_hue_and_chroma(hct.hue, hct.chroma)

    # /**
    #  * @param hue HCT hue
    #  * @param chroma HCT chroma
    #  * @return Tones matching hue and chroma.
    #  */
    @staticmethod
    def from_hue_and_chroma(hue, chroma):
        return TonalPalette(hue, chroma)

    # /**
    #  * @param tone HCT tone, measured from 0 to 100.
    #  * @return ARGB representation of a color with that tone.
    #  */
    def tone(self, tone):
        if tone not in self.cache.keys():
            argb = Hct.from_hct(self.hue, self.chroma, tone).to_int()
            self.cache[tone] = argb
        else:
            argb = self.cache[tone]
        return argb
