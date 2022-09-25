from color_grep.color import visual_diff
from color_grep.color import sRGBColor


some_colors = [
    # black and white
    "#000000",
    "#111111",
    # red green and blue
    "#FF0000",
    "#00FF00",
    "#0000FF",
    # Some others
    "#ADD8E6",
    "#FFFF00",
    "#D2B48C",
]


def test_rgb_strings() -> None:
    for x in some_colors:
        assert sRGBColor.from_string(x).to_string() == x


def test_self_similar() -> None:
    for x in some_colors:
        c = sRGBColor.from_string(x).to_xyz().to_cielab()
        assert visual_diff(c, c) < 1e-14


# TODO: real tests of visual diff + conversions
