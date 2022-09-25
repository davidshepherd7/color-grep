"""
Notes on colors/color spaces:

* Wow this is super complicated
* Seems like the best way to diff colors is "cielab2000"
* Decent explanation: https://ninedegreesbelow.com/photography/xyz-rgb.html
"""

from dataclasses import dataclass
from math import sqrt, cos, sin, exp, atan, degrees, radians
from typing import List, Optional, Any, Tuple
import re


@dataclass(frozen=True)
class sRGBColor:
    """Holder for RGB-represented colors.

    sRGB is "standard RGB", which is what most software pepole will mean when
    they say RGB. Technically you can define infinitely many RGB spaces by
    choosing a few key points like "black" and "red-est red". Luckily for us
    Microsoft and HP got together in 1996 and defined a standard space for RGB,
    and that's what we all use these days.

    NOTE: rgb values are in the 0-255 range (not the 0-1 range).

    """

    r: int
    g: int
    b: int

    @staticmethod
    def from_string(rgb: str) -> "sRGBColor":
        if not re.match("#[0-9A-F]{6}", rgb, re.IGNORECASE):
            raise ValueError(f"Not an rgb color: {rgb}")

        return sRGBColor(
            r=int(rgb[1:3], base=16), g=int(rgb[3:5], base=16), b=int(rgb[5:7], base=16)
        )

    def to_string(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_xyz(self) -> "CIEXYZColor":
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

    def to_cielab(self) -> "CIELabColor":
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

    def to_cielab(self) -> "CIELabColor":
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


def _cie_lab_to_hue(var_a: float, var_b: float) -> float:
    """          //Function returns CIE-H° value"""
    var_bias = 0
    if var_a >= 0 and var_b == 0:
        return 0
    if var_a < 0 and var_b == 0:
        return 180
    if var_a == 0 and var_b > 0:
        return 90
    if var_a == 0 and var_b < 0:
        return 270

    if var_a > 0 and var_b > 0:
        var_bias = 0
    if var_a < 0:
        var_bias = 180
    if var_a > 0 and var_b < 0:
        var_bias = 360
    return degrees(atan(var_b / var_a)) + var_bias


def visual_diff(c1: CIELabColor, c2: CIELabColor) -> float:
    """The CIE delta-E 2000 metric.

    A distance of 1.0 is "just noticable".

    From https://www.easyrgb.com/en/math.php again, with weights set to 1
    (Wikipedia says that they are usually all set to 1).
    """

    xC1 = sqrt(c1.a * c1.a + c1.b * c1.b)
    xC2 = sqrt(c2.a * c2.a + c2.b * c2.b)
    xCX = (xC1 + xC2) / 2
    xGX = 0.5 * (1 - sqrt((xCX ** 7) / ((xCX ** 7) + (25 ** 7))))
    xNN = (1 + xGX) * c1.a
    xC1 = sqrt(xNN * xNN + c1.b * c1.b)
    xH1 = _cie_lab_to_hue(xNN, c1.b)
    xNN = (1 + xGX) * c2.a
    xC2 = sqrt(xNN * xNN + c2.b * c2.b)
    xH2 = _cie_lab_to_hue(xNN, c2.b)
    xDL = c2.L - c1.L
    xDC = xC2 - xC1

    xDH: float
    if (xC1 * xC2) == 0:
        xDH = 0

    else:
        xNN = round(xH2 - xH1, 12)
        if abs(xNN) <= 180:
            xDH = xH2 - xH1
        else:
            if xNN > 180:
                xDH = xH2 - xH1 - 360
            else:
                xDH = xH2 - xH1 + 360

    xDH = 2 * sqrt(xC1 * xC2) * sin(radians(xDH / 2))
    xLX = (c1.L + c2.L) / 2
    xCY = (xC1 + xC2) / 2
    if (xC1 * xC2) == 0:
        xHX = xH1 + xH2

    else:
        xNN = abs(round(xH1 - xH2, 12))
        if xNN > 180:
            if (xH2 + xH1) < 360:
                xHX = xH1 + xH2 + 360
            else:
                xHX = xH1 + xH2 - 360

        else:
            xHX = xH1 + xH2

        xHX /= 2

    xTX = 1 - (
        0.17 * cos(radians(xHX - 30))
        + 0.24 * cos(radians(2 * xHX))
        + 0.32 * cos(radians(3 * xHX + 6))
        - 0.20 * cos(radians(4 * xHX - 63))
    )
    xPH = 30 * exp(-((xHX - 275) / 25) * ((xHX - 275) / 25))
    xRC = 2 * sqrt((xCY ** 7) / ((xCY ** 7) + (25 ** 7)))
    xSL = 1 + (
        (0.015 * ((xLX - 50) * (xLX - 50))) / sqrt(20 + ((xLX - 50) * (xLX - 50)))
    )

    xSC = 1 + 0.045 * xCY
    xSH = 1 + 0.015 * xCY * xTX
    xRT = -sin(radians(2 * xPH)) * xRC
    xDL = xDL / xSL
    xDC = xDC / xSC
    xDH = xDH / xSH

    return sqrt(xDL ** 2 + xDC ** 2 + xDH ** 2 + xRT * xDC * xDH)
