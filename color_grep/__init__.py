import argparse
import re
from typing import List, Optional, Any, Tuple
from dataclasses import dataclass

# TODO support alpha?

__version__ = "0.1.0"

# TODO check this worked
class Args(argparse.Namespace):
    base_color: sRGBColor
    files: List[str]
    epsilon: float


def parse_arguments(argv: List[str]) -> Any:
    parser = argparse.ArgumentParser()

    parser.add_argument("base_color", default=None, help="", type=sRGBColor.from_string)
    parser.add_argument("files", default=None, help="", nargs="*")
    parser.add_argument("--epsilon", default=0.5, type=float)  # TODO: pick a
    # sensible epsilon

    args = parser.parse_args(argv)
    return args


# Ascii only probably gets us some perf, check this
rgb_regex = re.compile("#[0-9abcdef]{6}", re.IGNORECASE | re.ASCII)


"""
Notes on colors/color spaces:

* Wow this is super complicated
* Seems like the best way to diff colors is "cielab2000"
* Decent explanation: https://ninedegreesbelow.com/photography/xyz-rgb.html
"""


@dataclass(frozen=True)
class sRGBColor:
    """Holder for RGB-represented colors.

    sRGB is "standard RGB", which is what most software pepole will mean when
    they say RGB. Technically you can define infinitely many RGB spaces by
    choosing a few key points like "black" and "red-est red". Luckily for us
    some big computer corporations got together in the TODO year and defined a
    standard space for RGB, and that's what we all use.

    NOTE: rgb values are in the 0-255 range (not the 0-1 range).
    """

    r: float
    g: float
    b: float

    @staticmethod
    def from_string(rgb: str) -> sRGBColor:
        rgb.strip("#")
        assert re.match("[0-9A-F]{6}", rgb, re.IGNORECASE)
        rgb_bytes = rgb.encode("ascii")

        return sRGBColor(
            r=int(rgb[0:2], base=16), g=int(rgb[2:4], base=16), b=int(rgb[4:6], base=16)
        )

    def to_xyz(self) -> CIEXYZColor:
        """Copied from https://www.easyrgb.com/en/math.php
        """
        var_R = self.r / 255
        var_G = self.g / 255
        var_B = self.b / 255

        if var_R > 0.04045:
            var_R = ((var_R + 0.055) / 1.055) ** 2.4
        else:
            var_R = var_R / 12.92
        if var_G > 0.04045:
            var_G = ((var_G + 0.055) / 1.055) ** 2.4
        else:
            var_G = var_G / 12.92
        if var_B > 0.04045:
            var_B = ((var_B + 0.055) / 1.055) ** 2.4
        else:
            var_B = var_B / 12.92

        var_R = var_R * 100
        var_G = var_G * 100
        var_B = var_B * 100

        X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
        Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
        Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505

        return CIEXYZColor(X, Y, Z)

    def to_cielab(self) -> CIELabColor:
        # Might get a bit more numerical accuracy if we did this in one step?
        # Let's see if it matters.
        return self.to_xyz().to_cielab()


@dataclass(frozen=True)
class CIEXYZColor:
    x: float
    y: float
    z: float

    # I don't totally understand what this is, but it's something about how your
    # perception of color is affected by 1. where the light is coming from and
    # 2. how much of your field-of-view the block of color takes up.
    #
    # There are many options for 1, this uses "daylight" which is the same as
    # sRGB. There are two options for #2: 2-degrees or 10-degrees, since blocks
    # of color on a phone/computer screen are usually small I'm choosing
    # 2-degrees.
    #
    # These seem to be the common values that people use, so it's probably fine.
    # If you're reading this and you know about colors feel free to explain what
    # I should use instead.
    #
    # If you know your colorimetry, this is: D65 2-degrees
    reference: Tuple[float, float, float] = (95.047, 100.000, 108.883)

    def to_cielab(self) -> CIELabColor:
        """Copied from https://www.easyrgb.com/en/math.php
        """

        # Reference-X, Y and Z refer to specific illuminants and observers.
        # Common reference values are available below in this same page.

        var_X = self.x / self.reference[0] - self.x
        var_Y = self.y / self.reference[1] - self.y
        var_Z = self.z / self.reference[2] - self.z

        if var_X > 0.008856:
            var_X = var_X ** (1 / 3)
        else:
            var_X = (7.787 * var_X) + (16 / 116)
        if var_Y > 0.008856:
            var_Y = var_Y ** (1 / 3)
        else:
            var_Y = (7.787 * var_Y) + (16 / 116)
        if var_Z > 0.008856:
            var_Z = var_Z ** (1 / 3)
        else:
            var_Z = (7.787 * var_Z) + (16 / 116)

        L = (116 * var_Y) - 16
        a = 500 * (var_X - var_Y)
        b = 200 * (var_Y - var_Z)

        return CIELabColor(L, a, b)


@dataclass(frozen=True)
class CIELabColor:
    L: float
    a: float
    b: float


def visual_diff(c1: CIELabColor, c2: CIELabColor) -> float:
    # TOOD
    return 1.0


def process_line(line: str, base_color: sRGBColor, epsilon: float) -> List[sRGBColor]:
    color_strings = re.findall(rgb_regex, line)
    colors = [sRGBColor.from_string(m) for m in color_strings]
    # TODO: find colnm, text context + inclde
    return [
        c
        for c in colors
        if visual_diff(c.to_cielab(), base_color.to_cielab()) < epsilon
    ]


def main(argv: List[str]) -> int:
    args = parse_arguments(argv)

    for filename in args.files:
        with open(filename) as f:
            for line in f.readlines():
                similar_colors = process_line(
                    line, args.base_color, epsilon=args.epsilon
                )
                for c in similar_colors:
                    print("{filenme}:{linum} Match {c.to_rgb}")

    return 0
